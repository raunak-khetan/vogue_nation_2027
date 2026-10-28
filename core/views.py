from django.shortcuts import render,redirect
from django.db import transaction
from .models import GN_MTeam, GN_MTeamLeader, GN_MMember
from .forms import (
    HC_D_form, HC_D_LeaderForm, HC_D_MemberFormSet,
    GN_M_Form, GN_M_LeaderForm, GN_M_MemberFormSet,
)


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
            team_data = form.cleaned_data
            leader_data = leader_form.cleaned_data

            member_data = [
                member.cleaned_data
                for member in member_form
                if member.cleaned_data
            ]

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



def gn_m_section(request):
    valid = False

    if request.method == "POST":
        form = GN_M_Form(
            request.POST,
            prefix="gn_m_team"
        )

        leader_form = GN_M_LeaderForm(
            request.POST,
            prefix="gn_m_leader"
        )

        member_form = GN_M_MemberFormSet(
            request.POST,
            prefix="gn_m_members"
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
            valid = True

            team_data = form.cleaned_data
            leader_data = leader_form.cleaned_data

            member_data = [
                member.cleaned_data
                for member in member_form
                if member.cleaned_data
            ]

    else:
        form = GN_M_Form(prefix="gn_m_team")

        leader_form = GN_M_LeaderForm(
            prefix="gn_m_leader"
        )

        member_form = GN_M_MemberFormSet(
            prefix="gn_m_members"
        )

    context = {
        "gn_m_form": form,
        "gn_m_leader_form": leader_form,
        "gn_m_member_formset": member_form,
    }

    return context, valid



REGISTRATION_SECTIONS = (
    hc_d_section,
    gn_m_section,
)



def registration(request):
    context, valid = gn_m_section(request)

    if request.method == "POST" and valid:
        form = context["gn_m_form"]
        leader_form = context["gn_m_leader_form"]
        member_formset = context["gn_m_member_formset"]

        team_data = form.cleaned_data
        leader_data = leader_form.cleaned_data

        # Prevent duplicate team names.
        if GN_MTeam.objects.filter(
            teamName=team_data["teamName"]
        ).exists():
            form.add_error(
                "teamName",
                "A team with this name is already registered."
            )
        else:
            # Save the team, leader and members together.
            with transaction.atomic():
                team = GN_MTeam.objects.create(**team_data)

                GN_MTeamLeader.objects.create(
                    team=team,
                    **leader_data
                )

                for member_form in member_formset:
                    if member_form.cleaned_data:
                        GN_MMember.objects.create(
                            team=team,
                            **member_form.cleaned_data
                        )

            # Clear the submitted form after successful registration.
            return redirect(request.path)

    return render(request, "core/registration.html", context)
