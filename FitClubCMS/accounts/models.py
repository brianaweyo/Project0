from django.db import models
from django.conf import settings
from datetime import datetime


class Profile(models.Model):
    CHOICES = [
        ('option1','Male'),
        ('option2','Female')
    ]
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    
    last_name = models.CharField(max_length=50)
    phone_no = models.CharField(max_length=50)
    sex = models.CharField(max_length=10, choices=CHOICES)
    date_of_birth= models.DateField(blank=True, null=True)
    package = models.ForeignKey('Package', on_delete=models.SET_NULL, null=True)
    photo = models.ImageField(upload_to='users/%Y/%m/%d/', blank=True)

    def __str__(self):
        return f'Profile of {self.user.username}'

class Package(models.Model):
    package_id = models.AutoField(primary_key=True)
    package_name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.package_name
    
class Transaction(models.Model):
    transaction_id = models.AutoField(primary_key=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    package = models.ForeignKey('Package', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    transaction_date = models.DateField()
    status = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sender_no = models.CharField(max_length=15)
    recipient_no = models.CharField(max_length=15)

    def __str__(self):
        return f"Transaction {self.transaction_id}"
    
    def save(self, *args, **kwargs):
        current_date = datetime.now().date()
        
        if self.transaction_date > current_date:
            self.status = "pending"
        elif self.transaction_date == current_date:
            self.status = "in progress"
        else:
            self.status = "complete"
        
        super().save(*args, **kwargs)


class Service(models.Model):
    service_name = models.CharField(max_length=60, null=False )
    description = models.TextField(null=False)
    cost = models.FloatField(null=False)
