from django import forms


class HC_D_form(forms.Form):
    teamName = forms.CharField(label="Team Name" , max_length=200 , widget = forms.TextInput(attrs={
        'placeholder':'Enter Team Name',
    })
    )

    submitPerformances = forms.URLField(label="Submit your performance(s)" , widget=forms.TextInput(attrs={
        'placeholder':'Enter Link Here',
    }))




class HC_D_LeaderForm(forms.Form):
    fullName = forms.CharField(label='Full Name' , max_length=100 , widget=forms.TextInput(attrs={
        'placeholder':'Full Name of Team Leader'
    }))

    contactNumber = forms.CharField(max_length=10 , label='Contact No.' , widget=forms.TextInput(attrs={
        'placeholder':'+91 Type your number',
    })
    )

    gender = forms.ChoiceField(label="Gender", choices=[("........" , ".........."),
         ("Male", "Male"),
        ("Female", "Female"),
        ("Other", "Other"),], )

    email = forms.EmailField(label='Email Address' , widget=forms.TextInput(attrs={
        'placeholder':'Enter Email Address'
    }))

    postalCode = forms.CharField(max_length=6 , label="Postal Code" , widget=forms.TextInput(attrs={
        'placeholder':'Type Here'
    }))

    cityName = forms.CharField(max_length=50 , label=' Your City ' , widget=forms.TextInput(attrs={
        'placeholder':'Typer Here'
    }))



class HC_D_MemberDetails(forms.Form):

    name = forms.CharField(label='Full Name', max_length=100, widget=forms.TextInput(attrs={
        'placeholder':'Enter your Full Name',
    }))

    email = forms.EmailField(label='Email Address' , widget=forms.TextInput(attrs={
            'placeholder':'Enter Email Address'
        }))

    contactNumber = forms.CharField(max_length=10 , label='Contact No.' , widget=forms.TextInput(attrs={
            'placeholder':'+91 Type your number',
        })
        )

    gender = forms.ChoiceField(label="Gender", choices=[("........" , ".........."),
         ("Male", "Male"),
        ("Female", "Female"),
        ("Other", "Other"),], )


    postalCode = forms.CharField(max_length=6 , label="Postal Code" , widget=forms.TextInput(attrs={
            'placeholder':'Type Here'
        }))
    
    cityName = forms.CharField(max_length=50 , label=' Your City ' , widget=forms.TextInput(attrs={
            'placeholder':'Typer Here'
        }))






