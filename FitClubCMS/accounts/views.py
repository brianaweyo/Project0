import email
import functools
import imaplib
import json
from datetime import date, datetime, timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core import serializers
from django.core.mail import send_mail
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_POST
from django_daraja.mpesa.core import MpesaClient

from .forms import (
    LoginForm,
    ProfileEditForm,
    ReplyEmailForm,
    SessionForm,
    UserEditForm,
    UserRegistrationForm,
)
from .models import (
    Booking,
    Email,
    Events,
    Package,
    Profile,
    Service,
    Trainers,
    Transaction,
)


def landing_page(request):
    return render(request, "accounts/pages/landingpage.html")


from django.shortcuts import redirect
from django.urls import reverse


def user_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(
                request, username=cd["username"], password=cd["password"]
            )
            if user is not None:
                if user.is_active:
                    login(request, user)
                else:
                    return HttpResponse("Disabled Account")
            else:
                return HttpResponse("Invalid Login")
    else:
        form = LoginForm()
    return render(request, "accounts/login.html", {"form": form})


def register(request):
    if request.method == "POST":
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # Create a new user but avoid saving it yet
            new_user = user_form.save(commit=False)
            # set the chosen password
            new_user.set_password(user_form.cleaned_data["password"])
            # save user object
            new_user.save()
            # create the user Profile object associated with new created user
            Profile.objects.create(user=new_user)
            return render(
                request, "accounts/register_done.html", {"new_user": new_user}
            )
    else:
        user_form = UserRegistrationForm()
    return render(request, "accounts/register.html", {"user_form": user_form})


@login_required
def edit(request):
    if request.method == "POST":
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(
            instance=request.user.profile, data=request.POST, files=request.FILES
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully")
        else:
            messages.error(request, "Error updating your profile")
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)

    return render(
        request,
        "accounts/edit.html",
        {"user_form": user_form, "profile_form": profile_form},
    )


@login_required
def payment_form(request):
    # Retrieve the package data from the database or any other source
    package_id = request.GET.get("package_id")
    package = get_object_or_404(Package, pk=package_id)

    context = {"package": package}
    return render(request, "accounts/pages/payment_form.html", context)


from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
@login_required
def payment_index(request):

    if request.method == "POST":
        # Retrieve the form data
        amount = float(request.POST.get("amount"))
        amount = round(
            amount
        )  # Convert to integer by rounding to the nearest whole number
        phone_number = request.POST.get("phone_no")
        package_name = request.POST.get("package_name")

        # storing the two in order to be accessed from the response in payment_result
        request.session["session_package_name"] = package_name
        request.session["username"] = request.user.username

        request.session.save()  # Save the session

        package_retrieved_name = request.session.get("session_package_name")
        username = request.session.get("username")

        print(package_name)
        print(username)

        

        cl = MpesaClient()
        account_reference = "reference"
        transaction_desc = "Description"
        callback_url = "https://ed51-105-160-111-11.ngrok-free.app/payment_result/"
        response = cl.stk_push(
            phone_number, amount, account_reference, transaction_desc, callback_url
        )

    return HttpResponse(response)


@csrf_exempt
def payment_result(request):
    print("callback returned")
    cl = MpesaClient()
    if request.method == "POST":
        result = cl.parse_stk_result(request.body)
        if result["ResultCode"] == 0:
            amount = result.get("Amount")
            receipt_no = result.get("MpesaReceiptNumber")
            transaction_date = result.get("TransactionDate")
            phone_number = result.get("PhoneNumber")

            print(amount)
            print(receipt_no)
            print(transaction_date)
            print(phone_number)


            
            transaction_date_str = str(transaction_date)
            transaction_date = datetime.strptime(transaction_date_str, "%Y%m%d%H%M%S")
            print(transaction_date)
           

            # Retrieve the package_name and username from the session
            package_name = request.session.get("session_package_name")
            username = request.session.get("username")

            print(package_name)
            print(username)


    return HttpResponse("okay")


 


