from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage, send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.html import format_html

from .models import (
    Booking,
    Email,
    Events,
    Package,
    Profile,
    Service,
    Sessions,
    Trainers,
    Transaction,
)

# Register your models here.


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "last_name",
        "sex",
        "phone_no",
        "photo",
        "package",
        "address",
    ]
    raw_id_fields = ["user"]


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ["service_name", "description", "cost"]


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = [
        "package_id",
        "package_name",
        "description",
        "price",
        "created_at",
        "updated_at",
        "package_photo",
    ]
    ordering = ["created_at"]


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        "transaction_id",
        "amount",
        "package",
        "user",
        "sender_no",
        "transaction_date",
        "status",
        "created_at",
        "receipt_no",
    ]


@admin.register(Events)
class EventsAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "start", "end", "trainer"]
    ordering = ["start"]


@admin.register(Trainers)
class TrainersAdmin(admin.ModelAdmin):
    list_display = ["trainer_id", "user", "first_name", "last_name", "phone_number"]


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        "booking_id",
        "user",
        "name",
        "start",
        "end",
        "trainer",
        "book_time",
    ]


class ReplyForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={"rows": 5, "cols": 60}))


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ["sender_email", "recipient", "subject", "content", "sent_date"]
    actions = ["reply_to_email"]

    def sender_email(self, obj):
        return obj.sender.email

    sender_email.short_description = "Sender Email"

    def reply_to_email(self, request, queryset):
        # Assuming queryset contains only one Email object, modify the code accordingly if needed
        email = queryset.first()

        # Prepare the redirect URL

        redirect_url = f"https://mail.google.com/mail/?view=cm&fs=1&to={email.sender.email}&su={email.subject}&body="

        # Redirect to the Gmail compose page with pre-filled fields
        return redirect(redirect_url)

    reply_to_email.short_description = "Reply to selected email(s)"


@admin.register(Sessions)
class SessionsAdmin(admin.ModelAdmin):
    list_display = ["session_name", "start", "end", "trainer"]
