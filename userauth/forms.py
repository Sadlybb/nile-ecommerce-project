from django import forms
from django.contrib.auth.forms import UserCreationForm

from . models import User


class UserRegisterForm(UserCreationForm):

    email = forms.EmailField(widget=forms.EmailInput(
        attrs={'placeholder': 'Email'}))
    username = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': 'Username'}))
    password1 = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder': 'Password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder': 'Password Confirmation'}))

    class Meta:
        model = User
        fields = ['email', 'username', 'password1', 'password2']
