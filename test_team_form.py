"""
Extensive pytest suite for the HCD team registration forms + view.

Setup:
    pip install pytest pytest-django
    Put this file at core/tests/test_forms_extensive.py (add an empty __init__.py
    in core/tests/ if you use a folder) or core/test_forms_extensive.py.
    Set URL_NAME below to the name of your url pattern for the `forms` view.

Run:
    pytest -v
    pytest -k "formset"            # one area
    pytest -x                      # stop at first failure
    pytest --cov=core              # coverage (pip install pytest-cov)

Requires Django >= 3.2 for the management-form tampering tests (older versions
raise ValidationError instead of returning a form error).
"""
import pytest
from unittest import mock
from django.test import Client
from django.urls import reverse

from core.forms import HCDTeamForm, HCDTeamLeaderForm, HCDMemberForm, MemberFormSet
from core.models import HCDTeam, HCDTeamLeader, HCDMember

URL_NAME = "forms"  # <-- change to your url name


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
LEADER = {
    "fullName": "Ravi Kumar",
    "email": "ravi@example.com",
    "contactNumber": "9876543210",
    "gender": "Male",
    "postalCode": "783101",
    "cityName": "Goalpara",
}


def leader_data(prefixed=True, **kw):
    d = {**LEADER, **kw}
    return {f"leader-{k}": v for k, v in d.items()} if prefixed else d


def member_data(i, **kw):
    d = {
        "name": f"Member {i}",
        "email": f"m{i}@example.com",
        "contactNumber": f"90000000{i:02d}",
        "gender": "Female",
        "postalCode": "783101",
        "cityName": "Goalpara",
    }
    d.update(kw)
    return {f"members-{i}-{k}": v for k, v in d.items()}


def management(n, **kw):
    d = {
        "members-TOTAL_FORMS": str(n),
        "members-INITIAL_FORMS": "0",
        "members-MIN_NUM_FORMS": "1",
        "members-MAX_NUM_FORMS": "1000",
    }
    d.update(kw)
    return d


def full_post(n_members=1, **overrides):
    data = {
        "teamName": "Alpha",
        "submitPerformances": "https://example.com/video",
        **leader_data(),
        **management(n_members),
    }
    for i in range(n_members):
        data.update(member_data(i))
    data.update(overrides)
    return data


def make_formset(n=1, leader=True, **overrides):
    data = {**management(n)}
    for i in range(n):
        data.update(member_data(i))
    data.update(overrides)
    fs = MemberFormSet(data, prefix="members")
    if leader:
        fs.leader_name = LEADER["fullName"]
        fs.leader_email = LEADER["email"]
        fs.leader_contact = LEADER["contactNumber"]
    return fs


@pytest.fixture
def url():
    return "/forms/"

def post(client, url, **overrides):
    n = overrides.pop("n_members", 1)
    return client.post(url, full_post(n, **overrides))


def nothing_saved():
    return (
        HCDTeam.objects.count() == 0
        and HCDTeamLeader.objects.count() == 0
        and HCDMember.objects.count() == 0
    )


# ---------------------------------------------------------------------------
# 1. TEAM FORM
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestTeamForm:
    @pytest.mark.parametrize("name", [
        "A", "Alpha", "Team 123", "  padded  ", "Ünïcödé Team", "团队", "Team-Name_1",
        "a" * 200, "O'Brien & Sons", "Team (Final)", "123", "😀 Emoji Team",
    ])
    def test_valid_names(self, name):
        f = HCDTeamForm({"teamName": name, "submitPerformances": "https://x.com"})
        assert f.is_valid(), f.errors

    @pytest.mark.parametrize("name", ["", "   ", "\t", "\n", None, "a" * 201, "a" * 500])
    def test_invalid_names(self, name):
        data = {"submitPerformances": "https://x.com"}
        if name is not None:
            data["teamName"] = name
        f = HCDTeamForm(data)
        assert not f.is_valid()
        assert "teamName" in f.errors

    @pytest.mark.parametrize("link", [
        "https://example.com",
        "http://example.com",
        "https://example.com/path/to/video",
        "https://example.com/watch?v=abc123&t=10s",
        "https://youtu.be/abc",
        "https://drive.google.com/file/d/1abc/view",
        "https://sub.domain.example.co.in/x",
        "http://localhost:8000/x",
        "http://192.168.0.1/video",
        "https://example.com/a%20b",
        "https://example.com/#fragment",
    ])
    def test_valid_urls(self, link):
        f = HCDTeamForm({"teamName": "T", "submitPerformances": link})
        assert f.is_valid(), f.errors

    @pytest.mark.parametrize("link", [
        "", "   ", "abc", "example.com", "www.example.com", "htp:/x", "http://",
        "https://", "javascript:alert(1)", "data:text/html,<h1>x</h1>",
        "https://exa mple.com", "http//example.com", "://example.com",
        "mailto:a@b.com", "file:///etc/passwd", "https://.com",
    ])
    def test_invalid_urls(self, link):
        f = HCDTeamForm({"teamName": "T", "submitPerformances": link})
        assert not f.is_valid()
        assert "submitPerformances" in f.errors

    def test_url_over_max_length(self):
        link = "https://example.com/" + "a" * 300  # URLField default max_length=200
        f = HCDTeamForm({"teamName": "T", "submitPerformances": link})
        assert not f.is_valid()

    def test_duplicate_team_name_rejected(self):
        HCDTeam.objects.create(teamName="Alpha", submitPerformances="https://x.com")
        f = HCDTeamForm({"teamName": "Alpha", "submitPerformances": "https://y.com"})
        assert not f.is_valid()
        assert "teamName" in f.errors

    def test_duplicate_team_name_different_case_currently_allowed(self):
        """Documents current behaviour: uniqueness is case-sensitive.
        If you decide this is a bug, flip the assertion and fix the form."""
        HCDTeam.objects.create(teamName="Alpha", submitPerformances="https://x.com")
        f = HCDTeamForm({"teamName": "alpha", "submitPerformances": "https://y.com"})
        assert f.is_valid()

    def test_duplicate_url_allowed(self):
        HCDTeam.objects.create(teamName="A", submitPerformances="https://x.com")
        f = HCDTeamForm({"teamName": "B", "submitPerformances": "https://x.com"})
        assert f.is_valid()

    def test_whitespace_is_stripped(self):
        f = HCDTeamForm({"teamName": "  Alpha  ", "submitPerformances": "https://x.com"})
        assert f.is_valid()
        assert f.cleaned_data["teamName"] == "Alpha"

    def test_placeholders(self):
        f = HCDTeamForm()
        assert f.fields["teamName"].widget.attrs["placeholder"] == "Enter Team Name"
        assert f.fields["submitPerformances"].widget.attrs["placeholder"] == "Enter Link Here"

    def test_only_expected_fields(self):
        assert list(HCDTeamForm().fields) == ["teamName", "submitPerformances"]

    def test_save_persists(self):
        f = HCDTeamForm({"teamName": "Alpha", "submitPerformances": "https://x.com"})
        assert f.is_valid()
        t = f.save()
        assert HCDTeam.objects.get(pk=t.pk).teamName == "Alpha"


