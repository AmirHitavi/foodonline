from django import forms
from accounts.validators import valid_image_extensions
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


class UserProfileForm(forms.ModelForm):

    address = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'start typing ...', 'required': 'required'}))

    profile_picture = forms.FileField(widget=forms.FileInput(attrs={'class': 'btb btn-info'}),
                                      validators=[valid_image_extensions])
    cover_photo = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info'}),
                                  validators=[valid_image_extensions])

    class Meta:
        model = accounts_models.UserProfile
        fields = [
            "profile_picture",
            "cover_photo",
            "address",
            "country",
            "state",
            "city",
            "pin_code",
            "latitude",
            "longitude",
        ]

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            if field in ["latitude", "longitude"]:
                self.fields[field].widget.attrs["readonly"] = 'readonly'