from django.db import models


# -- Shared choices --

GENDER_CHOICES = [
    ('M', 'Male'),
    ('F', 'Female'),
    ('O', 'Others'),
]


# -- States of Dress --

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