# ---------------------------------------------------------------------------
# 2. LEADER FORM  (and 3. MEMBER FORM, which shares the same rules)
# ---------------------------------------------------------------------------
def person_form(kind, **kw):
    if kind == "leader":
        return HCDTeamLeaderForm(leader_data(**kw) if False else
                                 {f"leader-{k}": v for k, v in {**LEADER, **kw}.items()},
                                 prefix="leader")
    d = {
        "name": "Member One", "email": "m1@example.com", "contactNumber": "9000000001",
        "gender": "Female", "postalCode": "783101", "cityName": "Goalpara",
    }
    d.update(kw)
    return HCDMemberForm(d)


NAME_FIELD = {"leader": "fullName", "member": "name"}


@pytest.mark.django_db
@pytest.mark.parametrize("kind", ["leader", "member"])
class TestPersonForms:
    def test_all_valid(self, kind):
        assert person_form(kind).is_valid()

    # ---- phone
    @pytest.mark.parametrize("phone", [
        "9876543210", "0000000000", "1234567890", "6000000000", "9999999999",
    ])
    def test_valid_phone(self, kind, phone):
        assert person_form(kind, contactNumber=phone).is_valid()

    @pytest.mark.parametrize("phone", [
        "", "1", "123456789", "12345678901", "98765abcde", "abcdefghij",
        "+919876543", "+919876543210", "98765 4321", "98765-4321", "(987)6543210",
        "9876543.10", "9876543210abc", "٩٨٧٦٥٤٣٢١٠",   # Arabic-Indic digits
        "९८७६५४३२१०",                                    # Devanagari digits
        "98765\n4321", "9876543,10", "९876543210",
        "12 34 56 78 90", "0x12345678", "1e9999999", "-123456789", "123456789.",
        "9" * 100,
    ])
    def test_invalid_phone(self, kind, phone):
        f = person_form(kind, contactNumber=phone)
        assert not f.is_valid()
        assert "contactNumber" in f.errors

    def test_phone_outer_whitespace_stripped(self, kind):
        f = person_form(kind, contactNumber=" 9876543210 ")
        assert f.is_valid()
        assert f.cleaned_data["contactNumber"] == "9876543210"

    def test_phone_trailing_newline_stripped(self, kind):
        f = person_form(kind, contactNumber="9876543210\n")
        assert f.is_valid()
        assert f.cleaned_data["contactNumber"] == "9876543210"

    def test_phone_error_message(self, kind):
        f = person_form(kind, contactNumber="123")
        assert "contactNumber" in f.errors
        msgs = " ".join(f.errors["contactNumber"])
        assert "10" in msgs

    # ---- postal code
    @pytest.mark.parametrize("pin", ["783101", "000000", "110001", "999999", "123456"])
    def test_valid_postal(self, kind, pin):
        assert person_form(kind, postalCode=pin).is_valid()

    @pytest.mark.parametrize("pin", [
        "", "1", "78310", "7831011", "78a101", "abcdef", "78 101", "78-101",
        "78.101", "+78310", "-78310", "७८३१०१", "783 101", "7831 01",
        "12345", "1234567", "      ", "00000a", "１２３４５６",  # full-width digits
    ])
    def test_invalid_postal(self, kind, pin):
        f = person_form(kind, postalCode=pin)
        assert not f.is_valid()
        assert "postalCode" in f.errors

    def test_postal_outer_whitespace_stripped(self, kind):
        f = person_form(kind, postalCode=" 783101 ")
        assert f.is_valid()
        assert f.cleaned_data["postalCode"] == "783101"

    # ---- email
    @pytest.mark.parametrize("email", [
        "a@b.co", "ravi@example.com", "first.last@example.com", "user+tag@example.com",
        "user_name@example.co.in", "u@sub.domain.example.org", "UPPER@EXAMPLE.COM",
        "a" * 64 + "@example.com", "123@456.com", "user-name@ex-ample.com",
        "o'brien@example.com", "x@localhost",
    ])
    def test_valid_email(self, kind, email):
        assert person_form(kind, email=email).is_valid(), email

    @pytest.mark.parametrize("email", [
        "", "abc", "abc@", "@example.com", "abc.com", "abc@@example.com",
        "a b@example.com", "abc@exa mple.com", "abc@.com", "abc@example..com",
        ".abc@example.com", "abc.@example.com", "a" * 250 + "@example.com",
        "abc@example.com,def@example.com", "<abc@example.com>", "abc@-example.com",
        "abc@example.com\nBcc: evil@x.com",
    ])
    def test_invalid_email(self, kind, email):
        f = person_form(kind, email=email)
        assert not f.is_valid(), email
        assert "email" in f.errors

    # ---- gender
    @pytest.mark.parametrize("g", ["Male", "Female", "Other"])
    def test_valid_gender(self, kind, g):
        assert person_form(kind, gender=g).is_valid()

    @pytest.mark.parametrize("g", [
        "", "male", "FEMALE", "other", "Robot", "M", "F", "Non-binary", "Unknown",
        " Male", "Male ", "0", "1", "<script>", "Male;Female",
    ])
    def test_invalid_gender(self, kind, g):
        f = person_form(kind, gender=g)
        # " Male" / "Male " are not stripped for ChoiceField? Django strips CharField only,
        # ChoiceField compares strings exactly, so these should fail.
        assert not f.is_valid(), repr(g)
        assert "gender" in f.errors

    # ---- name
    @pytest.mark.parametrize("name", [
        "A", "Ravi Kumar", "Ravi K. Singh", "O'Brien", "Anne-Marie", "José Álvarez",
        "राम कुमार", "李雷", "a" * 100, "Name With   Spaces", "Dr. X",
    ])
    def test_valid_names(self, kind, name):
        assert person_form(kind, **{NAME_FIELD[kind]: name}).is_valid()

    @pytest.mark.parametrize("name", ["", "   ", "\t\n", "a" * 101, "a" * 1000])
    def test_invalid_names(self, kind, name):
        f = person_form(kind, **{NAME_FIELD[kind]: name})
        assert not f.is_valid()
        assert NAME_FIELD[kind] in f.errors

    def test_name_stripped(self, kind):
        f = person_form(kind, **{NAME_FIELD[kind]: "  Ravi  "})
        assert f.is_valid()
        assert f.cleaned_data[NAME_FIELD[kind]] == "Ravi"

    # ---- city
    @pytest.mark.parametrize("city", ["A", "Goalpara", "New Delhi", "St. John's", "a" * 50, "गुवाहाटी"])
    def test_valid_city(self, kind, city):
        assert person_form(kind, cityName=city).is_valid()

    @pytest.mark.parametrize("city", ["", "   ", "a" * 51, "a" * 200])
    def test_invalid_city(self, kind, city):
        f = person_form(kind, cityName=city)
        assert not f.is_valid()
        assert "cityName" in f.errors

    # ---- missing fields
    @pytest.mark.parametrize("field", ["email", "contactNumber", "gender", "postalCode", "cityName"])
    def test_missing_field(self, kind, field):
        data = {**LEADER} if kind == "leader" else {
            "name": "M", "email": "m@example.com", "contactNumber": "9000000001",
            "gender": "Female", "postalCode": "783101", "cityName": "G"}
        data.pop(field)
        if kind == "leader":
            f = HCDTeamLeaderForm({f"leader-{k}": v for k, v in data.items()}, prefix="leader")
        else:
            f = HCDMemberForm(data)
        assert not f.is_valid()
        assert field in f.errors

    def test_completely_empty(self, kind):
        f = HCDTeamLeaderForm({}, prefix="leader") if kind == "leader" else HCDMemberForm({})
        assert not f.is_valid()
        assert len(f.errors) >= 6

    def test_multiple_errors_reported_together(self, kind):
        f = person_form(kind, contactNumber="1", postalCode="2", email="bad")
        assert not f.is_valid()
        assert {"contactNumber", "postalCode", "email"} <= set(f.errors)

    def test_team_field_not_exposed(self, kind):
        f = person_form(kind)
        assert "team" not in f.fields

    def test_unbound_form_not_valid(self, kind):
        f = HCDTeamLeaderForm(prefix="leader") if kind == "leader" else HCDMemberForm()
        assert not f.is_bound

    def test_extra_unknown_fields_ignored(self, kind):
        f = person_form(kind, hacker="1", is_admin="true")
        assert f.is_valid()
        assert "hacker" not in f.cleaned_data

    def test_xss_payload_is_stored_verbatim_but_escaped_on_render(self, kind):
        payload = "<script>alert(1)</script>"
        f = person_form(kind, cityName=payload)
        assert f.is_valid()
        assert "<script>" not in str(f["cityName"])  # widget escapes value

    def test_sql_injection_string_is_just_text(self, kind):
        f = person_form(kind, cityName="x'; DROP TABLE core_hcdteam;--")
        assert f.is_valid()


