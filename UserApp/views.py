from django.shortcuts import render, redirect
from .models import *


def login(request):
    if request.method == 'POST':
        if 'user_signin' in request.POST:
            user_email = request.POST.get('user_email')
            user_password = request.POST.get('user_password')

            user = UserModel.objects.filter(user_email=user_email, user_password=user_password).first()

            if user:
                request.session['user_id'] = user.user_id
                user_data = UserModel.objects.filter(user_id=user.user_id)
                return render(request, 'home.html', {'data_key': user_data})

            if user is None:
                return render(request, 'login.html', {'error': 'Invalid Credentials'})

        if 'user_signup' in request.POST:
            user_name = request.POST.get('user_name')
            user_email = request.POST.get('user_email')
            user_password = request.POST.get('user_password')

            user_obj = UserModel()
            user_obj.user_name = user_name
            user_obj.user_email = user_email
            user_obj.user_password = user_password
            user_obj.save()

            return redirect('login')

    return render(request, 'login.html')


def user(request):
    packages = PackageModel.objects.all()

    context = {
        'package_data': packages
    }

    return render(request, 'index.html', context)


def about(request):
    return render(request, 'nomadland_about.html')


def review(request):
    return render(request, 'nomadland_review.html')


def home(request):
    return render(request, 'home.html')


def offer(request):
    return render(request, 'offer.html')


def package(request):
    return render(request, 'package.html')


def package_filter(request):
    return render(request, 'package_filter.html')


def package_preview(request, id):
    return render(request, 'package_preview.html')


def package_payment(request):
    return render(request, 'package_payment.html')
