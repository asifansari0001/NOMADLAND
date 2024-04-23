from django import forms
from .models import AdminModel


class AdminLoginForm(forms.Form):
    email = forms.EmailField(label='Email',
                             widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password = forms.CharField(label='Password',
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    hidden_field = forms.CharField(widget=forms.HiddenInput(), initial='login')

    def clean_name(self):
        email=self.cleaned_data.get('email')
        if AdminModel.objects.filter(name=email).exists():
            raise forms.ValidationError('email already exists')
        return email

    def clean_password(self):
        password=self.cleaned_data.get('password')
        if AdminModel.objects.filter(password=password).exists():
            raise forms.ValidationError('password already exists')
        return password


class AdminSignupForm(forms.Form):
    name = forms.CharField(label='Name',
                           widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}))
    reg_number = forms.CharField(label='Registration Number', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Registration Number'}))
    email = forms.EmailField(label='Email',
                             widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password = forms.CharField(label='Password',
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    hidden_fields = forms.CharField(widget=forms.HiddenInput(), initial='signup')

    def clean_name(self):
        name=self.cleaned_data.get('name')
        if AdminModel.objects.filter(name=name).exists():
            raise forms.ValidationError('name already exists')
        return name

    def clean_reg_number(self):
        reg_number=self.cleaned_data.get('reg_number')
        if AdminModel.objects.filter(reg_number=reg_number).exists():
            raise forms.ValidationError('reg_number already exists')
        return reg_number

    def clean_email(self):
        email=self.cleaned_data.get('email')
        if AdminModel.objects.filter(email=email).exists():
            raise forms.ValidationError('email already exists')
        return email

    def clean_password(self):
        password=self.cleaned_data.get('password')
        if AdminModel.objects.filter(password=password).exists():
            raise forms.ValidationError('password already exists')
        return password




