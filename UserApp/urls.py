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
    path('package_preview/<int:package_id>/', views.package_preview, name='package_preview'),
    path('profile/', views.profile, name='profile'),
    path('add_wishlist/<int:package_id>/', views.add_wishlist, name='add_wishlist'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('remove_from_wishlist/<int:package_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('package_review/<int:package_id>/', views.package_review, name='feedback_form'),
    path('submit_feedback/', views.submit_feedback, name='submit_feedback'),
    path('logout/', views.logout, name='logout'),
    path('hotel_select/<int:package_split_id>/', views.hotel_select, name='hotel_select'),
    path('booking_user/', views.booking_user, name='booking_user'),
    path('history_booking/',views.history_booking, name='history_booking'),

]
