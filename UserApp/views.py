from datetime import datetime, timezone

from AgentApp.models import ActivitiesModel, HotelImage
from .models import *
from .models import OfferModel, PackageModel, PackageImagesModel
from django.db.models import Min, Avg
from django.db.models import Q
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import FeedbackModel
from django.http import HttpResponse


def login(request):
    if request.method == 'POST':
        if 'user_signin' in request.POST:
            user_email = request.POST.get('user_email')
            user_password = request.POST.get('user_password')

            user = UserModel.objects.filter(user_email=user_email, user_password=user_password).first()

            if user:
                request.session['user_id'] = user.user_id
                return redirect('/')

            if user is None:
                return render(request, 'login.html')

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


def logout(request):
    if 'user_id' in request.session:
        del request.session['user_id']
    return redirect('/')


def home(request):
    user_id = request.session.get('user_id')

    if user_id:
        user_data = UserModel.objects.filter(user_id=user_id)

        return render(request, 'home.html', {'user_data': user_data})
    else:
        return render(request, 'home.html')


def user(request):
    packages = PackageModel.objects.all()
    user_id = request.session.get('user_id')
    user_data = None

    if user_id:
        user_data = UserModel.objects.filter(user_id=user_id)
    recommended_packages = PackageModel.objects.annotate(avg_rating=Avg('feedbackmodel__rating')).filter(
        avg_rating__gte=4, avg_rating__lte=5
    )
    context = {'package_data': packages, 'user_data': user_data, 'recommended_packages': recommended_packages}
    for package in packages:
        average_rating = FeedbackModel.objects.filter(package_id=package).aggregate(Avg('rating'))['rating__avg']
        package.average_rating = round(average_rating, 1) if average_rating else None

    if request.method == 'POST':
        location = request.POST.get('input_location')
        from_date = request.POST.get('input_depart')
        to_date = request.POST.get('input_return')
        adult = int(request.POST.get('input_adult', 0))
        children = int(request.POST.get('input_children', 0))

        total_people = adult + children

        location_filter = PackageModel.objects.filter(
            Q(nation_id__nation__icontains=location) |
            Q(destination_name__icontains=location)
        )
        split_data = PackageSplit.objects.filter(
            Q(start_date__range=[from_date, to_date]) | Q(end_date__range=[from_date, to_date]) |
            Q(start_date__lte=from_date, end_date__gte=to_date) |
            Q(start_date__gte=from_date, end_date__lte=to_date)
        )

        split_data = split_data.filter(quantity__gte=total_people)

        if location_filter.exists() and split_data.exists():
            filtered_packages = location_filter.filter(packagesplit__in=split_data)

            context['filtered_packages'] = filtered_packages
        else:
            return render(request, 'index.html')

        context['filtered_packages'] = filtered_packages
        request.session['filtered_package_ids'] = list(filtered_packages.values_list('package_id', flat=True))

        # return render(request, 'package_filter.html', context)
        return redirect('/package_filter')

    return render(request, 'index.html', context)


def review(request):
    user_id = request.session.get('user_id')
    review_data = WebsiteReviewModel.objects.all()
    user_data = None
    if user_id:
        user_data = UserModel.objects.get(user_id=user_id)

    context = {'user_data': user_data, 'review_data': review_data}

    if request.method == 'POST':
        review_text = request.POST.get('review_text')
        rating = int(request.POST.get('star'))
        review = WebsiteReviewModel.objects.create(user=user_data, review_text=review_text, rating=rating)
        review.save()

        # Redirect to a success page or back to review page
        return redirect('/review')  # Change 'review_success' to your success URL

    return render(request, 'nomadland_review.html', context)


