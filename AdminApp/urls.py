from . import views
from django.urls import path

urlpatterns = [

    path('admin/', views.admin_login, name='admin_login'),
    path('welcome_admin/', views.welcome_admin, name='welcome_admin'),



]
