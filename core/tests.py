from django.test import TestCase

# Change this to your real URL, or use reverse("your_url_name")
URL = "/forms/"


def build_data(members=None, team=None, leader=None):
    """Build a full valid POST payload; override pieces per test."""
    data = {
        # Team form
        "teamName": "Thunder Squad",
        "submitPerformances": "https://youtube.com/watch?v=abc123",
        # Leader form
        "fullName": "Rahul Sharma",
        "contactNumber": "9876543210",
        "gender": "Male",
        "email": "rahul@example.com",
        "postalCode": "781101",
        "cityName": "Guwahati",
    }
    if team:
        data.update(team)
    if leader:
        data.update(leader)

    if members is None:
        members = [{
            "name": "Priya Das",
            "email": "priya@example.com",
            "contactNumber": "9123456780",
            "gender": "Female",
            "postalCode": "781001",
            "cityName": "Goalpara",
        }]

    data.update({
        "members-TOTAL_FORMS": str(len(members)),
        "members-INITIAL_FORMS": "0",
        "members-MIN_NUM_FORMS": "1",
        "members-MAX_NUM_FORMS": "1000",
    })
    for i, m in enumerate(members):
        for key, value in m.items():
            data[f"members-{i}-{key}"] = value
    return data


def member(**overrides):
    base = {
        "name": "Priya Das",
        "email": "priya@example.com",
        "contactNumber": "9123456780",
        "gender": "Female",
        "postalCode": "781001",
        "cityName": "Goalpara",
    }
    base.update(overrides)
    return base


class FormTests(TestCase):

    def post(self, data):
        return self.client.post(URL, data)

    def assert_all_valid(self, response):
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].is_valid(), response.context["form"].errors)
        self.assertTrue(response.context["form2"].is_valid(), response.context["form2"].errors)
        self.assertTrue(response.context["form3"].is_valid(),
                        (response.context["form3"].errors, response.context["form3"].non_form_errors()))

    # ---------- GET ----------
    def test_get_page_loads(self):
        r = self.client.get(URL)
        self.assertEqual(r.status_code, 200)

    # ---------- VALID ----------
    def test_valid_one_member(self):
        self.assert_all_valid(self.post(build_data()))

    def test_valid_three_members(self):
        members = [
            member(name="A One", email="a@x.com", contactNumber="9000000001"),
            member(name="B Two", email="b@x.com", contactNumber="9000000002"),
            member(name="C Three", email="c@x.com", contactNumber="9000000003"),
        ]
        self.assert_all_valid(self.post(build_data(members=members)))

    # ---------- TEAM FORM ----------
    def test_invalid_url(self):
        r = self.post(build_data(team={"submitPerformances": "not-a-url"}))
        self.assertIn("submitPerformances", r.context["form"].errors)

    def test_empty_team_name(self):
        r = self.post(build_data(team={"teamName": ""}))
        self.assertIn("teamName", r.context["form"].errors)

    # ---------- LEADER FORM ----------
    def test_leader_phone_9_digits(self):
        r = self.post(build_data(leader={"contactNumber": "987654321"}))
        self.assertIn("contactNumber", r.context["form2"].errors)

    def test_leader_phone_letters(self):
        r = self.post(build_data(leader={"contactNumber": "98765abcde"}))
        self.assertIn("contactNumber", r.context["form2"].errors)

    def test_leader_postal_5_digits(self):
        r = self.post(build_data(leader={"postalCode": "78110"}))
        self.assertIn("postalCode", r.context["form2"].errors)

    def test_leader_invalid_email(self):
        r = self.post(build_data(leader={"email": "rahul@"}))
        self.assertIn("email", r.context["form2"].errors)

    def test_leader_gender_not_selected(self):
        r = self.post(build_data(leader={"gender": ""}))
        self.assertIn("gender", r.context["form2"].errors)

    def test_leader_gender_invalid_choice(self):
        r = self.post(build_data(leader={"gender": "Robot"}))
        self.assertIn("gender", r.context["form2"].errors)

    # ---------- MEMBER FIELD VALIDATION ----------
    def test_member_bad_phone(self):
        r = self.post(build_data(members=[member(contactNumber="12345")]))
        self.assertTrue(r.context["form3"].errors[0].get("contactNumber"))

    def test_member_bad_postal(self):
        r = self.post(build_data(members=[member(postalCode="abc123")]))
        self.assertTrue(r.context["form3"].errors[0].get("postalCode"))

    def test_member_bad_email(self):
        r = self.post(build_data(members=[member(email="bad-email")]))
        self.assertTrue(r.context["form3"].errors[0].get("email"))

    def test_member_missing_name(self):
        r = self.post(build_data(members=[member(name="")]))
        self.assertTrue(r.context["form3"].errors[0].get("name"))

    def test_no_members_fails_min_num(self):
        r = self.post(build_data(members=[]))
        self.assertFalse(r.context["form3"].is_valid())

    # ---------- MEMBER vs LEADER DUPLICATES ----------
    def test_member_same_name_as_leader(self):
        r = self.post(build_data(members=[member(name="  RAHUL sharma ")]))
        self.assertIn("same name as the leader", str(r.context["form3"].non_form_errors()))

    def test_member_same_email_as_leader(self):
        r = self.post(build_data(members=[member(email="RAHUL@example.com")]))
        self.assertIn("same email as the leader", str(r.context["form3"].non_form_errors()))

    def test_member_same_contact_as_leader(self):
        r = self.post(build_data(members=[member(contactNumber="9876543210")]))
        self.assertIn("same contact number as the leader", str(r.context["form3"].non_form_errors()))

    # ---------- MEMBER vs MEMBER DUPLICATES ----------
    def test_two_members_same_name(self):
        members = [
            member(name="Same Name", email="a@x.com", contactNumber="9000000001"),
            member(name="same name", email="b@x.com", contactNumber="9000000002"),
        ]
        r = self.post(build_data(members=members))
        self.assertIn("Two members cannot have the same name", str(r.context["form3"].non_form_errors()))

    def test_two_members_same_email(self):
        members = [
            member(name="A One", email="same@x.com", contactNumber="9000000001"),
            member(name="B Two", email="SAME@x.com", contactNumber="9000000002"),
        ]
        r = self.post(build_data(members=members))
        self.assertIn("same email", str(r.context["form3"].non_form_errors()))

    def test_two_members_same_contact(self):
        members = [
            member(name="A One", email="a@x.com", contactNumber="9000000001"),
            member(name="B Two", email="b@x.com", contactNumber="9000000001"),
        ]
        r = self.post(build_data(members=members))
        self.assertIn("same contact number", str(r.context["form3"].non_form_errors()))