from .models import HCDTeam, HCDTeamLeader, HCDMember
from .models import GN_MTeam, GN_MTeamLeader, GN_MMember
from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.forms import BaseFormSet, formset_factory


phone_validator = RegexValidator(
    regex=r"^[0-9]{10}$",
    message="Contact number must contain exactly 10 digits."
)

postal_validator = RegexValidator(
    regex=r"^[0-9]{6}$",
    message="Postal code must contain exactly 6 digits."
)

GENDER_CHOICES = [
    ("", "Select Gender"),
    ("Male", "Male"),
    ("Female", "Female"),
    ("Other", "Other"),
]


# ---------------- Dipank (HC_D) ----------------

class HC_D_form(forms.Form):
    teamName = forms.CharField(
        label="Team Name",
        max_length=200,
        widget=forms.TextInput(attrs={"placeholder": "Enter Team Name"})
    )

    submitPerformances = forms.URLField(
        label="Submit your performance(s)",
        widget=forms.URLInput(attrs={"placeholder": "Enter Link Here"})
    )


class HC_D_LeaderForm(forms.Form):
    fullName = forms.CharField(
        label="Full Name",
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "Full Name of Team Leader"})
    )

    contactNumber = forms.CharField(
        min_length=10,
        max_length=10,
        validators=[phone_validator],
        label="Contact No.",
        widget=forms.TextInput(attrs={"placeholder": "Enter 10-digit mobile number"})
    )

    gender = forms.ChoiceField(label="Gender", choices=GENDER_CHOICES)

    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={"placeholder": "Enter Email Address"})
    )

    postalCode = forms.CharField(
        min_length=6,
        max_length=6,
        validators=[postal_validator],
        label="Postal Code",
        widget=forms.TextInput(attrs={"placeholder": "Enter 6-digit postal code"})
    )

    cityName = forms.CharField(
        max_length=50,
        label="Your City",
        widget=forms.TextInput(attrs={"placeholder": "Enter Your City"})
    )


class HC_D_MemberDetails(forms.Form):
    name = forms.CharField(
        label="Full Name",
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "Enter your Full Name"})
    )

    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={"placeholder": "Enter Email Address"})
    )

    contactNumber = forms.CharField(
        min_length=10,
        max_length=10,
        validators=[phone_validator],
        label="Contact No.",
        widget=forms.TextInput(attrs={"placeholder": "Enter 10-digit mobile number"})
    )

    gender = forms.ChoiceField(label="Gender", choices=GENDER_CHOICES)

    postalCode = forms.CharField(
        min_length=6,
        max_length=6,
        validators=[postal_validator],
        label="Postal Code",
        widget=forms.TextInput(attrs={"placeholder": "Enter 6-digit postal code"})
    )

    cityName = forms.CharField(
        max_length=50,
        label="Your City",
        widget=forms.TextInput(attrs={"placeholder": "Enter Your City"})
    )


# ---------------- Mritunjay (GN_M) ----------------

class GN_M_Form(forms.Form):
    teamName = forms.CharField(
        label="Team Name",
        max_length=200,
        widget=forms.TextInput(attrs={"placeholder": "Enter Team Name"})
    )

    submitPerformances = forms.URLField(
        label="Submit your performance(s)",
        widget=forms.URLInput(attrs={"placeholder": "Enter Link Here"})
    )


class GN_M_LeaderForm(forms.Form):
    fullName = forms.CharField(
        label="Full Name",
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "Full Name of Team Leader"})
    )

    contactNumber = forms.CharField(
        min_length=10,
        max_length=10,
        validators=[phone_validator],
        label="Contact No.",
        widget=forms.TextInput(attrs={"placeholder": "Enter 10-digit mobile number"})
    )

    gender = forms.ChoiceField(label="Gender", choices=GENDER_CHOICES)

    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={"placeholder": "Enter Email Address"})
    )

    postalCode = forms.CharField(
        min_length=6,
        max_length=6,
        validators=[postal_validator],
        label="Postal Code",
        widget=forms.TextInput(attrs={"placeholder": "Enter 6-digit postal code"})
    )

    cityName = forms.CharField(
        max_length=50,
        label="Your City",
        widget=forms.TextInput(attrs={"placeholder": "Enter Your City"})
    )


class GN_M_MemberDetails(forms.Form):
    name = forms.CharField(
        label="Full Name",
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "Enter your Full Name"})
    )

    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={"placeholder": "Enter Email Address"})
    )

    contactNumber = forms.CharField(
        min_length=10,
        max_length=10,
        validators=[phone_validator],
        label="Contact No.",
        widget=forms.TextInput(attrs={"placeholder": "Enter 10-digit mobile number"})
    )

    gender = forms.ChoiceField(label="Gender", choices=GENDER_CHOICES)

    postalCode = forms.CharField(
        min_length=6,
        max_length=6,
        validators=[postal_validator],
        label="Postal Code",
        widget=forms.TextInput(attrs={"placeholder": "Enter 6-digit postal code"})
    )

    cityName = forms.CharField(
        max_length=50,
        label="Your City",
        widget=forms.TextInput(attrs={"placeholder": "Enter Your City"})
    )


# ---------------- Shared ----------------

class UniqueMemberFormSet(BaseFormSet):
    def clean(self):
        super().clean()

        if any(self.errors):
            return

        leader_name = getattr(self, "leader_name", "")
        leader_email = getattr(self, "leader_email", "")
        leader_contact = getattr(self, "leader_contact", "")

        names = set()
        emails = set()
        contacts = set()

        for form in self.forms:
            data = form.cleaned_data

            if not data:
                continue

            name = data.get("name", "").strip().casefold()
            email = data.get("email", "").strip().casefold()
            contact = data.get("contactNumber", "").strip()

            # Member details must not match the leader.
            if name == leader_name:
                raise ValidationError(
                    "A member cannot have the same name as the leader."
                )

            if email == leader_email:
                raise ValidationError(
                    "A member cannot have the same email as the leader."
                )

            if contact == leader_contact:
                raise ValidationError(
                    "A member cannot have the same contact number as the leader."
                )

            # Members must also have unique details among themselves.
            if name in names:
                raise ValidationError("Two members cannot have the same name.")

            if email in emails:
                raise ValidationError("Two members cannot have the same email.")

            if contact in contacts:
                raise ValidationError(
                    "Two members cannot have the same contact number."
                )

            names.add(name)
            emails.add(email)
            contacts.add(contact)


HC_D_MemberFormSet = formset_factory(
    HC_D_MemberDetails,
    formset=UniqueMemberFormSet,
    extra=0,
    min_num=1,
    validate_min=True
)

GN_M_MemberFormSet = formset_factory(
    GN_M_MemberDetails,
    formset=UniqueMemberFormSet,
    extra=0,
    min_num=1,
    validate_min=True
)