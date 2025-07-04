from django import forms

from django.contrib.auth.forms import AuthenticationForm

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="username",
                               widget=forms.TextInput(
                                   attrs={
                                       "class": "form-control",
                                       "placeholder": "Username"
                                   }))

    password = forms.CharField(label="password",
                                widget=forms.PasswordInput(
                                    attrs={
                                        "class": "form-control",
                                        "placeholder": "password"
                                    }
                                ))