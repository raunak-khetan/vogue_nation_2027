import logging

from django.contrib import messages
from django.db import IntegrityError, transaction
from django.forms import formset_factory
from django.http import HttpResponse
from django.shortcuts import redirect, render

from .forms import (
    BaseSODMemberFormSet,
    SOD_MemberDetailForm,
    SOD_TeamForm,
    HC_D_form,
    HC_D_LeaderForm,
    HC_D_MemberFormSet,
    GN_M_Form,
    GN_M_LeaderForm,
    GN_M_MemberFormSet,
)

logger = logging.getLogger(__name__)


# States of Dress
def _has_registered(email, team_name):
    from .models import SOD_Member_detail, SOD_Team

    email_clean = (email or "").strip()
    email_taken = (
        SOD_Team.objects.filter(lead_email__iexact=email_clean).exists()
        or SOD_Member_detail.objects.filter(email__iexact=email_clean).exists()
    )
    team_taken  = SOD_Team.objects.filter(team_name__iexact=team_name).exists()
    return email_taken, team_taken


@transaction.atomic
def _save_sod_registration(team_form, member_formset):
    """All-or-nothing save for a SOD team and its members."""
    team = team_form.save()

    for member_form in member_formset:
        cd = member_form.cleaned_data
        if not cd or cd.get("DELETE", False):
            continue
        member = member_form.save(commit=False)
        member.team = team
        member.save()

    return team


def sod_section(request):
    SOD_MemberFormSet = formset_factory(
        SOD_MemberDetailForm,
        formset=BaseSODMemberFormSet,
        extra=0,
        min_num=1,
        validate_min=True,
        can_delete=False,
    )

    is_submitted = (
        request.method == "POST" and "sod_members-TOTAL_FORMS" in request.POST
    )

    if not is_submitted:
        InitialFormSet = formset_factory(
            SOD_MemberDetailForm,
            formset=BaseSODMemberFormSet,
            extra=1,
            min_num=1,
            validate_min=True,
            can_delete=False,
        )
        context = {
            "team_form": SOD_TeamForm(),
            "member_formset": InitialFormSet(prefix="sod_members"),
        }
        return context, False

    team_form      = SOD_TeamForm(request.POST)
    member_formset = SOD_MemberFormSet(request.POST, prefix="sod_members")

    for form in member_formset.forms:
        form.empty_permitted = False

    team_valid   = team_form.is_valid()
    member_valid = member_formset.is_valid()
    is_valid     = team_valid and member_valid

    if is_valid:
        from .models import SOD_Team

        email_val = team_form.cleaned_data.get("lead_email", "")
        team_name = team_form.cleaned_data.get("team_name", "")
        email_taken, team_taken = _has_registered(email_val, team_name)

        if email_taken:
            team_form.add_error(
                "lead_email",
                "This email is already registered for States of Dress.",
            )
        if team_taken:
            team_form.add_error(
                "team_name",
                "A team with this name is already registered.",
            )

        has_duplicate = email_taken or team_taken

        lead_email = (email_val or "").strip().lower()
        for member_form in member_formset.forms:
            if not member_form.cleaned_data:
                continue
            m_email = (member_form.cleaned_data.get("email") or "").strip().lower()
            if m_email and m_email == lead_email:
                member_form.add_error(
                    "email",
                    "Team member email cannot be the same as the team leader's email.",
                )
                has_duplicate = True
            elif m_email and SOD_Team.objects.filter(lead_email__iexact=m_email).exists():
                member_form.add_error(
                    "email",
                    "This email is already registered as a team leader.",
                )
                has_duplicate = True

        is_valid = not has_duplicate

    context = {
        "team_form": team_form,
        "member_formset": member_formset,
    }

    if not is_valid:
        return context, False

    try:
        _save_sod_registration(team_form, member_formset)
    except IntegrityError:
        logger.exception("IntegrityError during SOD registration.")
        messages.error(
            request,
            "A database conflict occurred. Please review your details.",
        )
        return context, False
    except Exception:
        logger.exception("Unexpected error during SOD registration.")
        messages.error(
            request,
            "Something went wrong on our end. Please try again in a moment.",
        )
        return context, False

    messages.success(request, "Registration successful! You're all set for States of Dress.")
    FreshFormSet = formset_factory(
        SOD_MemberDetailForm,
        formset=BaseSODMemberFormSet,
        extra=1,
        min_num=1,
        validate_min=True,
        can_delete=False,
    )
    fresh_context = {
        "team_form": SOD_TeamForm(),
        "member_formset": FreshFormSet(prefix="sod_members"),
        "registration_success": True,
    }
    return fresh_context, True


