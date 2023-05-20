from django import forms
from django .contrib.auth.models import User
from .models import Profile


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label= 'Password',
                               widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat Password',
                                widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'first_name','email']

    def clean_password2(self):
        cd =self.cleaned_data
        if cd['password'] != cd['password']:
            raise forms.ValidationError('Passwords don\'t match!')
        return cd['password2']
         

# UserEditForm allow users to edit the edit their first name, last name, and email, which are attributes of the built-in Django User model

#ProfileEditForm  allow users to edit the profile data that is saved in the custom Profile model
 
class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields =  ['first_name', 'last_name', 'email']    

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['sex', 'phone_no', 'photo','date_of_birth']   