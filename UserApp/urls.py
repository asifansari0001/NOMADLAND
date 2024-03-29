from . import views
from django.urls import path

urlpatterns = [

    path('', views.home, name='home'),
    path('user/', views.user, name='booking'),
    path('about/', views.about, name='about'),
    path('review/', views.review, name='review'),
    path('login/', views.login, name='login'),
    path('offer/', views.offer, name='offer'),
    path('package/', views.package, name='package'),
    path('package_filter/', views.package_filter, name='package_filter'),
    path('package_preview/', views.package_preview, name='package_preview'),
    path('package_payment/', views.package_payment, name='package_payment'),
    path('logout/', views.logout, name='logout')

]
