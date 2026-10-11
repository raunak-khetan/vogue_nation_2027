
from django.test import TestCase
from .models import HCDTeam, HCDTeamLeader, HCDMember


class TeamModelTests(TestCase):
    def setUp(self):
        self.team = HCDTeam.objects.create(
            teamName="Test Team",
            submitPerformances="https://example.com/performance",
        )

    def test_team_creation(self):
        self.assertEqual(self.team.teamName, "Test Team")

    def test_leader_creation(self):
        leader = HCDTeamLeader.objects.create(
            team=self.team,
            fullName="Test Leader",
            contactNumber="9876543210",
            gender="Male",
            email="leader@example.com",
            postalCode="123456",
            cityName="Guwahati",
        )
        self.assertEqual(leader.team, self.team)

    def test_member_creation(self):
        member = HCDMember.objects.create(
            team=self.team,
            name="Test Member",
            email="member@example.com",
            contactNumber="9876543211",
            gender="Female",
            postalCode="123456",
            cityName="Guwahati",
        )
        self.assertEqual(member.team, self.team)

    def test_deleting_team_deletes_related_records(self):
        HCDTeamLeader.objects.create(
            team=self.team,
            fullName="Test Leader",
            contactNumber="9876543210",
            gender="Male",
            email="leader@example.com",
            postalCode="123456",
            cityName="Guwahati",
        )
        HCDMember.objects.create(
            team=self.team,
            name="Test Member",
            email="member@example.com",
            contactNumber="9876543211",
            gender="Female",
            postalCode="123456",
            cityName="Guwahati",
        )

        self.team.delete()

        self.assertEqual(HCDTeam.objects.count(), 0)
        self.assertEqual(HCDTeamLeader.objects.count(), 0)
        self.assertEqual(HCDMember.objects.count(), 0)
