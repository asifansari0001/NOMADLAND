from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .form import AdminLoginForm, AdminSignupForm


def welcome_admin(request):
    return render(request, 'admin.html')


def admin_login(request):
    form = AdminLoginForm()
    forms = AdminSignupForm()
    if request.method == 'POST':
        if 'hidden_field' in request.POST and request.POST['hidden_field'] == 'login':
            print('login')
            form = AdminLoginForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data['email']
                password = form.cleaned_data['password']
                user = authenticate(request, email=email, password=password)
                if user is not None:
                    login(request, user)
                    # Redirect to a success page
                    return redirect('/welcome_admin')
            else:
                return render(request, 'admin_login.html', {'form': form, 'forms': forms})

        if 'hidden_field' in request.POST and request.POST['hidden_field'] == 'signup':

            forms = AdminSignupForm(request.POST)
            if forms.is_valid():
                # Process the form data and create a new user account
                # Redirect to a success page
                return redirect('/admin')  # Replace 'success_page' with the name of your success page URL
            else:
                forms = AdminSignupForm()
            return render(request, 'signup.html', {'forms': forms})

    else:

        return render(request, 'admin_login.html', {'form': form, 'forms': forms})
