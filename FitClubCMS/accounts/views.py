from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, UserRegistrationForm, UserEditForm,ProfileEditForm
from .models import Profile, Service, Events, Package
from django.core import serializers
from django.http import JsonResponse
from django.contrib import messages
import json
from django_daraja.mpesa.core import MpesaClient






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




def index(request):
    if request.method == 'POST':
        # Retrieve the form data
        amount = float(request.POST.get('amount'))
        amount = round(amount)  # Convert to integer by rounding to the nearest whole number
        phone_number = request.POST.get('phone_no')

        cl = MpesaClient()
        account_reference = 'reference'
        transaction_desc = 'Description'
        callback_url = 'https://api.darajambili.com/express-payment'
        response = cl.stk_push(phone_number, amount, account_reference, transaction_desc, callback_url)
        # return HttpResponse(response)
        return redirect('payment_success')
    
    # If the request method is not POST, you can handle it as desired
    # For example, you can redirect the user to the payment form again
    return redirect('payment_form')

def payment_success_page(request):
    return render(request, 'accounts/pages/payment_success.html')


@login_required 
def dashboard(request):
    return render(request, 'accounts/pages/dashboard.html')


def packages(request):
    packages = Package.objects.all()
    context = {'packages': packages}
    return render(request, 'accounts/pages/packages.html', context)

def my_package(request):
    return render(request, 'accounts/pages/my_package.html')

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
            'start': event.start.strftime("%m/%d/%Y,  %H:%M:%S"),
            'END': event.end.strftime("%m/%d/%Y,  %H:%M:%S"),
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




def services(request):
    data = Service.objects.all()
    serialized_data = serializers.serialize('json',data)
    return JsonResponse(serialized_data, safe=False)