from django.db import models
from django.core.validators import RegexValidator


# States of Dress
GENDER_CHOICES = [
    ('M', 'Male'),
    ('F', 'Female'),
    ('O', 'Others'),
]


class SOD_Team(models.Model):
    COMPETITION = 'States of Dress'

    team_name        = models.CharField(max_length=255, unique=True)
    prev_performance = models.URLField(max_length=500, null=True, blank=True)
    lead_name        = models.CharField(max_length=255)
    lead_gender      = models.CharField(max_length=1, choices=GENDER_CHOICES)
    lead_email       = models.EmailField(unique=True)
    lead_phone       = models.CharField(max_length=15)
    lead_city        = models.CharField(max_length=255, null=True, blank=True)
    lead_postal_code = models.CharField(max_length=6, null=True, blank=True)

    def __str__(self):
        return self.team_name

    class Meta:
        verbose_name        = 'States of Dress Team'
        verbose_name_plural = 'States of Dress Teams'


class SOD_Member_detail(models.Model):
    COMPETITION = 'States of Dress'

    team = models.ForeignKey(
        SOD_Team,
        related_name='members',
        on_delete=models.CASCADE
    )

    name        = models.CharField(max_length=255)
    gender      = models.CharField(max_length=1, choices=GENDER_CHOICES)
    email       = models.EmailField(unique=True)
    phone       = models.CharField(max_length=15)
    city        = models.CharField(max_length=255, null=True, blank=True)
    postal_code = models.CharField(max_length=6, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name        = 'States of Dress Member'
        verbose_name_plural = 'States of Dress Members'


# Haute Couture
class HCDTeam(models.Model):
    teamName = models.CharField(max_length=200, unique=True)
    submitPerformances = models.URLField()

    def __str__(self):
        return self.teamName

    class Meta:
        verbose_name = "HC Team"
        verbose_name_plural = "HC Teams"

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

    class Meta:
        verbose_name = "HC Team Leader"
        verbose_name_plural = "HC Team Leaders"

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
    
    class Meta:
        verbose_name = "HC Member"
        verbose_name_plural = "HC Members"


# Glamour Nova
class GN_MTeam(models.Model):
    teamName = models.CharField(max_length=200, unique=True)
    submitPerformances = models.URLField()

    def __str__(self):
        return self.teamName
    
    


class GN_MTeamLeader(models.Model):
    GENDER_CHOICES = [
        ("Male", "Male"),
        ("Female", "Female"),
        ("Other", "Other"),
    ]

    team = models.OneToOneField(
        GN_MTeam,
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


class GN_MMember(models.Model):
    GENDER_CHOICES = GN_MTeamLeader.GENDER_CHOICES

    team = models.ForeignKey(
        GN_MTeam,
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
