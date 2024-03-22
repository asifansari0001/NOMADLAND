from django.shortcuts import render, redirect, reverse
from AgentApp.models import *
from UserApp.models import *
from django.http import JsonResponse


# Create your views here.


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


def nation(request):
    if request.method == 'POST':
        nation_name = request.POST.get('nation_name')

        existing_nation = NationsModel.objects.filter(nation=nation_name).first()

        if existing_nation:
            request.session['nation_id'] = existing_nation.pk

        else:
            new_nation = NationsModel.objects.create(nation=nation_name)
            request.session['nation_id'] = new_nation.pk

        return redirect('/manage_package')

    return render(request, 'nation.html')


def manage_package(request):
    if request.method == 'POST':
        destination = request.POST.get('pk_destination')
        price = request.POST.get('pk_price')
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

        return redirect(reverse('activities') + f'?package_id={user_obj.pk}')

    return render(request, 'manage_package.html')


def activities(request):
    if request.method == 'POST':
        package_id = request.GET.get('package_id')  # Change from GET to POST

        # Handle the dynamic fields
        activity_names = request.POST.getlist('activity_name[]')
        activity_images = request.FILES.getlist('activity_image[]')
        activity_descriptions = request.POST.getlist('activity_description[]')

        for name, image, description in zip(activity_names, activity_images, activity_descriptions):
            new_activity = ActivitiesModel.objects.create(
                activities=name,
                activity_description=description,
                activity_images=image,
                package_id=PackageModel.objects.get(pk=package_id)
            )

        return redirect('home')  # Redirect to home page after saving activities

    return render(request, 'activities.html')



def agent_communication(request):
    return render(request, 'agent_communication.html')


def agent_analyticgraph(request):
    return render(request, 'agent_analyticgraph.html')
