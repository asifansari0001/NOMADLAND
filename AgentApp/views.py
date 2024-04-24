from django.shortcuts import render, redirect, reverse
from AgentApp.models import *
from UserApp.models import *


def agent_login(request):
    if request.method == 'POST':
        if 'agent_signin' in request.POST:
            agent_email = request.POST.get('agent_email')
            agent_password = request.POST.get('agent_password')

            agent = AgentModel.objects.filter(agent_email=agent_email, agent_password=agent_password).first()

            if agent:
                request.session['agent_id'] = agent.agent_id
                agent_data = AgentModel.objects.filter(agent_id=agent.agent_id)
                return render(request, 'welcome_agent.html', {'data_key': agent_data})

            if agent is None:
                return render(request, 'agent_login.html', {'error': 'Invalid Credentials'})

        if 'agent_signup' in request.POST:
            agent_name = request.POST.get('agent_name')
            agent_email = request.POST.get('agent_email')
            agent_password = request.POST.get('agent_password')
            agent_phone = request.POST.get('agent_phone')
            agent_license = request.POST.get('agent_license')

            agent_obj = AgentModel()
            agent_obj.agent_name = agent_name
            agent_obj.agent_email = agent_email
            agent_obj.agent_password = agent_password
            agent_obj.agent_phone = agent_phone
            agent_obj.agent_license = agent_license
            agent_obj.save()

            return redirect('agent_login')

    return render(request, 'agent_login.html')


def welcome_agent(request):
    return render(request, 'welcome_agent.html')


def agent_manage(request):
    return render(request, 'agent_manage.html')


def manage_package(request):
    agent_id = request.session.get('agent_id')
    agent = AgentModel.objects.get(agent_id=agent_id)
    packages = PackageModel.objects.filter(agent_id=agent)

    context = {
        'data_key': packages
    }

    if request.method == 'POST':

        nation_name = request.POST.get('nation_name')

        existing_nation = NationsModel.objects.filter(nation=nation_name).first()

        if existing_nation:
            request.session['nation_id'] = existing_nation.pk

        else:
            new_nation = NationsModel.objects.create(nation=nation_name)
            request.session['nation_id'] = new_nation.pk

        destination = request.POST.get('destination')
        price = request.POST.get('price')
        description = request.POST.get('activity_description')
        agent_id = request.session.get('agent_id')
        nation_id = request.session.get('nation_id')

        user_obj = PackageModel()
        user_obj.destination_name = destination
        user_obj.price = price
        user_obj.description = description
        user_obj.agent = AgentModel.objects.get(agent_id=agent_id)
        user_obj.nation_id = NationsModel.objects.get(nations_id=nation_id)
        user_obj.save()

        image = request.FILES.get('image')

        image_obj = PackageImagesModel()
        image_obj.image = image
        image_obj.package_id = PackageModel.objects.get(package_id=user_obj.pk)
        image_obj.save()

        image2 = request.FILES.get('image2')
        if image2:
            image2_obj = PackageImagesModel()
            image2_obj.image = image2
            image2_obj.package_id = PackageModel.objects.get(package_id=user_obj.pk)
            image2_obj.save()

        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        quantity = request.POST.get('quantity')
        split = PackageSplit()
        split.start_date = start_date
        split.end_date = end_date
        split.quantity = quantity
        split.package_id = PackageModel.objects.get(package_id=user_obj.pk)
        split.save()

        request.session['package_id'] = user_obj.pk
        return redirect(reverse('activities') + f'?package_id={user_obj.pk}')

    return render(request, 'manage_package.html', context)


def activities(request):
    if request.method == 'POST':
        package_id = request.GET.get('package_id')

        activity_names = request.POST.getlist('activity_name[]')
        activity_images = request.FILES.getlist('activity_image[]')
        activity_descriptions = request.POST.getlist('activity_description[]')

        for name, image, description in zip(activity_names, activity_images, activity_descriptions):
            new_activity = ActivitiesModel.objects.create(
                activities=name,
                activity_description=description,
                activity_images=image,
                package_id=PackageModel.objects.get(package_id=package_id)
            )

        return redirect('hotel_add')

    return render(request, 'activities.html')


