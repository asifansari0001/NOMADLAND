from . import views
from django.urls import path

urlpatterns = [

    path('agent_login/', views.agent_login, name='agent_login'),
    path('welcome_agent/', views.welcome_agent, name='welcome_agent'),
    path('agent_manage/', views.agent_manage, name='agent_manage'),
    path('manage_package/', views.manage_package, name='manage_package'),
    path('agent_communication/', views.agent_communication,name='agent_communication'),
    path('agent_offer/', views.agent_offer, name='agent_offer'),
    path('agent_analyticgraph/',views.agent_analyticgraph, name='agent_analyticgraph'),
    path('activities/', views.activities, name='activities'),
    path('hotel_add',views.hotel_add, name='hotel_add')


]
