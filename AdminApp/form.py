from django import forms
from .models import AdminModel


class AdminLoginForm(forms.Form):
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    hidden_field= forms.CharField(widget=forms.HiddenInput(), initial='login')




class AdminSignupForm(forms.Form):
    name = forms.CharField(label='Name',widget=forms.TextInput(attrs={'class': 'form-control','placeholder': 'Full Name'}))
    reg_number = forms.CharField(label='Registration Number',widget=forms.TextInput(attrs={'class': 'form-control','placeholder': 'Registration Number'}))
    email = forms.EmailField(label='Email',widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    hidden_fields = forms.CharField(widget=forms.HiddenInput(), initial='signup')
