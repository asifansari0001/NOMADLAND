from . import views
from django.urls import path

urlpatterns = [

    path('package_payment/', views.package_payment, name='package_payment'),
path('payment_success/', views.payment_success, name='payment_success')


]