def payment_success_page(request):
    return render(request, "accounts/pages/payment_success.html")


@login_required
def dashboard(request):
    context = {}
    if request.user.is_authenticated:
        context["date_today"] = date.today()
        context["current_time"] = datetime.now().strftime("%H:%M:%S")

        current_datetime = timezone.now()

        total_bookings = Booking.objects.filter(user=request.user).count()
        context["total_bookings"] = total_bookings

        # Find the next session booking that hasn't started yet
        next_session = (
            Booking.objects.filter(
                user=request.user,
                start__gt=current_datetime,
            )
            .order_by("start")
            .first()
        )

        # Get the start time and day of the next session
        if next_session:
            next_session_start_str = next_session.start
            next_session_start = datetime.strptime(
                next_session_start_str, "%Y-%m-%d %H:%M:%S"
            )
            next_session_date = next_session_start.date()
            next_session_time = next_session_start.strftime("%I:%M %p")

            if next_session_date == date.today():
                day_indicator = "Today"
            else:
                day_indicator = day_indicator = next_session_date.strftime(
                    "%A"
                )  # Format the day of the week
            context["next_session_start"] = f"{day_indicator} at {next_session_time}"
        else:
            context["next_session_start"] = "No upcoming sessions"

        # Retrieve the package associated with the logged-in user
        try:
            profile = Profile.objects.get(user=request.user)
            package = profile.package
            context["profile"] = profile
            context["user"] = request.user
            context["package_name"] = package.package_name

        except Profile.DoesNotExist:
            context["package_name"] = None

        # Retrieve the account status and last login information
        user = User.objects.get(pk=request.user.pk)
        context["account_status"] = user.is_active
        context["last_login"] = user.last_login
        context["date_joined"] = user.date_joined

        # Retrieve the total count of transactions made by the logged-in user
        total_transactions = Transaction.objects.filter(user=request.user).count()
        context["total_transactions"] = total_transactions

        # Retrieve the most recent transaction associated with the logged-in user
        recent_transaction = (
            Transaction.objects.filter(user=request.user)
            .order_by("-transaction_date")
            .first()
        )
        if recent_transaction:
            transaction_date = recent_transaction.transaction_date
            expiry_date = transaction_date + timedelta(days=30)
            context["expiry_date"] = expiry_date.strftime("%Y-%m-%d")
        else:
            context["expiry_date"] = None

        try:
            profile = Profile.objects.get(user=request.user)
            photo_url = profile.photo.url
            context["photo_url"] = photo_url
        except Profile.DoesNotExist:
            context["photo_url"] = None

    return render(request, "accounts/pages/dashboard.html", context)


@login_required
def payment_history(request):
    transactions = Transaction.objects.filter(user=request.user).order_by("-created_at")
    return render(
        request, "accounts/pages/payment_records.html", {"transactions": transactions}
    )


@login_required
def packages(request):
    packages = Package.objects.all()
    context = {"packages": packages}
    return render(request, "accounts/pages/packages.html", context)


@login_required
def my_package(request):
    profile = Profile.objects.get(user=request.user)

    package = profile.package
    context = {"package": package}
    return render(request, "accounts/pages/my_package.html", context)


def trainers(request):
    return render(request, "accounts/pages/trainers.html")


def schedule(request):
    all_events = Events.objects.all()
    context = {
        "events": all_events,
    }
    return render(request, "accounts/pages/schedule.html", context)


def all_events(request):
    all_events = Events.objects.all()
    out = []
    for event in all_events:
        out.append(
            {
                "title": event.name,
                "id": event.id,
                "start": event.start.strftime("%Y/%m/%d,  %H:%M"),
                "end": event.end.strftime("%Y/%m/%d,  %H:%M"),
            }
        )
    return JsonResponse(out, safe=False)


def add_event(request):
    start = request.GET.get("start", None)
    end = request.GET.get("end", None)
    title = request.GET.get("title", None)
    event = Events(name=str(title), start=start, end=end)
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