def hotel_add(request):
    if request.method == 'POST':

        package_id = request.session.get('package_id')

        hotel_names = request.POST.getlist('hotel_name[]')
        hotel_prices = request.POST.getlist('hotel_price[]')
        hotel_quantities = request.POST.getlist('hotel_quantity[]')
        hotel_images = request.FILES.getlist('hotel_image[]')

        # Loop through the submitted data and save hotels
        for name, price, quantity, image in zip(hotel_names, hotel_prices, hotel_quantities, hotel_images):
            # Create hotel instance
            hotel = HotelModel.objects.create(hotel_name=name)

            # Save hotel image
            hotel_image = HotelImage.objects.create(hotel_id=hotel, hotel_image=image)

            # Get package split associated with this hotel
            package_split_id = PackageSplit.objects.get(package_id=package_id)

            # Create package hotel instance
            package_hotel = PackageHotel.objects.create(
                hotel_id=hotel,
                package_split_id=package_split_id,
                price=price,
                quantity=quantity
            )

        return redirect('/agent_offer')

    return render(request, 'hotel_add.html')


def agent_offer(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        discount_percentage = request.POST.get('discount_percentage')
        valid_from = request.POST.get('valid_from')
        valid_to = request.POST.get('valid_to')
        status = request.POST.get('status')

        agent_id = request.session.get('agent_id')
        package_id = request.session.get('package_id')

        # Create and save the offer object
        offer_obj = OfferModel(
            title=title,
            description=description,
            discount_percentage=discount_percentage,
            valid_from=valid_from,
            valid_to=valid_to,
            status=status
        )
        offer_obj.save()

        # Add the agent and package to the offer
        offer_obj.applicable_agents.add(agent_id)
        offer_obj.applicable_packages.add(package_id)

        return redirect('/welcome_agent')

    return render(request, 'agent_offer.html')


def logout(request):
    if 'agent_id' in request.session:
        del request.session['agent_id']
    return redirect('/')


def package_remove(request, package_id):
    package_del = PackageModel.objects.filter(package_id=package_id)
    package_del.delete()
    return redirect('/manage_package')


# update package


def pack_img_del(request, image_id):
    img_del = PackageImagesModel.objects.filter(image_id=image_id)
    img_del.delete()
    package_id = request.GET.get('package_id')
    destination = PackageModel.objects.filter(package_id=package_id)
    package_image = PackageImagesModel.objects.filter(package_id=package_id)
    activity = ActivitiesModel.objects.filter(package_id=package_id)

    package_split = PackageSplit.objects.filter(package_id=package_id).first()
    hotel_package_ids = PackageHotel.objects.filter(package_split_id=package_split.package_split_id)

    hotel_ids = [hotel_package.hotel_id_id for hotel_package in hotel_package_ids]

    hotel_images = HotelImage.objects.filter(hotel_id__in=hotel_ids)
    hotel_names = HotelModel.objects.filter(hotel_id__in=hotel_ids)

    hotel_details = PackageHotel.objects.filter(package_split_id=package_split.package_split_id)

    # Zip hotel_details and hotel_images together with hotel_names
    hotel_data = zip(hotel_names, hotel_details, hotel_images)

    destination_for_nation = PackageModel.objects.get(package_id=package_id)
    nation = NationsModel.objects.get(nation=destination_for_nation.nation_id)

    package_split_data = PackageSplit.objects.get(package_id=package_id)
    package_start_date_formatted = package_split_data.start_date
    package_end_date_formatted = package_split_data.end_date

    if request.method == 'POST':
        nation_name = request.POST.get('nation_name')

        destination_name = request.POST.get('destination')
        package_quantity = request.POST.get('package_quantity')
        package_status = request.POST.get('package_status')
        package_description = request.POST.get('package_description')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        package_price = request.POST.get('package_price')
        package_images = request.FILES.get('package_image')
        activity_name = request.POST.get('activity_name')
        activity_description = request.POST.get('activity_description')
        activity_img = request.FILES.get('activity_img')
        hotel_name = request.POST.get('hotel_name')
        hotel_quantity = request.POST.get('hotel_quantity')
        hotel_price = request.POST.get('hotel_price')
        hotel_image = request.FILES.get('hotel_image')
        target_activity_id = request.POST.get('target_activity_id')

        nation_obj = NationsModel.objects.get(nation=destination_for_nation.nation_id)
        nation_obj.nation = nation_name
        nation_obj.save()

        pack_obj = PackageModel.objects.get(package_id=package_id)
        pack_obj.destination_name = destination_name
        pack_obj.status = package_status
        pack_obj.package_description = package_description
        pack_obj.package_price = package_price

        if package_images:
            package = PackageModel.objects.get(package_id=package_id)

            # Create a new instance of PackageImagesModel with the retrieved PackageModel instance
            pak_img = PackageImagesModel.objects.create(package_id=package, image=package_images)

        pack_obj.save()

        split_obj = PackageSplit.objects.get(package_id=package_id)
        split_obj.quantity = package_quantity
        split_obj.start_date = start_date
        split_obj.end_date = end_date
        split_obj.save()

        for activity in ActivitiesModel.objects.filter(package_id=package_id):
            activity_name = request.POST.get(f'activity_name_{activity.activities_id}')
            activity_description = request.POST.get(f'activity_description_{activity.activities_id}')
            activity_img = request.FILES.get(f'activity_img_{activity.activities_id}')

            if activity_name and activity_description:
                activity.activities = activity_name
                activity.activity_description = activity_description

                if activity_img:
                    activity.activity_images = activity_img

                activity.save()

        # done till here

        for hotel, details, image in hotel_data:
            hotel_id = hotel.hotel_id
            hotel_name = request.POST.get(f'hotel_name_{hotel_id}')
            hotel_quantity = request.POST.get(f'hotel_quantity_{hotel_id}')
            hotel_price = request.POST.get(f'hotel_price_{hotel_id}')
            hotel_image = request.FILES.get(f'hotel_image_{hotel_id}')

            # Update hotel name
            hotel_obj = HotelModel.objects.get(hotel_id=hotel_id)
            hotel_obj.hotel_name = hotel_name
            hotel_obj.save()

            # Update package-hotel details
            pack_hotel_obj = PackageHotel.objects.get(hotel_id=hotel_id)
            pack_hotel_obj.quantity = hotel_quantity
            pack_hotel_obj.price = hotel_price
            pack_hotel_obj.save()

            # Update hotel image if provided
            if hotel_image:
                image_obj = HotelImage.objects.get(hotel_id=hotel_obj.hotel_id)

                image_obj.hotel_image = hotel_image
                image_obj.save()

        return redirect('/update_package')

    return render(request, 'update_package.html', {
        'data_key': destination,
        'image_key': package_image,
        'activities': activity,
        'hotel_data': hotel_data,
        'nation': nation,
        'package_split': package_split_data,
        'package_start_date': package_start_date_formatted,
        'package_end_date': package_end_date_formatted
    })


def hotel_img_del(request, hotel_image_id):
    img_del = HotelImage.objects.filter(hotel_image_id=hotel_image_id)
    img_del.delete()
    package_id = request.GET.get('package_id')
    destination = PackageModel.objects.filter(package_id=package_id)
    package_image = PackageImagesModel.objects.filter(package_id=package_id)
    activity = ActivitiesModel.objects.filter(package_id=package_id)

    package_split = PackageSplit.objects.filter(package_id=package_id).first()
    hotel_package_ids = PackageHotel.objects.filter(package_split_id=package_split.package_split_id)

    hotel_ids = [hotel_package.hotel_id_id for hotel_package in hotel_package_ids]

    hotel_images = HotelImage.objects.filter(hotel_id__in=hotel_ids)
    hotel_names = HotelModel.objects.filter(hotel_id__in=hotel_ids)

    hotel_details = PackageHotel.objects.filter(package_split_id=package_split.package_split_id)

    # Zip hotel_details and hotel_images together with hotel_names
    hotel_data = zip(hotel_names, hotel_details, hotel_images)

    destination_for_nation = PackageModel.objects.get(package_id=package_id)
    nation = NationsModel.objects.get(nation=destination_for_nation.nation_id)

    package_split_data = PackageSplit.objects.get(package_id=package_id)
    package_start_date_formatted = package_split_data.start_date
    package_end_date_formatted = package_split_data.end_date

    if request.method == 'POST':
        nation_name = request.POST.get('nation_name')

        destination_name = request.POST.get('destination')
        package_quantity = request.POST.get('package_quantity')
        package_status = request.POST.get('package_status')
        package_description = request.POST.get('package_description')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        package_price = request.POST.get('package_price')
        package_images = request.FILES.get('package_image')
        # activity_name = request.POST.get('activity_name')
        # activity_description = request.POST.get('activity_description')
        # activity_img = request.FILES.get('activity_img')
        # hotel_name = request.POST.get('hotel_name')
        # hotel_quantity = request.POST.get('hotel_quantity')
        # hotel_price = request.POST.get('hotel_price')
        # hotel_image = request.FILES.get('hotel_image')
        # target_activity_id = request.POST.get('target_activity_id')

        nation_obj = NationsModel.objects.get(nation=destination_for_nation.nation_id)
        nation_obj.nation = nation_name
        nation_obj.save()

        pack_obj = PackageModel.objects.get(package_id=package_id)
        pack_obj.destination_name = destination_name
        pack_obj.status = package_status
        pack_obj.package_description = package_description
        pack_obj.package_price = package_price

        if package_images:
            package = PackageModel.objects.get(package_id=package_id)

            # Create a new instance of PackageImagesModel with the retrieved PackageModel instance
            pak_img = PackageImagesModel.objects.create(package_id=package, image=package_images)

        pack_obj.save()

        split_obj = PackageSplit.objects.get(package_id=package_id)
        split_obj.quantity = package_quantity
        split_obj.start_date = start_date
        split_obj.end_date = end_date
        split_obj.save()

        for activity in ActivitiesModel.objects.filter(package_id=package_id):
            activity_name = request.POST.get(f'activity_name_{activity.activities_id}')
            activity_description = request.POST.get(f'activity_description_{activity.activities_id}')
            activity_img = request.FILES.get(f'activity_img_{activity.activities_id}')

            if activity_name and activity_description:
                activity.activities = activity_name
                activity.activity_description = activity_description

                if activity_img:
                    activity.activity_images = activity_img

                activity.save()

        for hotel, details, image in hotel_data:
            hotel_id = hotel.hotel_id
            hotel_name = request.POST.get(f'hotel_name_{hotel_id}')
            hotel_quantity = request.POST.get(f'hotel_quantity_{hotel_id}')
            hotel_price = request.POST.get(f'hotel_price_{hotel_id}')
            hotel_image = request.FILES.get(f'hotel_image_{hotel_id}')

            # Update hotel name
            hotel_obj = HotelModel.objects.get(hotel_id=hotel_id)
            hotel_obj.hotel_name = hotel_name
            hotel_obj.save()

            # Update package-hotel details
            pack_hotel_obj = PackageHotel.objects.get(hotel_id=hotel_id)
            pack_hotel_obj.quantity = hotel_quantity
            pack_hotel_obj.price = hotel_price
            pack_hotel_obj.save()

            # Update hotel image if provided
            if hotel_image:
                image_obj = HotelImage.objects.get(hotel_id=hotel_obj.hotel_id)

                image_obj.hotel_image = hotel_image
                image_obj.save()

        return redirect('/update_package')

    return render(request, 'update_package.html', {
        'data_key': destination,
        'image_key': package_image,
        'activities': activity,
        'hotel_data': hotel_data,
        'nation': nation,
        'package_split': package_split_data,
        'package_start_date': package_start_date_formatted,
        'package_end_date': package_end_date_formatted
    })


def package_update(request, package_id):
    destination = PackageModel.objects.filter(package_id=package_id)
    package_image = PackageImagesModel.objects.filter(package_id=package_id)
    activity = ActivitiesModel.objects.filter(package_id=package_id)

    package_split = PackageSplit.objects.filter(package_id=package_id).first()
    hotel_package_ids = PackageHotel.objects.filter(package_split_id=package_split.package_split_id)
    hotel_ids = [hotel_package.hotel_id_id for hotel_package in hotel_package_ids]
    hotel_images = HotelImage.objects.filter(hotel_id__in=hotel_ids)
    hotel_names = HotelModel.objects.filter(hotel_id__in=hotel_ids)
    hotel_details = PackageHotel.objects.filter(package_split_id=package_split.package_split_id)
    # Zip hotel_details and hotel_images together with hotel_names
    hotel_data = zip(hotel_names, hotel_details, hotel_images)

    destination_for_nation = PackageModel.objects.get(package_id=package_id)
    nation = NationsModel.objects.get(nation=destination_for_nation.nation_id)

    package_split_data = PackageSplit.objects.get(package_id=package_id)
    package_start_date_formatted = package_split_data.start_date
    package_end_date_formatted = package_split_data.end_date

    if request.method == 'POST':
        nation_name = request.POST.get('nation_name')

        destination_name = request.POST.get('destination')
        package_quantity = request.POST.get('package_quantity')
        package_status = request.POST.get('package_status')
        package_description = request.POST.get('package_description')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        package_price = request.POST.get('package_price')
        package_images = request.FILES.get('package_image')

        # activity_name = request.POST.get('activity_name')
        # activity_description = request.POST.get('activity_description')
        # activity_img = request.FILES.get('activity_img')
        # hotel_name = request.POST.get('hotel_name')
        # hotel_quantity = request.POST.get('hotel_quantity')
        # hotel_price = request.POST.get('hotel_price')
        # hotel_image = request.FILES.get('hotel_image')
        # target_activity_id = request.POST.get('target_activity_id')

        nation_obj = NationsModel.objects.get(nation=destination_for_nation.nation_id)
        nation_obj.nation = nation_name
        nation_obj.save()

        pack_obj = PackageModel.objects.get(package_id=package_id)
        pack_obj.destination_name = destination_name
        pack_obj.status = package_status
        pack_obj.package_description = package_description
        pack_obj.package_price = package_price

        if package_images:
            package = PackageModel.objects.get(package_id=package_id)

            # Create a new instance of PackageImagesModel with the retrieved PackageModel instance
            pak_img = PackageImagesModel.objects.create(package_id=package, image=package_images)

        pack_obj.save()

        split_obj = PackageSplit.objects.get(package_id=package_id)
        split_obj.quantity = package_quantity
        split_obj.start_date = start_date
        split_obj.end_date = end_date
        split_obj.save()

        for activity in ActivitiesModel.objects.filter(package_id=package_id):
            activity_name = request.POST.get(f'activity_name_{activity.activities_id}')
            activity_description = request.POST.get(f'activity_description_{activity.activities_id}')
            activity_img = request.FILES.get(f'activity_img_{activity.activities_id}')

            if activity_name and activity_description:
                activity.activities = activity_name
                activity.activity_description = activity_description

                if activity_img:
                    activity.activity_images = activity_img

                activity.save()

        # done till here

        for hotel, details, image in hotel_data:
            hotel_id = hotel.hotel_id
            hotel_name = request.POST.get(f'hotel_name_{hotel_id}')
            hotel_quantity = request.POST.get(f'hotel_quantity_{hotel_id}')
            hotel_price = request.POST.get(f'hotel_price_{hotel_id}')
            hotel_image = request.FILES.get(f'hotel_image_{hotel_id}')

            # Update hotel name
            hotel_obj = HotelModel.objects.get(hotel_id=hotel_id)
            hotel_obj.hotel_name = hotel_name
            hotel_obj.save()

            # Update package-hotel details
            pack_hotel_obj = PackageHotel.objects.get(hotel_id=hotel_id)
            pack_hotel_obj.quantity = hotel_quantity
            pack_hotel_obj.price = hotel_price
            pack_hotel_obj.save()

            # Update hotel image if provided
            if hotel_image:
                image_obj = HotelImage.objects.get(hotel_id=hotel_obj.hotel_id)

                image_obj.hotel_image = hotel_image
                image_obj.save()

        return redirect('/update_package')

    return render(request, 'update_package.html', {
        'data_key': destination,
        'image_key': package_image,
        'activities': activity,
        'hotel_data': hotel_data,
        'nation': nation,
        'package_split': package_split_data,
        'package_start_date': package_start_date_formatted,
        'package_end_date': package_end_date_formatted
    })


def agent_communication(request):
    return render(request, 'agent_communication.html')


def agent_analyticgraph(request):
    return render(request, 'agent_analyticgraph.html')


def contact(request):
    user_id = request.session.get('user_id')
    if user_id:
        user_data = UserModel.objects.filter(user_id=user_id)
        return render(request, 'contact.html', {'user_data': user_data})
    return render(request, 'contact.html')


def booking_approval(request, booking_id):
    if request.method == 'POST':
        booking = BookingModel.objects.get(booking_id=booking_id)
        if 'approve' in request.POST:
            booking.booking_status = 'approved'
        elif 'deny' in request.POST:
            booking.booking_status = 'denied'
        booking.save()
        return redirect('/agent_booking')
    else:
        return render(request, 'agent_manage.html')


def agent_booking(request):
    bookings = BookingModel.objects.filter(booking_status='pending',payment_status='complete')
    context = {
        'bookings': bookings,
    }
    return render(request, 'agent_manage.html', context)

