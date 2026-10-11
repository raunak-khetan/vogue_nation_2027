
from django.shortcuts import render

from .forms import HC_D_form,HC_D_LeaderForm, MemberFormSet



def forms(request):
    if request.method == "POST":
        form = HC_D_form(request.POST)
        leader_form = HC_D_LeaderForm(request.POST)
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
        form = HC_D_form()
        leader_form = HC_D_LeaderForm()
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
