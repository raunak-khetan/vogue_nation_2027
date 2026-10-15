
from django.shortcuts import render

from .forms import GN_M_Form, GN_M_LeaderForm, MemberFormSet


def forms(request):
    if request.method == "POST":
        form = GN_M_Form(request.POST)
        leader_form = GN_M_LeaderForm(request.POST)
        member_form = MemberFormSet(
            request.POST,
            prefix="members"
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
            team_data = form.cleaned_data
            leader_data = leader_form.cleaned_data

            member_data = [
                member.cleaned_data
                for member in member_form
                if member.cleaned_data
            ]

    else:
        form = GN_M_Form()
        leader_form = GN_M_LeaderForm()
        member_form = MemberFormSet(prefix="members")

    return render(
        request,
        "core/forms.html",
        {
            "form": form,
            "form2": leader_form,
            "form3": member_form,
        },
    )
