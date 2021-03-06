from django import forms
from django.core import validators

class RegisterForm(forms.Form):
    email = forms.EmailField(min_length=5, max_length=254)
    password = forms.CharField(widget=forms.PasswordInput, min_length=8, max_length=254)
    password_confirmation = forms.CharField(widget=forms.PasswordInput)

class LoginForm(forms.Form):
    email = forms.EmailField(max_length=254)
    password = forms.CharField(widget=forms.PasswordInput, max_length=254)

class CreateProjectForm(forms.Form):
    project_name = forms.CharField(max_length=254)

class NewSentencesForm(forms.Form):
    sentences = forms.Textarea
