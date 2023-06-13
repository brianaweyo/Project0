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
    
class Trainers(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


    
    def __str__(self):
        return self.user.username
    
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


#Schedule model
class Events(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True,blank=True)

    class Meta:
        verbose_name ="Events"
        verbose_name_plural = "Events"
        db_table = "events"

# class Booking(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     event = models.ForeignKey('events.Event', on_delete=models.CASCADE)
#     name = models.CharField(max_length=100)
#     trainer = models.CharField(max_length=100)
#     start = models.DateTimeField()
#     end = models.DateTimeField()

#     def __str__(self):
#         return self.name

class Trainers(models.Model):
        user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE, primary_key=True)
        @property
        def first_name(self):
            return self.user.first_name

        @property
        def phone_number(self):
            return self.user.phone_number
        class Meta:
             verbose_name ="Trainers"    #prevents the addition of (S) in the admin section
             verbose_name_plural = "Trainers"
             db_table = "trainers"
       
    
          
class Service(models.Model):
    service_name = models.CharField(max_length=60, null=False )
    description = models.TextField(null=False)
    cost = models.FloatField(null=False)