@pytest.mark.django_db
class TestLeaderOnly:
    def test_prefix_required_for_keys(self):
        f = HCDTeamLeaderForm(LEADER)  # no prefix -> nothing bound correctly
        assert not f.is_valid()

    def test_widget_placeholders(self):
        f = HCDTeamLeaderForm(prefix="leader")
        assert f.fields["contactNumber"].widget.attrs["placeholder"] == "+91 Type your number"
        assert f.fields["fullName"].widget.attrs["placeholder"] == "Enter your Full Name"

    def test_labels(self):
        f = HCDTeamLeaderForm(prefix="leader")
        assert f.fields["contactNumber"].label == "Contact No."
        assert f.fields["postalCode"].label == "Postal Code"

    def test_save_requires_team(self):
        f = HCDTeamLeaderForm(leader_data(), prefix="leader")
        assert f.is_valid()
        obj = f.save(commit=False)
        assert obj.team_id is None  # view must set team before save

    def test_same_leader_email_in_two_teams_allowed(self):
        t1 = HCDTeam.objects.create(teamName="A", submitPerformances="https://x.com")
        t2 = HCDTeam.objects.create(teamName="B", submitPerformances="https://x.com")
        HCDTeamLeader.objects.create(team=t1, **LEADER)
        HCDTeamLeader.objects.create(team=t2, **LEADER)  # documents: no cross-team uniqueness
        assert HCDTeamLeader.objects.count() == 2

    def test_one_leader_per_team_enforced_by_db(self):
        from django.db import IntegrityError, transaction
        t = HCDTeam.objects.create(teamName="A", submitPerformances="https://x.com")
        HCDTeamLeader.objects.create(team=t, **LEADER)
        with pytest.raises(IntegrityError), transaction.atomic():
            HCDTeamLeader.objects.create(team=t, **LEADER)


