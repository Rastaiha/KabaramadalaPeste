from django import forms

from accounts.models import *


class SignUpForm(forms.Form):
    name = forms.CharField()
    email = forms.EmailField()
    phone = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    gender = forms.CharField()
    city = forms.CharField()
    school = forms.CharField()
    document = forms.FileField()

    def clean(self):
        if Member.objects.filter(email__exact=self.cleaned_data['email']).count() > 0:
            raise forms.ValidationError({'email', 'email is token'})
        return self.cleaned_data

