
from django.db import models
from django.core.validators import RegexValidator


class HCDTeam(models.Model):
    teamName = models.CharField(max_length=200, unique=True)
    submitPerformances = models.URLField()

    def __str__(self):
        return self.teamName


class HCDTeamLeader(models.Model):
    GENDER_CHOICES = [
        ("Male", "Male"),
        ("Female", "Female"),
        ("Other", "Other"),
    ]

    team = models.OneToOneField(
        HCDTeam,
        on_delete=models.CASCADE,
        related_name="leader"
    )
    fullName = models.CharField(max_length=100)
    contactNumber = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex=r"^[0-9]{10}$",
                message="Contact number must contain exactly 10 digits."
            )
        ]
    )
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    email = models.EmailField()
    postalCode = models.CharField(
        max_length=6,
        validators=[
            RegexValidator(
                regex=r"^[0-9]{6}$",
                message="Postal code must contain exactly 6 digits."
            )
        ]
    )
    cityName = models.CharField(max_length=100)

    def __str__(self):
        return self.fullName


class HCDMember(models.Model):
    GENDER_CHOICES = HCDTeamLeader.GENDER_CHOICES

    team = models.ForeignKey(
        HCDTeam,
        on_delete=models.CASCADE,
        related_name="members"
    )
    name = models.CharField(max_length=100)
    email = models.EmailField()
    contactNumber = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex=r"^[0-9]{10}$",
                message="Contact number must contain exactly 10 digits."
            )
        ]
    )
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    postalCode = models.CharField(
        max_length=6,
        validators=[
            RegexValidator(
                regex=r"^[0-9]{6}$",
                message="Postal code must contain exactly 6 digits."
            )
        ]
    )
    cityName = models.CharField(max_length=100)

    def __str__(self):
        return self.name
