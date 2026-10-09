from django.shortcuts import render
from .forms import HC_D_form , HC_D_LeaderForm , HC_D_MemberDetails
# Create your views here.

def forms(request):
    form = HC_D_form()
    form2 = HC_D_LeaderForm()
    form3 = HC_D_MemberDetails()
    return render(request , 'core/forms.html' , {'form' : form  , 'form2' : form2 , 'form3':form3})