from django.shortcuts import render, redirect, HttpResponse

from UserApp.models import *
from .models import *
from AgentApp.models import *
from .form import AdminLoginForm, AdminSignupForm


def welcome_admin(request):
    return render(request, 'admin.html')


def admin_login(request):
    form = AdminLoginForm()
    forms = AdminSignupForm()

    if request.method == 'POST':

        if 'hidden_field' in request.POST and request.POST['hidden_field'] == 'login':

            email = request.POST['email']
            password = request.POST['password']
            admin = AdminModel.objects.filter(email=email, password=password)
            if admin:

                return redirect('welcome_admin')
            else:
                return redirect('admin_login')

        elif 'hidden_fields' in request.POST and request.POST['hidden_fields'] == 'signup':

            email = request.POST['email']

            existing_admin = AdminModel.objects.filter(email=email).exists()

            if existing_admin:
                message = "Account is already registered"
                return HttpResponse(f'<script>alert("{message}"); window.location.href = "/admin/"</script>')

            else:

                # Create a new AdminModel instance

                new_admin = AdminModel(

                    admin_name=request.POST['name'],

                    reg_no=request.POST['reg_number'],

                    email=email,

                    password=request.POST['password']

                )

                new_admin.save()

                return redirect('admin_login')

    return render(request, 'admin_login.html', {'form': form, 'forms': forms})


def agent_remove(request):
    agents = AgentModel.objects.all()
    agent_data = []
    for agent in agents:
        agent_info = {
            'agent_id': agent.agent_id,
            'agent_name': agent.agent_name,
            'agent_email': agent.agent_email,
            'agent_phone': agent.agent_phone,
            'created_at': agent.created_at,
            'license': agent.license
        }
        agent_data.append(agent_info)
    return render(request, 'agent_remove.html', {'agent_data': agent_data})


def agent_remove_fun(request,agent_id):
    agent = AgentModel.objects.filter(agent_id=agent_id).first()
    agent.delete()
    message = "Agent Successfully Removed"
    return HttpResponse(f'<script>alert("{message}"); window.location.href = "/agent_remove/"</script>')


def user_remove(request):
    users = UserModel.objects.all()
    user_data = []
    for user in users:
        agent_info = {
            'user_id': user.user_id,
            'user_name': user.user_name,
            'user_email': user.user_email,
            'created_at': user.created_at,
        }
        user_data.append(agent_info)
    return render(request, 'remove_user.html', {'user_data': user_data})

def user_remove_fun(request,user_id):
    user = UserModel.objects.filter(user_id=user_id).first()
    user.delete()
    message = "User Successfully Removed"
    return HttpResponse(f'<script>alert("{message}"); window.location.href = "/user_remove/"</script>')

