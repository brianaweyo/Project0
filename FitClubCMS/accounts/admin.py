from django.contrib import admin

from .models import Profile, Service, Package, Transaction

# Register your models here.

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display =['user', 'last_name', 'sex', 'phone_no', 'photo']
    raw_id_fields=['user']


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['service_name', 'description', 'cost']

@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ['package_id','package_name', 'description', 'price', 'created_at', 'updated_at']
    ordering = ['created_at']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_id','amount', 'package','user', 'sender_no', 'recipient_no','transaction_date','status', 'created_at','updated_at'] 