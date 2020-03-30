from django import forms


class EmptySubmitForm(forms.Form):
    pass


class ShortStringSubmitForm(forms.Form):
    answer = forms.CharField(required=True)


class ShortIntSubmitForm(forms.Form):
    answer = forms.IntegerField(required=True)


class ShortFloatSubmitForm(forms.Form):
    answer = forms.FloatField(required=True)


class JudgeableFileSubmitForm(forms.Form):
    answer = forms.FileField(required=True)


class ProfilePictureUploadForm(forms.Form):
    picture = forms.FileField(required=True)


class StatUploadForm(forms.Form):
    stat = forms.FileField(required=True)
