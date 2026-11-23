from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.forms import BaseFormSet, formset_factory

from .models import SOD_Team, SOD_Member_detail
from .models import HCDTeam, HCDTeamLeader, HCDMember
from .models import GN_MTeam, GN_MTeamLeader, GN_MMember


# States of Dress
sod_phone_validator = RegexValidator(
    regex=r'^(?:\+91[\s-]?)?[6-9]\d{9}$',
    message='Enter a valid 10-digit Indian mobile number (e.g. 9876543210 or +91 9876543210).'
)


class SOD_TeamForm(forms.ModelForm):
    class Meta:
        model = SOD_Team
        fields = [
            'team_name',
            'prev_performance',
            'lead_name',
            'lead_gender',
            'lead_email',
            'lead_phone',
            'lead_city',
            'lead_postal_code',
        ]
        widgets = {
            'team_name': forms.TextInput(attrs={'placeholder': 'Enter Team Name'}),
            'prev_performance': forms.URLInput(attrs={'placeholder': 'https://...'}),
            'lead_name': forms.TextInput(attrs={'placeholder': 'Full Name of Team Leader'}),
            'lead_gender': forms.Select(),
            'lead_email': forms.EmailInput(attrs={'placeholder': 'Team Leader Email'}),
            'lead_phone': forms.TextInput(attrs={'placeholder': '+91 9876543210'}),
            'lead_city': forms.TextInput(attrs={'placeholder': 'Type Here'}),
            'lead_postal_code': forms.TextInput(attrs={'placeholder': '6-digit PIN code', 'maxlength': '6'}),
        }

    def clean_lead_phone(self):
        phone = self.cleaned_data.get('lead_phone', '')
        if phone:
            phone = phone.strip()
            sod_phone_validator(phone)
        return phone

    def clean_lead_postal_code(self):
        code = (self.cleaned_data.get('lead_postal_code') or '').strip()
        if code:
            if not code.isdigit() or len(code) != 6:
                raise forms.ValidationError('Enter a valid 6-digit postal code.')
        return code or None

    def clean_team_name(self):
        name = self.cleaned_data.get('team_name', '')
        if name and len(name.strip()) < 3:
            raise forms.ValidationError('Team name must be at least 3 characters.')
        return name.strip()

    def clean_lead_email(self):
        email = self.cleaned_data.get('lead_email', '')
        return email.strip().lower() if email else email


class SOD_MemberDetailForm(forms.ModelForm):
    class Meta:
        model = SOD_Member_detail
        fields = [
            'name',
            'email',
            'phone',
            'city',
            'gender',
            'postal_code',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Type Here'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Type Here'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Type Here'}),
            'city': forms.TextInput(attrs={'placeholder': 'Type Here'}),
            'gender': forms.Select(),
            'postal_code': forms.TextInput(attrs={'placeholder': '6-digit PIN code', 'maxlength': '6'}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        if phone:
            phone = phone.strip()
            sod_phone_validator(phone)
        return phone

    def clean_email(self):
        email = self.cleaned_data.get('email', '')
        return email.strip().lower() if email else email

    def clean_postal_code(self):
        code = (self.cleaned_data.get('postal_code') or '').strip()
        if code:
            if not code.isdigit() or len(code) != 6:
                raise forms.ValidationError('Enter a valid 6-digit postal code.')
        return code or None


class BaseSODMemberFormSet(forms.BaseFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return

        emails = set()
        for form in self.forms:
            if not form.cleaned_data or form.cleaned_data.get('DELETE', False):
                continue
            email = (form.cleaned_data.get('email') or '').strip().lower()
            if email:
                if email in emails:
                    form.add_error('email', 'Each team member must have a unique email address.')
                else:
                    emails.add(email)


# Haute Couture & Glamour Nova
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


# Haute Couture forms
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


# Glamour Nova forms
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


# Unique member validation for HCD and GNM
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

            if name == leader_name:
                raise ValidationError("A member cannot have the same name as the leader.")

            if email == leader_email:
                raise ValidationError("A member cannot have the same email as the leader.")

            if contact == leader_contact:
                raise ValidationError("A member cannot have the same contact number as the leader.")

            if name in names:
                raise ValidationError("Two members cannot have the same name.")

            if email in emails:
                raise ValidationError("Two members cannot have the same email.")

            if contact in contacts:
                raise ValidationError("Two members cannot have the same contact number.")

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
