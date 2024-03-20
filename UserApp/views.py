from django.shortcuts import render, redirect


def user(request):
    if request.method == 'POST':
        location = request.POST.get('input_location')
        depart = request.POST.get('input_depart')
        return_date = request.POST.get('input_return1')
        adults = request.POST.get('input_adult')
        children = request.POST.get('input_children')

        return render(request, 'package_filter.html', {
            'location': location,
            'depart': depart,
            'return_date': return_date,
            'adults': adults,
            'children': children,
        })

    return render(request, 'index.html')


def about(request):
    return render(request, 'nomadland_about.html')


def review(request):
    return render(request, 'nomadland_review.html')


def home(request):
    return render(request, 'home.html')


def login(request):
    return render(request, 'login.html')


def offer(request):
    return render(request, 'offer.html')


def package(request):
    return render(request, 'package.html')


def package_filter(request):
    return render(request, 'package_filter.html')


def package_preview(request):
    return render(request, 'package_preview.html')


def package_payment(request):
    return render(request, 'package_payment.html')
