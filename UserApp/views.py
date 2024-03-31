from django.shortcuts import render, redirect
from django.db.models import Q
from AgentApp.models import PackageModel
from .models import *


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


# def user(request):
#     packages = PackageModel.objects.all()
#     user_id = request.session.get('user_id')
#     user_data = None
#
#     if user_id:
#         user_data = UserModel.objects.filter(user_id=user_id)
#
#     context = {'package_data': packages, 'user_data': user_data}
#
#     if request.method == 'POST':
#         location = request.POST.get('input_location')
#         from_date = request.POST.get('input_depart')
#         to_date = request.POST.get('input_return')
#         adult = int(request.POST.get('input_adult'))
#         children = int(request.POST.get('input_children'))
#
#         total_people = adult + children
#
#         location_filter = PackageModel.objects.filter(destination_name__icontains=location)
#         split_data = PackageSplit.objects.filter(start_date=from_date, end_date=to_date)
#         split_data = split_data.filter(quantity__gte=total_people)
#
#         if location_filter.exists() and split_data.exists():
#             filtered_packages = location_filter.filter(packagesplit__in=split_data)
#             context['filtered_packages'] = filtered_packages
#             return render(request, 'package_filter.html', context)
#         else:
#             return render(request, 'login.html')
#
#     return render(request, 'index.html', context)


def user(request):
    packages = PackageModel.objects.all()
    user_id = request.session.get('user_id')
    user_data = None

    if user_id:
        user_data = UserModel.objects.filter(user_id=user_id)

    context = {'package_data': packages, 'user_data': user_data}

    if request.method == 'POST':
        location = request.POST.get('input_location')
        from_date = request.POST.get('input_depart')
        to_date = request.POST.get('input_return')
        adult = int(request.POST.get('input_adult', 0))
        children = int(request.POST.get('input_children', 0))
        print(from_date)
        print(to_date)

        total_people = adult + children
        print(total_people, 'total people')

        location_filter = PackageModel.objects.filter(destination_name__icontains=location)
        split_data = PackageSplit.objects.filter(
            Q(start_date__range=[from_date, to_date]) | Q(end_date__range=[from_date, to_date]) |
            Q(start_date__lte=from_date, end_date__gte=to_date) |
            Q(start_date__gte=from_date, end_date__lte=to_date)
        )
        print(location_filter, 'location')
        print(split_data, 'sp1')
        split_data = split_data.filter(quantity__gte=total_people)
        print(split_data, 'sp2')

        if location_filter.exists() and split_data.exists():
            filtered_packages = location_filter.filter(packagesplit__in=split_data)
            print(filtered_packages, 'all done')
            context['filtered_packages'] = filtered_packages
        else:
            return render(request, 'login.html')

        context['filtered_packages'] = filtered_packages
        request.session['filtered_package_ids'] = list(filtered_packages.values_list('package_id', flat=True))
        print(context['filtered_packages'], 'all to done')
        return render(request, 'package_filter.html', context)

    return render(request, 'index.html', context)


def package_filter(request):
    # Retrieve the filtered package IDs from the session
    filtered_package_ids = request.session.get('filtered_package_ids', [])

    # Reconstruct the queryset of filtered packages
    filtered_packages = PackageModel.objects.filter(package_id__in=filtered_package_ids)

    # Check if the request is a POST request
    if request.method == 'POST':
        # Handle form submission for price buttons
        price_option = request.POST.get('price_option')
        # Add logic to adjust queryset based on selected price option
        if price_option == 'low_high':
            filtered_packages = filtered_packages.order_by('price')
        elif price_option == 'high_low':
            filtered_packages = filtered_packages.order_by('-price')

        # Handle form submission for sort button
        sort_option = request.POST.get('sort_option')
        # Add logic to adjust queryset based on selected sort option
        if sort_option == 'latest':
            filtered_packages = filtered_packages.order_by('-created_at')
        elif sort_option == 'oldest':
            filtered_packages = filtered_packages.order_by('created_at')
        elif sort_option == 'customer_rating':
            # Add sorting logic based on customer rating
            pass
        elif sort_option == 'better_offer':
            # Add sorting logic based on better offer
            pass

    context = {'filtered_packages': filtered_packages}
    return render(request, 'package_filter.html', context)



def about(request):
    user_id = request.session.get('user_id')
    if user_id:
        user_data = UserModel.objects.filter(user_id=user_id)

        return render(request, 'nomadland_about.html', {'user_data': user_data})
    else:

        return render(request, 'nomadland_about.html')


def review(request):
    user_id = request.session.get('user_id')
    if user_id:
        user_data = UserModel.objects.filter(user_id=user_id)

        return render(request, 'nomadland_review.html', {'user_data': user_data})
    else:

        return render(request, 'nomadland_review.html')


def offer(request):
    return render(request, 'offer.html')


def package(request):
    return render(request, 'package.html')


def package_preview(request, id):
    return render(request, 'package_preview.html')


def package_payment(request):
    return render(request, 'package_payment.html')