def offer(request):
    update_expired_offers()
    user_id = request.session.get('user_id')

    # Filter offers where the status is active and the valid_to date is not in the past
    current_time = timezone.now()
    active_offers = OfferModel.objects.filter(status='active', valid_to__gte=current_time)

    # Filter packages associated with active offers
    packages_offers = []
    for package in PackageModel.objects.filter(offers__in=active_offers).distinct():
        package_images = PackageImagesModel.objects.filter(package_id=package)
        packages_offers.append({'package': package, 'images': package_images})

    context = {
        'packages_offers': packages_offers
    }

    if user_id:
        user_data = UserModel.objects.filter(user_id=user_id).first()
        if user_data:
            context['user_data'] = user_data

    # Fetch valid_to date from your database
    valid_to_date = active_offers.aggregate(min_valid_to=Min('valid_to'))['min_valid_to']
    context['valid_to'] = valid_to_date.strftime('%Y-%m-%d') if valid_to_date else None

    return render(request, 'offer.html', context)


def update_expired_offers():
    current_time = timezone.now()
    expired_offers = OfferModel.objects.filter(valid_to__lt=current_time, status='active')


    # Update the status of expired offers to 'inactive'
    num_updated = expired_offers.update(status='inactive')



def package_review(request, package_id):
    user_id = request.session.get('user_id')
    if user_id:
        user_data = UserModel.objects.filter(user_id=user_id)

        return render(request, 'package_review.html', {'user_data': user_data, 'package_id': package_id})
    else:

        return render(request, 'package_review.html', {'package_id': package_id})


def submit_feedback(request):
    if request.method == 'POST':
        package_id = request.POST.get('package_id')
        rating = request.POST.get('star')
        review = request.POST.get('review_text')

        # Convert package_id to an integer
        try:
            package_id = int(package_id)
        except ValueError:
            return HttpResponse("Invalid Package ID", status=400)

        # Retrieve the PackageModel instance
        package = get_object_or_404(PackageModel, pk=package_id)

        # Validate rating
        if rating is None:
            return HttpResponse("Rating is required", status=400)

        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError("Rating must be between 1 and 5")
        except ValueError:
            return HttpResponse("Invalid Rating", status=400)
        package_now = PackageModel.objects.get(package_id=package_id)
        user_id = request.session.get('user_id')
        user = UserModel.objects.get(user_id=user_id)
        # Create and save the feedback
        feedback = FeedbackModel(package_id=package_now, rating=rating, review=review, user_id=user)
        feedback.save()

        return redirect('/')
    else:
        return HttpResponse("Method Not Allowed", status=405)


def package(request):
    return render(request, 'package.html')


def package_payment(request):
    return render(request, 'package_payment.html')


def profile(request):
    user_id = request.session.get('user_id')
    if user_id:
        user_data = UserModel.objects.filter(user_id=user_id)

        return render(request, 'profiledisplay.html', {'user_data': user_data})
    else:

        return render(request, 'profiledisplay.html')


from django.http import JsonResponse
from .models import WishlistModel

# views.py

from django.shortcuts import render

from django.shortcuts import redirect
from django.contrib import messages


def package_filter(request):
    user_id = request.session.get('user_id')
    user_data = None
    if user_id:
        user_data = UserModel.objects.get(user_id=user_id)

    # Retrieve the filtered package IDs from the session
    filtered_package_ids = request.session.get('filtered_package_ids', [])

    # Reconstruct the queryset of filtered packages
    filtered_packages = PackageModel.objects.filter(package_id__in=filtered_package_ids)

    # Calculate average rating for each package
    filtered_packages = filtered_packages.annotate(average_rating=Avg('feedbackmodel__rating'))

    # Check if each package is in the wishlist
    for package in filtered_packages:
        package_in_wishlist = WishlistModel.objects.filter(user=user_data, package=package).exists()
        package.package_in_wishlist = package_in_wishlist

    if request.method == 'POST':
        price_option = request.POST.get('price_option')
        sort_option = request.POST.get('sort_option')

        if price_option == 'low_high':
            filtered_packages = filtered_packages.order_by('price')
        elif price_option == 'high_low':
            filtered_packages = filtered_packages.order_by('-price')

        if sort_option == 'latest':
            filtered_packages = filtered_packages.order_by('-created_at')
        elif sort_option == 'oldest':
            filtered_packages = filtered_packages.order_by('created_at')

    context = {
        'filtered_packages': filtered_packages,
        'user_data': user_data,  # Include user_data in the context
    }
    return render(request, 'package_filter.html', context)


