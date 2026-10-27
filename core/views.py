from django.shortcuts import render
from django.db import transaction
from .models import HCDTeam, HCDTeamLeader, HCDMember
from .forms import (
    HC_D_form, HC_D_LeaderForm, HC_D_MemberFormSet,
    GN_M_Form, GN_M_LeaderForm, GN_M_MemberFormSet,
)



def hc_d_section(request):
    valid = False

    if request.method == "POST":
        form = HC_D_form(request.POST, prefix="hcd")
        leader_form = HC_D_LeaderForm(
            request.POST,
            prefix="hcd_leader",
        )
        member_form = HC_D_MemberFormSet(
            request.POST,
            prefix="hcd_members",
        )

        valid1 = form.is_valid()
        valid2 = leader_form.is_valid()

        if valid2:
            member_form.leader_name = (
                leader_form.cleaned_data["fullName"]
                .strip()
                .casefold()
            )
            member_form.leader_email = (
                leader_form.cleaned_data["email"]
                .strip()
                .casefold()
            )
            member_form.leader_contact = (
                leader_form.cleaned_data["contactNumber"].strip()
            )

        valid3 = member_form.is_valid()

        if valid1 and valid2 and valid3:
            team_data = form.cleaned_data
            leader_data = leader_form.cleaned_data

            member_data = [
                member.cleaned_data
                for member in member_form
                if member.cleaned_data
            ]

            with transaction.atomic():
                hcd_team = HCDTeam.objects.create(
                    teamName=team_data["teamName"],
                    submitPerformances=team_data[
                        "submitPerformances"
                    ],
                )

                HCDTeamLeader.objects.create(
                    team=hcd_team,
                    **leader_data,
                )

                for hcd_member_data in member_data:
                    HCDMember.objects.create(
                        team=hcd_team,
                        **hcd_member_data,
                    )

            valid = True

    else:
        form = HC_D_form(prefix="hcd")
        leader_form = HC_D_LeaderForm(prefix="hcd_leader")
        member_form = HC_D_MemberFormSet(
            prefix="hcd_members",
        )

    context = {
        "hcd_form": form,
        "hcd_leader_form": leader_form,
        "hcd_member_formset": member_form,
    }

    return context, valid

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
            team_data = form.cleaned_data
            leader_data = leader_form.cleaned_data

            member_data = [
                member.cleaned_data
                for member in member_form
                if member.cleaned_data
            ]

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


REGISTRATION_SECTIONS = (
    hc_d_section,
   # gn_m_section,
)


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