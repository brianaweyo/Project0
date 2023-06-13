from django.urls import path, include
from django.contrib.auth import views as auth_views 
from . import views


urlpatterns = [
    # path('login/', auth_views.LoginView.as_view(), name='login'),
    # path('login/', auth_views.LogoutView.as_view(), name='logout'),
    # path('password-change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    # path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    # path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    # path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    # path('password-reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # path('password-reset-/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
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
     path('index/', views.index, name='index'),
     path('payment_form/', views.payment_form, name='payment_form'),
     path('payment_success_page/', views.payment_success_page, name='payment_success'),
     path('sessions_list/', views.sessions_list, name='sessions_list'),
    #  path('book_session/', views.book_session, name='book_session'),
]