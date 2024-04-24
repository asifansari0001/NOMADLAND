from datetime import datetime

from django.utils import timezone

from django.shortcuts import render
from django.http import JsonResponse
import razorpay
from project1 import settings
from .models import *


def package_payment(request):
    user_id = request.session.get('user_id')
    bookings = BookingModel.objects.filter(user_id=user_id, created_at__date=timezone.now().date())

    latest_booking = bookings.latest('created_at')
    package_id = latest_booking.package_id_id
    packages = PackageModel.objects.get(package_id=package_id)
    destination = packages.destination_name

    total_price = latest_booking.total_price

    razor_price = total_price * 100

    from_date = latest_booking.from_date
    to_date = latest_booking.to_date

    package_image = PackageImagesModel.objects.filter(package_id=package_id)

    total_people = int(latest_booking.num_adult + latest_booking.num_children)
    agent = packages.agent

    user_data = UserModel.objects.filter(user_id=user_id)
    user_datas = UserModel.objects.get(user_id=user_id)
    username = user_datas.user_name

    context1 = {

        'bookings': bookings,
        'price': total_price,
        'razor_price': razor_price,
        'from_date': from_date,
        'to_date': to_date,
        'destination': destination,
        'package_image': package_image,
        'travelers': total_people,
        'agent': agent,
        'username': username,
        'user_data': user_data

    }

    if request.method == "POST":

        amount = int(request.POST.get("amount")) * 100
        client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))
        payment = client.order.create({'amount': amount, 'currency': 'INR', 'payment_capture': '1'})
        return JsonResponse(payment)

    else:
        return render(request, 'package_payment.html', context1)


def payment_success(request):
    user_id = request.session.get('user_id')
    user_data = UserModel.objects.filter(user_id=user_id)
    context = None
    if request.method == "POST":
        razorpay_signature = request.POST.get('razorpay_signature')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        price=request.POST.get('price')

        current_datetime = datetime.now()

        context = {

            'razorpay_signature': razorpay_signature,
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'user_data': user_data,
            'current_datetime': current_datetime,
            'price':price,

        }

    return render(request, 'payment_success.html', context)


def payment_failure(request):
    # Handle payment failure logic here
    return render(request, 'payment_failure.html')