# ---------------------------------------------------------------------------
# 4. MEMBER FORMSET
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestFormsetStructure:
    def test_one_member_valid(self):
        assert make_formset(1).is_valid()

    @pytest.mark.parametrize("n", [2, 3, 5, 10, 25, 50, 100])
    def test_many_members_valid(self, n):
        fs = make_formset(n)
        assert fs.is_valid(), fs.errors

    def test_zero_members_invalid(self):
        fs = make_formset(0)
        assert not fs.is_valid()

    def test_min_num_is_one(self):
        assert MemberFormSet.min_num == 1

    def test_extra_zero(self):
        assert MemberFormSet.extra == 0

    def test_unbound_formset_shows_one_blank_form(self):
        fs = MemberFormSet(prefix="members")
        assert len(fs.forms) == 1

    def test_one_bad_member_invalidates_whole_set(self):
        fs = make_formset(3, **{"members-1-postalCode": "12"})
        assert not fs.is_valid()
        assert fs.errors[0] == {} and fs.errors[2] == {}
        assert "postalCode" in fs.errors[1]

    def test_every_member_bad(self):
        over = {f"members-{i}-email": "bad" for i in range(4)}
        fs = make_formset(4, **over)
        assert not fs.is_valid()
        assert all("email" in e for e in fs.errors)

    def test_blank_extra_form_is_ignored_when_not_first(self):
        """An untouched extra form beyond min_num should be allowed to be empty."""
        data = {**management(2), **member_data(0)}  # form 1 absent entirely
        fs = MemberFormSet(data, prefix="members")
        fs.leader_name = fs.leader_email = fs.leader_contact = ""
        assert fs.is_valid(), fs.errors

    def test_first_form_blank_is_invalid(self):
        data = {**management(1)}
        fs = MemberFormSet(data, prefix="members")
        assert not fs.is_valid()

    def test_cleaned_data_order_preserved(self):
        fs = make_formset(3)
        assert fs.is_valid()
        assert [f.cleaned_data["name"] for f in fs.forms] == ["Member 0", "Member 1", "Member 2"]


@pytest.mark.django_db
class TestFormsetManagementTampering:
    @pytest.mark.parametrize("value", ["abc", "", "-1", "1.5", "NaN", "1e3", " "])
    def test_bad_total_forms(self, value):
        fs = make_formset(1, **{"members-TOTAL_FORMS": value})
        assert not fs.is_valid()

    def test_missing_total_forms(self):
        data = full_post(1)
        data.pop("members-TOTAL_FORMS")
        fs = MemberFormSet(data, prefix="members")
        assert not fs.is_valid()

    def test_missing_initial_forms(self):
        data = full_post(1)
        data.pop("members-INITIAL_FORMS")
        fs = MemberFormSet(data, prefix="members")
        assert not fs.is_valid()

    def test_total_forms_larger_than_data(self):
        fs = make_formset(1, **{"members-TOTAL_FORMS": "3"})
        # Forms 1 and 2 are empty extras and should be ignored; form 0 is valid.
        assert fs.is_valid(), fs.errors

    def test_total_forms_smaller_than_data(self):
        data = {**management(1)}
        for i in range(3):
            data.update(member_data(i))
        fs = MemberFormSet(data, prefix="members")
        fs.leader_name = fs.leader_email = fs.leader_contact = ""
        assert fs.is_valid()
        assert len(fs.forms) == 1  # extra data ignored

    def test_huge_total_forms_does_not_crash(self):
        fs = make_formset(1, **{"members-TOTAL_FORMS": "100000"})
        fs.is_valid()  # must not hang or raise unexpectedly

    def test_wrong_prefix_data_ignored(self):
        data = {k.replace("members-", "people-"): v for k, v in full_post(1).items()}
        fs = MemberFormSet(data, prefix="members")
        assert not fs.is_valid()


