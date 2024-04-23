from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from pyexpat.errors import messages

from .models import *
from .form import AdminLoginForm, AdminSignupForm


def welcome_admin(request):
    return render(request, 'admin.html')


def admin_login(request):
    form = AdminLoginForm()
    forms = AdminSignupForm()

    if request.method == 'POST':
        print('post')
        if 'hidden_field' in request.POST and request.POST['hidden_field'] == 'login':
            print('login')
            email = request.POST['email']
            password = request.POST['password']
            admin = AdminModel.objects.filter(email=email, password=password)
            if admin:
                print('log in successfully')
                return redirect('welcome_admin')
            else:
                return redirect('admin_login')

        elif 'hidden_fields' in request.POST and request.POST['hidden_fields'] == 'signup':
            print('signup')

            email = request.POST['email']

            existing_admin = AdminModel.objects.filter(email=email).exists()

            if existing_admin:
                print('exist')
                messages.error(request, 'User with this email already exists.')

            else:

                # Create a new AdminModel instance

                new_admin = AdminModel(

                    admin_name=request.POST['name'],

                    reg_no=request.POST['reg_number'],

                    email=email,

                    password=request.POST['password']

                )

                # Save the new admin instance to the database

                new_admin.save()
                print('saved')

                # Redirect the user to some success page or login page

                return redirect('admin_login')

    return render(request, 'admin_login.html', {'form': form, 'forms': forms})