def remove_event(request):
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
        return redirect("success")
    else:
        # Render the form again with the errors.
        return render(request, "accounts/pages/trainer_assignment.html")


@login_required
def sessions_list(request):
    current_time = timezone.now()
    events = Events.objects.filter(start__gt=current_time)[:8]

    context = {"events": events}
    return render(request, "accounts/pages/booking_form.html", context)


@login_required
def book_session(request):
    if request.method == "POST":
        event_name = request.POST.get("event_name")
        event_start = request.POST.get("event_start")
        event_end = request.POST.get("event_end")
        event_trainer = request.POST.get("event_trainer")

        # Get the User instance of the logged-in user
        user = User.objects.get(username=request.user.username)

        # Check if a booking with the same details already exists
        existing_booking = Booking.objects.filter(
            user=user,
            name=event_name,
            start=event_start,
            end=event_end,
            trainer=event_trainer,
        ).exists()

        if existing_booking:
            messages.error(request, "You have already booked this session!")

        else:
            booking = Booking.objects.create(
                user=user,
                name=event_name,
                start=event_start,
                end=event_end,
                trainer=event_trainer,
            )
            messages.success(request, "Session booked successfully.")

        return redirect("sessions_list")

    return render("sessions_list")


@login_required
def my_bookings(request):
    user = request.user
    current_time = timezone.now()
    bookings = Booking.objects.filter(user=user, start__gt=current_time).values(
        "booking_id", "name", "start"
    )

    data = {
        "bookings": list(bookings),
    }

    return JsonResponse(data)


from django.http import JsonResponse


@login_required
def cancel_booking(request, booking_id):
    if request.method == "POST":
        try:
            booking = Booking.objects.get(
                booking_id=booking_id
            )  # Retrieve the booking from the database
            booking.delete()  # Delete the booking
            return JsonResponse({"success": True})  # Return a success response
        except Booking.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "Booking not found"}
            )  # Return an error response if the booking is not found
    else:
        return JsonResponse({"success": False, "error": "Invalid request method"})
    # if request.method == "POST":
    #     booking_id = request.POST.get(
    #         "bookingId"
    #     )  # Retrieve the booking ID from the POST data
    #     try:
    #         booking = Booking.objects.get(
    #             booking_id=booking_id
    #         )  # Retrieve the booking from the database
    #         booking.delete()  # Delete the booking
    #         return JsonResponse({"success": True})  # Return a success response
    #     except Booking.DoesNotExist:
    #         return JsonResponse(
    #             {"success": False, "error": "Booking not found"}
    #         )  # Return an error response if the booking is not found
    # else:
    #     return JsonResponse(
    #         {"success": False, "error": "Invalid request method"}
    #     )  # Return an error response for other request methods


@login_required
def send_email(request):
    if request.method == "POST":
        subject = request.POST.get("subject")
        content = request.POST.get("content")
        recipient = settings.EMAIL_HOST_USER
        sender_email = request.user.email

        sender = User.objects.get(email=sender_email)  # Get the User instance

        send_mail(
            subject=subject,
            message=content,
            from_email=sender,
            recipient_list=[recipient],
            fail_silently=False,
        )

        if subject:
            email = Email(
                subject=subject, content=content, recipient=recipient, sender=sender
            )
            email.save()
            messages.success(request, "Email sent successfully.")
        else:
            messages.error(request, "Subject or Content cannot be empty.")

    return redirect("dashboard")


@login_required
def inbox(request):
    # Assuming the logged-in user's email address is stored in the 'email' field
    email = request.user.email

    # Query the database to get the count of emails sent to the logged-in user
    total_notifications = Email.objects.filter(recipient=email).count()

    context = {"total_notifications": total_notifications}

    return render(request, "inbox.html", context)


def services(request):
    data = Service.objects.all()
    serialized_data = serializers.serialize("json", data)
    return JsonResponse(serialized_data, safe=False)