# ---- uniqueness logic --------------------------------------------------------
@pytest.mark.django_db
class TestFormsetUniqueness:
    def test_all_unique_ok(self):
        assert make_formset(5).is_valid()

    # member vs leader
    @pytest.mark.parametrize("name", [
        "Ravi Kumar", "ravi kumar", "RAVI KUMAR", "rAvI kUmAr", "  Ravi Kumar  ",
        "Ravi Kumar\t",
    ])
    def test_member_name_equals_leader(self, name):
        fs = make_formset(1, **{"members-0-name": name})
        assert not fs.is_valid()
        assert "Duplicate name" in str(fs.non_form_errors())

    @pytest.mark.parametrize("email", [
        "ravi@example.com", "RAVI@EXAMPLE.COM", "Ravi@Example.Com", " ravi@example.com ",
    ])
    def test_member_email_equals_leader(self, email):
        fs = make_formset(1, **{"members-0-email": email})
        assert not fs.is_valid()
        assert "Duplicate email" in str(fs.non_form_errors())

    def test_member_contact_equals_leader(self):
        fs = make_formset(1, **{"members-0-contactNumber": "9876543210"})
        assert not fs.is_valid()
        assert "Duplicate contact" in str(fs.non_form_errors())

    def test_member_contact_with_spaces_equals_leader(self):
        fs = make_formset(1, **{"members-0-contactNumber": " 9876543210 "})
        assert not fs.is_valid()

    # member vs member (try every pairing position)
    @pytest.mark.parametrize("a,b", [(0, 1), (0, 2), (1, 2), (0, 4), (3, 4)])
    @pytest.mark.parametrize("field,value,needle", [
        ("name", "Same Person", "Duplicate name"),
        ("name", "SAME PERSON", "Duplicate name"),
        ("email", "same@example.com", "Duplicate email"),
        ("email", "SAME@example.com", "Duplicate email"),
        ("contactNumber", "9111111111", "Duplicate contact"),
    ])
    def test_member_vs_member(self, a, b, field, value, needle):
        over = {f"members-{a}-{field}": value, f"members-{b}-{field}": value}
        if field == "name":
            over[f"members-{b}-{field}"] = value.swapcase()
        fs = make_formset(5, **over)
        assert not fs.is_valid()
        assert needle in str(fs.non_form_errors())

    # non-unique fields must be allowed to repeat
    @pytest.mark.parametrize("field,value", [
        ("postalCode", "783101"), ("cityName", "Goalpara"), ("gender", "Male"),
    ])
    def test_non_unique_fields_may_repeat(self, field, value):
        over = {f"members-{i}-{field}": value for i in range(4)}
        assert make_formset(4, **over).is_valid()

    def test_member_postal_equals_leader_postal_ok(self):
        fs = make_formset(1, **{"members-0-postalCode": LEADER["postalCode"]})
        assert fs.is_valid()

    def test_member_city_equals_leader_city_ok(self):
        fs = make_formset(1, **{"members-0-cityName": LEADER["cityName"]})
        assert fs.is_valid()

    def test_similar_but_different_name_ok(self):
        fs = make_formset(1, **{"members-0-name": "Ravi Kumar Jr"})
        assert fs.is_valid()

    def test_similar_but_different_email_ok(self):
        fs = make_formset(1, **{"members-0-email": "ravi2@example.com"})
        assert fs.is_valid()

    def test_contact_off_by_one_digit_ok(self):
        fs = make_formset(1, **{"members-0-contactNumber": "9876543211"})
        assert fs.is_valid()

    def test_inner_whitespace_in_name_not_collapsed(self):
        """Documents behaviour: 'Ravi  Kumar' (two spaces) is NOT treated as a duplicate."""
        fs = make_formset(1, **{"members-0-name": "Ravi  Kumar"})
        assert fs.is_valid()

    def test_unicode_casefold_equivalence(self):
        fs = make_formset(2, **{"members-0-name": "Straße", "members-1-name": "STRASSE"})
        assert not fs.is_valid()  # casefold maps ß -> ss

    def test_duplicates_skipped_when_leader_info_missing(self):
        """If leader invalid the view never sets leader_* so only member-vs-member is checked."""
        fs = make_formset(1, leader=False, **{"members-0-email": LEADER["email"]})
        assert fs.is_valid()

    def test_all_three_duplicates_reports_first_found(self):
        fs = make_formset(1, **{
            "members-0-name": "Ravi Kumar",
            "members-0-email": "ravi@example.com",
            "members-0-contactNumber": "9876543210",
        })
        assert not fs.is_valid()
        assert len(fs.non_form_errors()) == 1  # clean() raises on first hit

    def test_field_error_short_circuits_uniqueness(self):
        fs = make_formset(2, **{
            "members-0-postalCode": "12",
            "members-0-email": "same@example.com",
            "members-1-email": "same@example.com",
        })
        assert not fs.is_valid()
        assert not fs.non_form_errors()  # only field errors shown

    def test_error_message_contains_offending_value(self):
        fs = make_formset(2, **{"members-0-email": "x@y.com", "members-1-email": "x@y.com"})
        fs.is_valid()
        assert "x@y.com" in str(fs.non_form_errors())


# ---------------------------------------------------------------------------
# 5. VIEW / INTEGRATION
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestViewGet:
    def test_get_ok(self, client, url):
        r = client.get(url)
        assert r.status_code == 200

    def test_get_template(self, client, url):
        r = client.get(url)
        assert "core/forms.html" in [t.name for t in r.templates]

    def test_get_context_keys(self, client, url):
        r = client.get(url)
        assert {"form", "form2", "form3"} <= set(r.context.keys())

    def test_get_forms_unbound(self, client, url):
        r = client.get(url)
        assert not r.context["form"].is_bound
        assert not r.context["form2"].is_bound
        assert not r.context["form3"].is_bound

    def test_get_no_success_flag(self, client, url):
        r = client.get(url)
        assert not r.context.get("success")

    def test_get_creates_nothing(self, client, url):
        client.get(url)
        assert nothing_saved()

    def test_get_with_query_string_ignored(self, client, url):
        r = client.get(url, {"teamName": "Alpha"})
        assert r.status_code == 200
        assert nothing_saved()

    @pytest.mark.parametrize("method", ["put", "delete", "patch", "options"])
    def test_other_methods_show_blank_form(self, client, url, method):
        r = getattr(client, method)(url)
        assert r.status_code == 200
        assert nothing_saved()

    def test_head(self, client, url):
        assert client.head(url).status_code == 200


