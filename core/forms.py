from django import forms
from django.core.validators import RegexValidator

from .models import SOD_Team, SOD_Member_detail


# -- Shared validators --

sod_phone_validator = RegexValidator(
    regex=r'^(?:\+91[\s-]?)?[6-9]\d{9}$',
    message='Enter a valid 10-digit Indian mobile number (e.g. 9876543210 or +91 9876543210).'
)


# -- States of Dress --

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
            'team_name': forms.TextInput(attrs={
                'placeholder': 'Enter Team Name',
            }),
            'prev_performance': forms.URLInput(attrs={
                'placeholder': 'https://...',
            }),
            'lead_name': forms.TextInput(attrs={
                'placeholder': 'Full Name of Team Leader',
            }),
            'lead_gender': forms.Select(),
            'lead_email': forms.EmailInput(attrs={
                'placeholder': 'Team Leader Email',
            }),
            'lead_phone': forms.TextInput(attrs={
                'placeholder': '+91 9876543210',
            }),
            'lead_city': forms.TextInput(attrs={
                'placeholder': 'Type Here',
            }),
            'lead_postal_code': forms.TextInput(attrs={
                'placeholder': '6-digit PIN code',
                'maxlength': '6',
            }),
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
            'name': forms.TextInput(attrs={
                'placeholder': 'Type Here',
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Type Here',
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': 'Type Here',
            }),
            'city': forms.TextInput(attrs={
                'placeholder': 'Type Here',
            }),
            'gender': forms.Select(),
            'postal_code': forms.TextInput(attrs={
                'placeholder': '6-digit PIN code',
                'maxlength': '6',
            }),
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
    """Custom formset that validates uniqueness across member forms."""
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
