from django_daraja.mpesa.core import MpesaClient
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .forms import LoginForm, UserRegistrationForm, UserEditForm,ProfileEditForm, SessionForm
from .models import Profile, Service, Events, Package, Trainers, Booking, Transaction
from django.core import serializers
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from datetime import datetime, date, timedelta
from django.db import IntegrityError
import json






def landing_page(request):
    return render(request, 'accounts/pages/landingpage.html')



def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request,
                                username = cd['username'],
                                password = cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated successfully')
                else:
                    return HttpResponse('Disabled Account')
            else:
                return HttpResponse('Invalid Login')
    else:
            form = LoginForm()
    return render(request, 'accounts/login.html', {'form':form})


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            #Create a new user but avoid saving it yet
            new_user =  user_form.save(commit=False)
            #set the chosen password
            new_user.set_password(
                user_form.cleaned_data['password'])
            #save user object
            new_user.save()
            #create the user Profile object associated with new created user
            Profile.objects.create(user=new_user)
            return render(request,
                          'accounts/register_done.html',{'new_user':new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request,
                      'accounts/register.html',{'user_form': user_form})

@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile, data=request.POST, files=request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully')
        else:
            messages.error(request, 'Error updating your profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)

    return render(request,
                  'accounts/edit.html',{'user_form': user_form, 
                                        'profile_form':profile_form})
def payment_form(request):
    # Retrieve the package data from the database or any other source
    package_id = request.GET.get('package_id')
    package = get_object_or_404(Package, pk=package_id)
    
    context = {
        'package': package
    }
    return render(request, 'accounts/pages/payment_form.html', context)




def payment_index(request):
    if request.method == 'POST':
        # Retrieve the form data
        amount = float(request.POST.get('amount'))
        amount = round(amount)  # Convert to integer by rounding to the nearest whole number
        phone_number = request.POST.get('phone_no')
        package_name =request.POST.get('package_name')

        cl = MpesaClient()
        account_reference = 'reference'
        transaction_desc = 'Description'
        callback_url = 'https://api.darajambili.com/express-payment'
        response = cl.stk_push(phone_number, amount, account_reference, transaction_desc, callback_url)

        package = Package.objects.get(package_name=package_name)
        transaction = Transaction.objects.create(
        amount=amount,
        package=package,
        user=request.user,  # Assuming you have a logged-in user
        transaction_date=timezone.now().date(),
        # status='Pending',  # Set the initial status as 'Pending'
        sender_no=request.POST.get('phone_no'),  # Assuming you have a 'phone_number' field in your User model
        )
        # return HttpResponse(response)
        return redirect('payment_success')
    
    # If the request method is not POST, you can handle it as desired
    # For example, you can redirect the user to the payment form again
    return redirect('payment_form')

def payment_success_page(request):
    return render(request, 'accounts/pages/payment_success.html')


@login_required 
def dashboard(request):
    context = {}
    if request.user.is_authenticated:
        context['date_today'] = date.today()
        context['current_time'] = datetime.now().strftime('%H:%M:%S')

        current_date = date.today()
        current_time = datetime.now().time()

       
        total_bookings = Booking.objects.filter(user=request.user).count()
        context['total_bookings'] = total_bookings

        # Find the next session booking that hasn't started yet
        next_session = Booking.objects.filter(user=request.user, start__gte=datetime.combine(current_date, current_time)).order_by('start').first()

        # Calculate the countdown time until the next session
        if next_session:
            next_session_start = datetime.strptime(next_session.start, '%Y-%m-%d %H:%M:%S')
            time_diff = next_session_start - datetime.combine(current_date, datetime.min.time())
            countdown = str(time_diff).split('.')[0]  # Extract hours:minutes:seconds
            context['countdown'] = countdown
        
    return render(request, 'accounts/pages/dashboard.html', context)

@login_required 
def packages(request):
    packages = Package.objects.all()
    context = {'packages': packages}
    return render(request, 'accounts/pages/packages.html', context)

@login_required 
def my_package(request):
    profile = Profile.objects.get(user=request.user)

    package = profile.package
    context = {
        'package': package
    }
    return render(request, 'accounts/pages/my_package.html', context)




def trainers(request):
    return render(request, 'accounts/pages/trainers.html')

def schedule(request):
    all_events = Events.objects.all()
    context = {
        "events": all_events,
    }
    return render(request, 'accounts/pages/schedule.html', context)


def all_events(request):
    all_events = Events.objects.all()
    out = []
    for event in all_events:
        out.append({
            'title':event.name,
            'id': event.id,
            'start': event.start.strftime("%Y/%m/%d,  %H:%M"),
            'end': event.end.strftime("%Y/%m/%d,  %H:%M"),
       })
    return JsonResponse(out, safe=False)



def add_event(request):
    start = request.GET.get("start", None)
    end = request.GET.get("end", None)
    title = request.GET.get("title", None)
    event = Events(name = str(title), start=start, end=end)
    event.save()
    data = {}
    return JsonResponse(data)
    
def update_event(request):
    start = request.GET.get("start", None)
    end = request.GET.get("end", None)
    title = request.GET.get("title", None)
    id = request.GET.get("id", None)
    event = Events.objects.get(id=id)
    event.start = start
    event.end = end
    event.name = title
    event.save()
    data = {}
    return JsonResponse(data)

def remove_event (request):
    id = request.GET.get("id", None)
    event = Events.objects.get(id=id)
    event.delete()
    data = {}
    return JsonResponse(data)


def add_session(request):
    form = SessionForm(request.POST)
    if form.is_valid():
        # Save the data from the form to the database.
        sessions = form.save()
        # Redirect the user to the success page.
        return redirect('success')
    else:
        # Render the form again with the errors.
        return render(request, 'accounts/pages/trainer_assignment.html')
        

@login_required
def sessions_list(request):
    current_time = timezone.now()
    events = Events.objects.filter(start__gt=current_time)[:8]
     
    context = {"events": events}
    return render(request, 'accounts/pages/booking_form.html', context)

@login_required  
def book_session(request):
    if request.method == 'POST':
        event_name = request.POST.get('event_name')
        event_start = request.POST.get('event_start')
        event_end = request.POST.get('event_end')
        event_trainer = request.POST.get('event_trainer')


        # Get the User instance of the logged-in user
        user = User.objects.get(username=request.user.username)

        # Check if a booking with the same details already exists
        existing_booking = Booking.objects.filter(
            user=user,
            name=event_name,
            start=event_start,
            end=event_end,
            trainer=event_trainer
        ).exists()

        if existing_booking:
            messages.error(request, 'You have already booked this session!')

        else:
            booking = Booking.objects.create(
            user = user,
            name=event_name,
            start=event_start,
            end=event_end,
            trainer=event_trainer
           )
            messages.success(request, 'Session booked successfully.')
       
        return redirect('sessions_list')

    return render('sessions_list')

@login_required
def my_bookings(request):
    
    user = request.user
    current_time = timezone.now()
    bookings = Booking.objects.filter(user=user, start__gt=current_time).values('booking_id', 'name', 'start')

    data = {
        'bookings': list(bookings),
    }


    return JsonResponse(data)




@require_POST
def cancel_booking(request):
    if request.method == 'POST':
        try:
            booking_id = request.POST.get('bookingId') 

            existing_booking = Booking.objects.filter(
                booking_id = booking_id,
            ).exists()
            
            if existing_booking:
                existing_booking.delete()
                return JsonResponse({'success': True})

            
        except Booking.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Booking not found'})
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Invalid booking ID'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})



def services(request):
    data = Service.objects.all()
    serialized_data = serializers.serialize('json',data)
    return JsonResponse(serialized_data, safe=False)