@pytest.mark.django_db
class TestViewPostSuccess:
    def test_status_200(self, client, url):
        assert post(client, url).status_code == 200

    def test_success_flag(self, client, url):
        assert post(client, url).context["success"] is True

    def test_form_reset_after_success(self, client, url):
        r = post(client, url)
        assert not r.context["form"].is_bound
        assert not r.context["form2"].is_bound
        assert not r.context["form3"].is_bound

    def test_counts(self, client, url):
        post(client, url, n_members=3)
        assert HCDTeam.objects.count() == 1
        assert HCDTeamLeader.objects.count() == 1
        assert HCDMember.objects.count() == 3

    @pytest.mark.parametrize("n", [1, 2, 7, 20, 60])
    def test_n_members_saved(self, client, url, n):
        post(client, url, n_members=n)
        assert HCDMember.objects.count() == n

    def test_team_fields_saved(self, client, url):
        post(client, url)
        t = HCDTeam.objects.get()
        assert t.teamName == "Alpha"
        assert t.submitPerformances == "https://example.com/video"

    def test_leader_fields_saved(self, client, url):
        post(client, url)
        l = HCDTeamLeader.objects.get()
        for k, v in LEADER.items():
            assert getattr(l, k) == v

    def test_leader_linked_to_team(self, client, url):
        post(client, url)
        assert HCDTeamLeader.objects.get().team == HCDTeam.objects.get()
        assert HCDTeam.objects.get().leader.fullName == "Ravi Kumar"

    def test_members_linked_to_team(self, client, url):
        post(client, url, n_members=3)
        t = HCDTeam.objects.get()
        assert t.members.count() == 3
        assert {m.team_id for m in HCDMember.objects.all()} == {t.id}

    def test_member_fields_saved(self, client, url):
        post(client, url, n_members=2)
        m = HCDMember.objects.get(name="Member 1")
        assert m.email == "m1@example.com"
        assert m.contactNumber == "9000000001"
        assert m.gender == "Female"
        assert m.postalCode == "783101"
        assert m.cityName == "Goalpara"

    def test_whitespace_stripped_before_saving(self, client, url):
        post(client, url, **{"teamName": "  Alpha  ", "leader-fullName": "  Ravi Kumar  ",
                             "members-0-name": "  Member 0  "})
        assert HCDTeam.objects.get().teamName == "Alpha"
        assert HCDTeamLeader.objects.get().fullName == "Ravi Kumar"
        assert HCDMember.objects.get().name == "Member 0"

    def test_unicode_data_saved(self, client, url):
        post(client, url, **{"teamName": "团队 Ünï", "leader-cityName": "गुवाहाटी"})
        assert HCDTeam.objects.get().teamName == "团队 Ünï"
        assert HCDTeamLeader.objects.get().cityName == "गुवाहाटी"

    def test_two_different_teams_can_register(self, client, url):
        post(client, url)
        post(client, url, **{
            "teamName": "Beta",
            "leader-email": "b@example.com", "leader-contactNumber": "9111111111",
            "leader-fullName": "Other Leader",
            "members-0-name": "Other Member", "members-0-email": "om@example.com",
            "members-0-contactNumber": "9222222222",
        })
        assert HCDTeam.objects.count() == 2
        assert HCDMember.objects.count() == 2

    def test_same_person_in_two_teams_currently_allowed(self, client, url):
        """Documents: no cross-team uniqueness. Flip if business rules say otherwise."""
        post(client, url)
        post(client, url, **{"teamName": "Beta"})
        assert HCDTeam.objects.count() == 2
        assert HCDTeamLeader.objects.count() == 2

    def test_non_model_post_keys_ignored(self, client, url):
        post(client, url, **{"is_admin": "1", "team": "999", "leader-team": "999",
                             "members-0-team": "999"})
        t = HCDTeam.objects.get()
        assert HCDTeamLeader.objects.get().team_id == t.id
        assert HCDMember.objects.get().team_id == t.id

    def test_xss_in_team_name_stored_verbatim(self, client, url):
        post(client, url, teamName="<b>x</b>")
        assert HCDTeam.objects.get().teamName == "<b>x</b>"

    def test_sqli_string_stored_verbatim(self, client, url):
        post(client, url, teamName="'; DROP TABLE core_hcdteam; --")
        assert HCDTeam.objects.count() == 1