def add_wishlist(request, package_id):
    user_id = request.session.get('user_id')

    if user_id:
        try:
            user_data = UserModel.objects.get(user_id=user_id)
            package = PackageModel.objects.get(package_id=package_id)

            if WishlistModel.objects.filter(user=user_data, package=package).exists():
                return redirect('/package_filter')
            else:
                wishlist = WishlistModel.objects.create(user=user_data, package=package)
                return redirect('/package_filter')
        except UserModel.DoesNotExist:
            return redirect('/login')
        except PackageModel.DoesNotExist:
            return redirect('/package_filter')
    else:
        return redirect('/login')


def remove_from_wishlist(request, package_id):
    user_id = request.session.get('user_id')
    if user_id:
        wishlist_remove = WishlistModel.objects.filter(user=user_id, package=package_id)

        wishlist_remove.delete()

        return redirect('/package_filter')
    else:
        return redirect('/login')


def wishlist(request):
    user_id = request.session.get('user_id')
    if user_id:
        user_data = UserModel.objects.filter(user_id=user_id)
        wishlist_items = WishlistModel.objects.filter(user=user_id)
    else:
        return redirect('/login')

    return render(request, 'wishlist.html', {'wishlist_items': wishlist_items, 'user_data': user_data})


def about(request):
    user_id = request.session.get('user_id')
    if user_id:
        user_data = UserModel.objects.filter(user_id=user_id)

        return render(request, 'nomadland_about.html', {'user_data': user_data})
    else:

        return render(request, 'nomadland_about.html')


def package_preview(request, package_id):
    user_id = request.session.get('user_id')
    user = UserModel.objects.filter(user_id=user_id)
    package = PackageModel.objects.get(package_id=package_id)
    package_split = PackageSplit.objects.filter(package_id=package_id)
    package_images = PackageImagesModel.objects.filter(package_id=package_id)
    activities = ActivitiesModel.objects.filter(package_id=package_id)
    feedbacks = FeedbackModel.objects.filter(package_id=package_id)

    package_split_durations = []

    for package_split_item in package_split:
        duration = (package_split_item.end_date - package_split_item.start_date).days
        package_split_durations.append(duration)

    # Calculate average rating for the package
    average_rating = feedbacks.aggregate(Avg('rating'))['rating__avg']
    package.average_rating = round(average_rating, 1) if average_rating else None

    hotel_images = []

    for split in package_split:
        package_hotel = PackageHotel.objects.filter(package_split_id=split.package_split_id)
        for hotel in package_hotel:
            hotel_image = HotelImage.objects.filter(hotel_id=hotel.hotel_id).first()
            if hotel_image:
                hotel_images.append(hotel_image)

    activity_images = []

    for activity in activities:
        if activity.activity_images:
            activity_images.append(activity.activity_images)

    if user_id:
        context1 = {
            'user_data': user,
            'package': package,
            'package_split': package_split,
            'package_images': package_images,
            'activities': activities,
            'package_split_durations': package_split_durations,
            'feedbacks': feedbacks,
            'hotel_images': hotel_images,
            'activity_images': activity_images,
        }
        return render(request, 'package_preview.html', context1)
    else:
        context2 = {
            'package': package,
            'package_split': package_split,
            'package_images': package_images,
            'activities': activities,
            'package_split_durations': package_split_durations,
            'feedbacks': feedbacks,
            'hotel_images': hotel_images,
            'activity_images': activity_images,
        }

    return render(request, 'package_preview.html', context2)


