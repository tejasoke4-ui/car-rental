"""
URL configuration for cars project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('contact/',views.contact, name='contact'),
    path('cardetail/<int:car_id>/',views.cardetail, name='cardetail'),
    path('fleet/',views.fleet, name='fleet'),
    path('about/',views.about, name='about'),
    path('bookings/',views.bookings_view, name='bookings'),
    path('register/',views.register_view,name='register'),
    path('profile/',views.profile,name='profile'),
    path('mybookings/',views.mybookings,name='mybookings'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('login/',views.login_view,name='login'),
    path('logout/',views.logout_view,name='logout'),
    path('bookings/new/', views.new_booking_view, name='new_booking'),
    path('bookings/<int:booking_id>/view/', views.view_booking, name='view_booking'),
    path('bookings/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('users/', views.users_view, name='users'),

    # Admin URLs (Custom Admin Panel at /panel/)
    path('panel/', views.admin_login, name='admin_login'),
    path('panel/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('panel/cars/', views.admin_cars, name='admin_cars'),
    path('panel/cars/add/', views.admin_car_add, name='admin_car_add'),
    path('panel/cars/<int:car_id>/edit/', views.admin_car_edit, name='admin_car_edit'),
    path('panel/cars/<int:car_id>/delete/', views.admin_car_delete, name='admin_car_delete'),
    path('panel/bookings/', views.admin_bookings, name='admin_bookings'),
    path('panel/bookings/<int:booking_id>/update/', views.admin_booking_update, name='admin_booking_update'),
    path('panel/users/', views.admin_users, name='admin_users'),
    path('panel/users/<int:user_id>/delete/', views.admin_user_delete, name='admin_user_delete'),

]
urlpatterns=urlpatterns+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