@pytest.mark.django_db
class TestViewPostFailures:
    # Each tuple: description, overrides. Nothing should be saved for any of these.
    BAD_POSTS = [
        # team
        ("empty team name", {"teamName": ""}),
        ("blank team name", {"teamName": "   "}),
        ("long team name", {"teamName": "a" * 201}),
        ("bad url", {"submitPerformances": "nope"}),
        ("empty url", {"submitPerformances": ""}),
        ("js url", {"submitPerformances": "javascript:alert(1)"}),
        # leader
        ("leader empty name", {"leader-fullName": ""}),
        ("leader long name", {"leader-fullName": "a" * 101}),
        ("leader bad email", {"leader-email": "bad"}),
        ("leader short phone", {"leader-contactNumber": "123"}),
        ("leader letters phone", {"leader-contactNumber": "98765abcde"}),
        ("leader bad gender", {"leader-gender": "Robot"}),
        ("leader empty gender", {"leader-gender": ""}),
        ("leader short pin", {"leader-postalCode": "123"}),
        ("leader letter pin", {"leader-postalCode": "12a456"}),
        ("leader empty city", {"leader-cityName": ""}),
        ("leader long city", {"leader-cityName": "c" * 51}),
        # member
        ("member empty name", {"members-0-name": ""}),
        ("member long name", {"members-0-name": "a" * 101}),
        ("member bad email", {"members-0-email": "bad"}),
        ("member short phone", {"members-0-contactNumber": "123"}),
        ("member bad gender", {"members-0-gender": "Robot"}),
        ("member bad pin", {"members-0-postalCode": "12"}),
        ("member empty city", {"members-0-cityName": ""}),
        # duplicates
        ("member = leader name", {"members-0-name": "Ravi Kumar"}),
        ("member = leader name (case)", {"members-0-name": "ravi kumar"}),
        ("member = leader email", {"members-0-email": "ravi@example.com"}),
        ("member = leader email (case)", {"members-0-email": "RAVI@EXAMPLE.COM"}),
        ("member = leader phone", {"members-0-contactNumber": "9876543210"}),
        # management form
        ("zero members", {"members-TOTAL_FORMS": "0"}),
        ("garbage total forms", {"members-TOTAL_FORMS": "abc"}),
        ("negative total forms", {"members-TOTAL_FORMS": "-5"}),
    ]

    @pytest.mark.parametrize("desc,over", BAD_POSTS, ids=[d for d, _ in BAD_POSTS])
    def test_bad_post_saves_nothing(self, client, url, desc, over):
        r = post(client, url, **over)
        assert r.status_code == 200
        assert nothing_saved()
        assert not r.context.get("success")

    @pytest.mark.parametrize("desc,over", BAD_POSTS, ids=[d for d, _ in BAD_POSTS])
    def test_bad_post_rerenders_bound_forms(self, client, url, desc, over):
        r = post(client, url, **over)
        assert r.context["form"].is_bound
        assert r.context["form2"].is_bound
        assert r.context["form3"].is_bound

    def test_empty_post(self, client, url):
        r = client.post(url, {})
        assert r.status_code == 200
        assert nothing_saved()

    def test_missing_leader_block(self, client, url):
        data = full_post()
        data = {k: v for k, v in data.items() if not k.startswith("leader-")}
        client.post(url, data)
        assert nothing_saved()

    def test_missing_team_block(self, client, url):
        data = full_post()
        data.pop("teamName")
        data.pop("submitPerformances")
        client.post(url, data)
        assert nothing_saved()

    def test_missing_members_block(self, client, url):
        data = {k: v for k, v in full_post().items() if not k.startswith("members-")}
        client.post(url, data)
        assert nothing_saved()

    def test_one_bad_member_among_many_saves_nothing(self, client, url):
        client.post(url, full_post(10, **{"members-7-postalCode": "x"}))
        assert nothing_saved()

    def test_duplicate_between_members_saves_nothing(self, client, url):
        client.post(url, full_post(3, **{"members-2-email": "m0@example.com"}))
        assert nothing_saved()

    def test_duplicate_team_name_saves_nothing_new(self, client, url):
        post(client, url)
        before = (HCDTeam.objects.count(), HCDMember.objects.count())
        r = post(client, url)
        assert not r.context.get("success")
        assert (HCDTeam.objects.count(), HCDMember.objects.count()) == before

    def test_refresh_after_success_does_not_double_save(self, client, url):
        post(client, url)
        post(client, url)  # browser re-POST on refresh
        assert HCDTeam.objects.count() == 1
        assert HCDTeamLeader.objects.count() == 1
        assert HCDMember.objects.count() == 1

    def test_errors_visible_in_response(self, client, url):
        r = post(client, url, **{"leader-contactNumber": "123"})
        assert "contactNumber" in r.context["form2"].errors

    def test_duplicate_error_in_non_form_errors(self, client, url):
        r = post(client, url, **{"members-0-email": "ravi@example.com"})
        assert "Duplicate email" in str(r.context["form3"].non_form_errors())

    def test_entered_values_preserved_on_error(self, client, url):
        r = post(client, url, **{"leader-contactNumber": "123"})
        html = r.content.decode()
        assert "Alpha" in html          # team name still in the page
        assert "Ravi Kumar" in html     # leader name still in the page

    def test_xss_escaped_when_rerendered(self, client, url):
        payload = "<script>alert(1)</script>"
        r = post(client, url, **{"teamName": payload, "leader-contactNumber": "123"})
        assert payload not in r.content.decode()

    def test_leader_invalid_skips_duplicate_check(self, client, url):
        """Documents: with an invalid leader the formset has no leader_* attrs,
        so no duplicate error shows (but nothing is saved anyway)."""
        r = post(client, url, **{"leader-postalCode": "1", "members-0-email": "ravi@example.com"})
        assert nothing_saved()
        assert not r.context["form3"].non_form_errors()

    def test_leader_error_and_member_error_both_reported(self, client, url):
        r = post(client, url, **{"leader-email": "bad", "members-0-email": "bad"})
        assert "email" in r.context["form2"].errors
        assert "email" in r.context["form3"].errors[0]

    def test_all_three_blocks_invalid_all_reported(self, client, url):
        r = post(client, url, **{"teamName": "", "leader-email": "bad", "members-0-email": "bad"})
        assert r.context["form"].errors
        assert r.context["form2"].errors
        assert r.context["form3"].errors