def hotel_select(request, package_split_id):
    package_hotels = PackageHotel.objects.filter(package_split_id=package_split_id)
    user_id = request.session.get('user_id')

    pack_split = PackageSplit.objects.filter(package_split_id=package_split_id)
    package_id = pack_split[0].package_id_id

    children = None
    adults = None
    car_rental = None

    if request.method == 'POST':
        # Accessing form data
        car_rental = request.POST.get('input_car_rental')
        adults = request.POST.get('input_adult')
        children = request.POST.get('input_children')

    # Initialize an empty list to store hotel instances
    hotels = []

    # Iterate over each package hotel to retrieve the associated hotel
    for package_hotel in package_hotels:
        # Retrieve the hotel associated with the package hotel
        hotel = package_hotel.hotel_id
        # Add the hotel instance to the list
        hotels.append(hotel)

    hotel_images = HotelImage.objects.select_related('hotel_id').all()

    if user_id:
        user_data = UserModel.objects.filter(user_id=user_id)
        context1 = {

            'hotels': hotels,
            'hotel_images': hotel_images,
            'package_hotels': package_hotels,
            'user_data': user_data,
            'package_id': package_id,
            'children': children,
            'adults': adults,
            'car_rental': car_rental

        }
        return render(request, 'hotel_select.html', context1)

    return redirect('/login')


def booking_user(request):
    adults = None
    children = None
    car_rental = None
    package_id = None
    hotel_id = None

    if request.method == 'POST':
        children = request.POST.get('children')
        car_rental = request.POST.get('car_rental')
        adults = request.POST.get('adults')
        package_id = request.POST.get('package_id')
        hotel_id = request.POST.get('hotel_id')

    package_id = package_id
    hotel_id = hotel_id

    user_id = request.session.get('user_id')
    usermodel = UserModel.objects.get(user_id=user_id)
    package_split = PackageSplit.objects.get(package_id=package_id)
    packagemodel = PackageModel.objects.get(package_id=package_id)

    package_split_from_date = package_split.start_date
    package_split_to_date = package_split.end_date

    package_hotel = PackageHotel.objects.get(hotel_id=hotel_id)
    package_hotel_price = package_hotel.price
    package_price = packagemodel.price
    total_price = int(package_hotel_price + package_price)

    booking_obj = BookingModel()
    booking_obj.from_date = package_split_from_date
    booking_obj.to_date = package_split_to_date
    booking_obj.total_price = total_price
    booking_obj.num_adult = adults
    booking_obj.num_children = children
    booking_obj.car_rental = car_rental
    booking_obj.package_id = packagemodel
    booking_obj.package_hotel_id = package_hotel
    booking_obj.user_id = usermodel

    booking_obj.save()

    return redirect('/package_payment')


def history_booking(request):
    if 'user_id' in request.session:
        user_id = request.session.get('user_id')
        user_data = UserModel.objects.filter(user_id=user_id)

        # Filter bookings with status 'complete'
        bookings = BookingModel.objects.filter(user_id=user_id, booking_status='complete')

        # Lists to store individual booking details
        total_prices = []
        destinations = []
        package_imgs = []
        from_dates = []
        to_dates = []

        # Iterate over filtered bookings queryset to fetch individual booking details
        for booking in bookings:
            total_prices.append(booking.total_price)
            from_dates.append(booking.from_date)
            to_dates.append(booking.to_date)

            # Fetch destination name
            destination = PackageModel.objects.get(package_id=booking.package_id_id).destination_name
            destinations.append(destination)

            # Fetch package image
            package_images = PackageImagesModel.objects.filter(package_id=booking.package_id)
            if package_images.exists():
                package_img = package_images.first().image
            else:
                package_img = None  # Handle the case where no image is found
            package_imgs.append(package_img)

        # Zip the lists together
        booking_data = zip(total_prices, destinations, package_imgs, from_dates, to_dates)

        context = {
            'booking_data': booking_data,
            'user_data': user_data,
        }

        return render(request, 'history_booking.html', context)
    else:
        return redirect('/login')


