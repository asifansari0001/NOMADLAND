from datetime import datetime, timezone
from .models import *
from django.shortcuts import render, redirect
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

        return render(request, 'package_filter.html', context)

    return render(request, 'index.html', context)


def package_filter(request):
    user_id = request.session.get('user_id')
    user_data = None
    if user_id:
        user_data = UserModel.objects.filter(user_id=user_id)

    # Retrieve the filtered package IDs from the session
    filtered_package_ids = request.session.get('filtered_package_ids', [])

    # Reconstruct the queryset of filtered packages
    filtered_packages = PackageModel.objects.filter(package_id__in=filtered_package_ids)

    # Check if the request is a POST request
    if request.method == 'POST':
        price_option = request.POST.get('price_option')
        # Add logic to adjust queryset based on selected price option
        if price_option == 'low_high':
            filtered_packages = filtered_packages.order_by('price')
        elif price_option == 'high_low':
            filtered_packages = filtered_packages.order_by('-price')
        context = {
            'filtered_packages': filtered_packages,
            'user_data': user_data,  # Include user_data in the context
        }
        return render(request, 'package_filter.html', context)

    # Get the IDs of filtered packages
    filtered_package_ids = filtered_packages.values_list('package_id', flat=True)

    # Reconstruct the queryset of filtered packages with the selected price order
    filtered_packages = PackageModel.objects.filter(package_id__in=filtered_package_ids)

    # Handle form submission for sort button
    sort_option = request.POST.get('sort_option')
    # Add logic to adjust queryset based on selected sort option
    if sort_option == 'latest':
        filtered_packages = filtered_packages.order_by('-created_at')
    elif sort_option == 'oldest':
        filtered_packages = filtered_packages.order_by('created_at')

    context = {
        'filtered_packages': filtered_packages,
        'user_data': user_data,  # Include user_data in the context
    }
    return render(request, 'package_filter.html', context)


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


def about(request):
    user_id = request.session.get('user_id')
    if user_id:
        user_data = UserModel.objects.filter(user_id=user_id)

        return render(request, 'nomadland_about.html', {'user_data': user_data})
    else:

        return render(request, 'nomadland_about.html')




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
    print(f"Found {expired_offers.count()} expired offers to update")

    # Update the status of expired offers to 'inactive'
    num_updated = expired_offers.update(status='inactive')
    print(f"Successfully updated status for {num_updated} expired offers")


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


def package_preview(request, id):
    return render(request, 'package_preview.html')


def package_payment(request):
    return render(request, 'package_payment.html')


def profile(request):
    user_id = request.session.get('user_id')
    if user_id:
        user_data = UserModel.objects.filter(user_id=user_id)

        return render(request, 'profiledisplay.html', {'user_data': user_data})
    else:

        return render(request, 'profiledisplay.html')


def wishlist(request):
    user_id = request.session.get('user_id')
    if user_id:
        user_data = UserModel.objects.filter(user_id=user_id)

        return render(request, 'wishlist.html', {'user_data': user_data})
    else:

        return render(request, 'wishlist.html')