@pytest.mark.django_db
class TestViewAtomicity:
    def test_member_save_failure_rolls_back_everything(self, client, url):
        with mock.patch.object(HCDMember, "save", side_effect=RuntimeError("boom")):
            with pytest.raises(RuntimeError):
                post(client, url, n_members=3)
        assert nothing_saved()

    def test_leader_save_failure_rolls_back_team(self, client, url):
        with mock.patch.object(HCDTeamLeader, "save", side_effect=RuntimeError("boom")):
            with pytest.raises(RuntimeError):
                post(client, url)
        assert nothing_saved()

    def test_failure_on_third_member_rolls_back_first_two(self, client, url):
        real_save = HCDMember.save
        calls = {"n": 0}

        def flaky(self, *a, **kw):
            calls["n"] += 1
            if calls["n"] == 3:
                raise RuntimeError("third fails")
            return real_save(self, *a, **kw)

        with mock.patch.object(HCDMember, "save", flaky):
            with pytest.raises(RuntimeError):
                post(client, url, n_members=5)
        assert nothing_saved()

    def test_team_save_failure_saves_nothing(self, client, url):
        with mock.patch.object(HCDTeam, "save", side_effect=RuntimeError("boom")):
            with pytest.raises(RuntimeError):
                post(client, url)
        assert nothing_saved()

    def test_can_register_after_failed_attempt(self, client, url):
        with mock.patch.object(HCDMember, "save", side_effect=RuntimeError("boom")):
            with pytest.raises(RuntimeError):
                post(client, url)
        r = post(client, url)
        assert r.context["success"] is True
        assert HCDTeam.objects.count() == 1


@pytest.mark.django_db
class TestViewSecurityAndHttp:
    def test_csrf_enforced(self, url):
        c = Client(enforce_csrf_checks=True)
        r = c.post(url, full_post())
        assert r.status_code == 403
        assert nothing_saved()

    def test_csrf_token_rendered_in_form(self, client, url):
        assert "csrfmiddlewaretoken" in client.get(url).content.decode()

    def test_csrf_accepted_with_token(self, url):
        c = Client(enforce_csrf_checks=True)
        c.get(url)
        token = c.cookies["csrftoken"].value
        r = c.post(url, {**full_post(), "csrfmiddlewaretoken": token})
        assert r.status_code == 200
        assert HCDTeam.objects.count() == 1

    def test_mass_assignment_team_id_ignored(self, client, url):
        other = HCDTeam.objects.create(teamName="Other", submitPerformances="https://x.com")
        post(client, url, **{"members-0-team": str(other.id), "leader-team": str(other.id)})
        assert other.members.count() == 0
        assert not HCDTeamLeader.objects.filter(team=other).exists()

    def test_huge_payload_rejected_or_handled(self, client, url):
        r = post(client, url, **{"teamName": "a" * 1_000_000})
        assert r.status_code in (200, 400, 413)
        assert nothing_saved()

    def test_null_byte_in_input(self, client, url):
        r = post(client, url, **{"teamName": "Al\x00pha"})
        assert r.status_code == 200
        assert nothing_saved()  # Django's ProhibitNullCharactersValidator

    def test_trailing_slash_url(self, client, url):
        assert client.get(url).status_code == 200

    def test_response_content_type_html(self, client, url):
        assert "text/html" in client.get(url)["Content-Type"]

    def test_concurrent_style_double_post_same_team(self, client, url):
        """Second submit with same team name must fail cleanly (no 500)."""
        post(client, url)
        r = post(client, url, **{"leader-email": "other@example.com",
                                  "leader-contactNumber": "9222222222",
                                  "members-0-email": "z@example.com",
                                  "members-0-contactNumber": "9333333333"})
        assert r.status_code == 200
        assert HCDTeam.objects.count() == 1


# ---------------------------------------------------------------------------
# 6. MODEL SANITY
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestModels:
    def test_team_str(self):
        assert str(HCDTeam(teamName="Alpha")) == "Alpha"

    def test_leader_str(self):
        assert str(HCDTeamLeader(fullName="Ravi")) == "Ravi"

    def test_member_str(self):
        assert str(HCDMember(name="Meena")) == "Meena"

    def test_team_name_unique_db_level(self):
        from django.db import IntegrityError, transaction
        HCDTeam.objects.create(teamName="A", submitPerformances="https://x.com")
        with pytest.raises(IntegrityError), transaction.atomic():
            HCDTeam.objects.create(teamName="A", submitPerformances="https://y.com")

    def test_cascade_delete_removes_leader_and_members(self, client, url):
        post(client, url, n_members=3)
        HCDTeam.objects.get().delete()
        assert nothing_saved()

    def test_related_names(self):
        t = HCDTeam.objects.create(teamName="A", submitPerformances="https://x.com")
        HCDTeamLeader.objects.create(team=t, **LEADER)
        HCDMember.objects.create(team=t, name="M", email="m@x.com", contactNumber="9000000001",
                                 gender="Male", postalCode="783101", cityName="G")
        assert t.leader.fullName == "Ravi Kumar"
        assert t.members.count() == 1

    def test_model_does_not_enforce_form_validators(self):
        """Documents: model-level create() skips RegexValidator; only forms enforce it.
        Consider adding validators to the model fields too."""
        t = HCDTeam.objects.create(teamName="A", submitPerformances="https://x.com")
        m = HCDMember.objects.create(team=t, name="M", email="bad", contactNumber="abc",
                                     gender="Robot", postalCode="x", cityName="G")
        assert m.pk is not None