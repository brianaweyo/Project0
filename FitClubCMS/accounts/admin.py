from datetime import datetime, timezone

from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage, send_mail
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from import_export import resources
from import_export.admin import ExportMixin
from import_export.formats import base_formats
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter

from .models import (
    Booking,
    Email,
    Events,
    Package,
    Profile,
    Sessions,
    Trainers,
    Transaction,
)

User = get_user_model()
group_name = "Trainers"
group, created = Group.objects.get_or_create(name=group_name)
group.is_staff = True
group.save()

trainers = Trainers.objects.all()
for trainer in trainers:
    user = trainer.user
    user.is_staff = True
    user.groups.add(group)
    user.save()

# Create the 'Clients' group and add non-staff users to it
clients_group_name = "Clients"
clients_group, created = Group.objects.get_or_create(name=clients_group_name)
clients_group.is_staff = False 
clients_group.save()

non_staff_users = User.objects.filter(is_staff=False)
for user in non_staff_users:
    user.groups.add(clients_group)
    user.save()



class CustomExportMixin(ExportMixin):
    def get_export_filename(self, request, queryset, file_format):
        # Get the current date and time
        current_datetime = timezone.now().strftime("%Y-%m-%d_%H-%M-%S")

        # Get the model name
        model_name = self.model.__name__

        # Set the document title
        document_title = f"{model_name} Report"

        # Get the organization name and logo
        organization_name = (
            "GenZFIT Fitness Center"  # Replace with your organization name
        )
        # organization_logo = "path/to/your/logo.png"  # Replace with the path to your organization logo

        # Render the HTML template for the document header
        document_header = render_to_string(
            "document_header.html",
            {
                "document_title": document_title,
                "organization_name": organization_name,
                # 'organization_logo': organization_logo,
            },
        )

        # Generate the export filename with the appropriate file extension
        filename = f"{document_title}_{current_datetime}.{file_format.get_extension()}"

        # Set the response headers for file download
        response = HttpResponse(content_type=file_format.get_content_type())
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        return response


class ProfileResource(resources.ModelResource):
    class Meta:
        model = Profile


class BookingResource(resources.ModelResource):
    class Meta:
        model = Booking


class TrainersResource(resources.ModelResource):
    class Meta:
        model = Trainers


class PackageResource(resources.ModelResource):
    class Meta:
        model = Package


class EmailResource(resources.ModelResource):
    class Meta:
        model = Email


class EventsResource(resources.ModelResource):
    class Meta:
        model = Events


class SessionsResource(resources.ModelResource):
    class Meta:
        model = Sessions


class CustomUserAdmin(ExportMixin, UserAdmin):
    list_display = [
        "id",
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_superuser",
    ]



admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# filters to enable report generation
class PackageNameFilter(admin.SimpleListFilter):
    title = "Package Name"
    parameter_name = "package_name"

    def lookups(self, request, model_admin):
        packages = Package.objects.values_list("package_name", flat=True).distinct()
        return [(package, package) for package in packages]

    def queryset(self, request, queryset):
        package_name = self.value()
        if package_name:
            queryset = queryset.filter(package_name=package_name)
        return queryset


# Register your models here.
@admin.register(Profile)
class ProfileAdmin(CustomExportMixin, admin.ModelAdmin):
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
    list_filter = ("user", "sex", "package")
    formats = [base_formats.CSV, base_formats.XLSX, base_formats.TSV]
    list_per_page = 7


class PriceRangeFilter(admin.SimpleListFilter):
    title = "Price Range"
    parameter_name = "price_range"

    def lookups(self, request, model_admin):
        return [
            ("1-2", "1-2"),
            ("3-4", "3-4"),
            ("5-10", "5-10"),
            # Add more price ranges as needed
        ]

    def queryset(self, request, queryset):
        price_range = self.value()
        if price_range:
            min_price, max_price = price_range.split("-")
            queryset = queryset.filter(price__gte=min_price, price__lte=max_price)
        return queryset


@admin.register(Package)
class PackageAdmin(ExportMixin, admin.ModelAdmin):
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
    list_filter = (PackageNameFilter, PriceRangeFilter)


@admin.register(Transaction)
class TransactionAdmin(ExportMixin, admin.ModelAdmin):
    list_display = [
        "transaction_id",
        "amount",
        "package",
        "user",
        "sender_no",
        "transaction_date",
        "status",
        "receipt_no",
    ]
    list_per_page = 7

    list_filter = (
        "user",
        "package",
        ("transaction_date", DateRangeFilter),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        # Apply filters based on selected user and transaction date range
        selected_user = request.GET.get("user")
        start_date = request.GET.get("transaction_date__gte")
        end_date = request.GET.get("transaction_date__lte")

        if selected_user:
            queryset = queryset.filter(user__username=selected_user)

        if start_date and end_date:
            queryset = queryset.filter(transaction_date__range=(start_date, end_date))

        return queryset


@admin.register(Events)
class EventsAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ["id", "name", "start", "end", "trainer"]
    ordering = ["start"]
    list_filter = (
        "name",
        "start",
        "trainer",
    )
    list_per_page = 7
    ordering = ["-start"]


@admin.register(Trainers)
class TrainersAdmin(ExportMixin, admin.ModelAdmin):
    list_display = [
        "trainer_id",
        "user",
        "first_name",
        "phone_number",
        "specialization",
        "experience",
    ]
    list_per_page = 7

    def get_list_display(self, request):
        list_display = super().get_list_display(request)
        list_display[5] = "experience_in_years"
        return list_display

    def experience_in_years(self, obj):
        return obj.experience

    experience_in_years.short_description = "Experience (years)"


@admin.register(Booking)
class BookingAdmin(ExportMixin, admin.ModelAdmin):
    list_display = [
        "booking_id",
        "user",
        "name",
        "start",
        "end",
        "trainer",
        "book_time",
    ]
    list_per_page = 7
    list_filter = (
        "user",
        "trainer",
        "name",
    )


class ReplyForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={"rows": 5, "cols": 60}))


@admin.register(Email)
class EmailAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ["sender_email", "recipient", "subject", "content", "sent_date"]
    actions = ["reply_to_email"]
    list_filter = (
        "sender",
        "subject",
        ("sent_date", DateRangeFilter),
    )
    list_per_page = 7

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


# @admin.register(Sessions)
# class SessionsAdmin(ExportMixin, admin.ModelAdmin):
#     list_display = ["session_name", "start", "end", "trainer"]
