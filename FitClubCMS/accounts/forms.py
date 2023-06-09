from django import forms
from django.contrib.auth.models import User
from django.forms import DateInput

from .models import Profile


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"placeholder": "............."}),
    )
    password2 = forms.CharField(
        label="Repeat Password",
        widget=forms.PasswordInput(attrs={"placeholder": "............"}),
    )

    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "example@example.com"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].help_text = None

    class Meta:
        model = User
        fields = ["username", "first_name", "email"]

    def clean_password2(self):
        cd = self.cleaned_data
        if cd["password"] != cd["password"]:
            raise forms.ValidationError("Passwords don't match!")
        return cd["password2"]

    # preventing a user from registering with an already existing email address
    def clean_email(self):
        data = self.cleaned_data["email"]
        if User.objects.filter(email=data).exists():
            raise forms.ValidationError("Email already in use")
        return data


# UserEditForm allow users to edit the edit their first name, last name, and email, which are attributes of the built-in Django User model

# ProfileEditForm  allow users to edit the profile data that is saved in the custom Profile model


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]

    # preventing user from using an already existing email during profile editing
    def clean_email(self):
        data = self.cleaned_data["email"]
        qs = User.objects.exclude(id=self.instance.id).filter(email=data)
        if qs.exists():
            raise forms.ValidationError("Email already in use")
        return data


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            "phone_no",
            "sex",
            "date_of_birth",
            "photo",
        ]

        widgets = {
            "date_of_birth": DateInput(attrs={"type": "date"}),
        }

        photo = forms.ImageField(
          widget=forms.FileInput(attrs={"class": "custom-photo-field"})
        )



class SessionForm(forms.Form):
    trainers = []
    name = forms.CharField(max_length=255)
    start = forms.DateTimeField()
    end = forms.DateTimeField()
    trainer = forms.ChoiceField(
        choices=[(trainer.trainer_id, trainer.first_name) for trainer in trainers]
    )


class ReplyEmailForm(forms.Form):
    recipient = forms.EmailField()
    subject = forms.CharField(max_length=255)
    message = forms.CharField(widget=forms.Textarea)
