from django import forms

from accounts import models as accounts_models


class RegisterUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = accounts_models.User
        fields = ["first_name", "last_name", "username", "email", "password"]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data["password"]
        confirm_password = cleaned_data["confirm_password"]

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Password does not match!")

        return cleaned_data