# Haute Couture
def hc_d_section(request):
    valid = False

    if request.method == "POST":
        form = HC_D_form(request.POST, prefix="hcd")
        leader_form = HC_D_LeaderForm(request.POST, prefix="hcd_leader")
        member_form = HC_D_MemberFormSet(
            request.POST,
            prefix="hcd_members"
        )

        valid1 = form.is_valid()
        valid2 = leader_form.is_valid()

        if valid2:
            member_form.leader_name = (
                leader_form.cleaned_data["fullName"].strip().casefold()
            )
            member_form.leader_email = (
                leader_form.cleaned_data["email"].strip().casefold()
            )
            member_form.leader_contact = (
                leader_form.cleaned_data["contactNumber"].strip()
            )

        valid3 = member_form.is_valid()

        if valid1 and valid2 and valid3:
            valid = True

    else:
        form = HC_D_form(prefix="hcd")
        leader_form = HC_D_LeaderForm(prefix="hcd_leader")
        member_form = HC_D_MemberFormSet(prefix="hcd_members")

    context = {
        "hcd_form": form,
        "hcd_leader_form": leader_form,
        "hcd_member_formset": member_form,
    }
    return context, valid


# Glamour Nova
def gn_m_section(request):
    valid = False

    if request.method == "POST":
        form = GN_M_Form(request.POST, prefix="gnm")
        leader_form = GN_M_LeaderForm(request.POST, prefix="gnm_leader")
        member_form = GN_M_MemberFormSet(
            request.POST,
            prefix="gnm_members"
        )

        valid1 = form.is_valid()
        valid2 = leader_form.is_valid()

        if valid2:
            member_form.leader_name = (
                leader_form.cleaned_data["fullName"].strip().casefold()
            )
            member_form.leader_email = (
                leader_form.cleaned_data["email"].strip().casefold()
            )
            member_form.leader_contact = (
                leader_form.cleaned_data["contactNumber"].strip()
            )

        valid3 = member_form.is_valid()

        if valid1 and valid2 and valid3:
            valid = True

    else:
        form = GN_M_Form(prefix="gnm")
        leader_form = GN_M_LeaderForm(prefix="gnm_leader")
        member_form = GN_M_MemberFormSet(prefix="gnm_members")

    context = {
        "gnm_form": form,
        "gnm_leader_form": leader_form,
        "gnm_member_formset": member_form,
    }
    return context, valid


# Section registry
REGISTRATION_SECTIONS = [
    sod_section,
    hc_d_section,
    gn_m_section,
]


# Master registration view
def registration(request):
    context = {}
    section_results = []

    for section in REGISTRATION_SECTIONS:
        section_context, section_valid = section(request)
        context.update(section_context)
        section_results.append(section_valid)

    if request.method == "POST" and all(section_results):
        pass

    return render(request, "core/registration.html", context)


# Success view
def success(request):
    """Temporary success page — replace with a proper template when ready."""
    return HttpResponse(
        "<h1>Registration successful!</h1>"
        "<p>You're registered for States of Dress. We'll be in touch.</p>"
        "<a href='/forms/'>Back to forms</a>",
        status=200,
    )
