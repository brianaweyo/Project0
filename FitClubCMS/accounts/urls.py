from django.urls import path, include
from django.contrib.auth import views as auth_views 
from . import views


urlpatterns = [
     path('', include('django.contrib.auth.urls')),
     path('', views.landing_page, name='home'),
     path('dashboard/', views.dashboard, name='dashboard'),
     path('register/', views.register, name='register'),
     path('edit/', views.edit, name='edit'),
     path('services/', views.services, name='services'),
     path('packages/', views.packages, name='packages'),
     path('my_package/', views.my_package, name='my_package'),
     path('trainers/', views.trainers, name='trainers'),
     path('schedule/', views.schedule, name='schedule'),
     path('all_events/', views.all_events, name='all_events'),
     path('add_event/', views.add_event, name='add_event'),
     path('update_event/', views.update_event, name='update_event'),
     path('remove_event/', views.remove_event, name='remove_event'),
     path('payment_index/', views.payment_index, name='payment_index'),
     path('payment_form/', views.payment_form, name='payment_form'),
     path('payment_success_page/', views.payment_success_page, name='payment_success'),
     path('sessions_list/', views.sessions_list, name='sessions_list'),
     path('add_session/', views.add_session, name='add_session'),
     path('book_session/', views.book_session, name='book_session'),
     path('my_bookings/', views.my_bookings, name='my_bookings'),
     path('cancel_booking/', views.cancel_booking, name='cancel_booking'),
     path('payment_history/', views.payment_history, name='payment_history'),
]