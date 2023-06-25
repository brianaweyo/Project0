from django.db import models
from django.conf import settings
from datetime import datetime



class Package(models.Model):
    package_id = models.AutoField(primary_key=True)
    package_name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    package_photo = models.ImageField(upload_to='site/%Y/%m/%d/', blank=True)
    

    def __str__(self):
        return self.package_name

class Profile(models.Model):
    CHOICES = [
        ('Male','Male'),
        ('Female','Female')
    ]
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    
    last_name = models.CharField(max_length=50)
    phone_no = models.CharField(max_length=50)
    sex = models.CharField(max_length=10, choices=CHOICES)
    date_of_birth= models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='users/%Y/%m/%d/', blank=True)
    package = models.ForeignKey('Package', on_delete=models.SET_NULL, null=True)
  

    def __str__(self):
        return f'Profile of {self.user.username}'


    
class Transaction(models.Model):
    transaction_id = models.AutoField(primary_key=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    package = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    transaction_date = models.DateField()
    status = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sender_no = models.CharField(max_length=15)
   

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

class Trainers(models.Model):
        # trainer_id = models.AutoField(primary_key=True)
        # user = models.OneToOneField(Profile, on_delete=models.CASCADE)
        user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
        trainer_id = models.AutoField(primary_key=True)
        first_name = models.CharField(max_length=100)
        last_name = models.CharField(max_length=100)
        phone_number = models.CharField(max_length=20)

        def __str__(self):
         return self.first_name
        
        class Meta:
             verbose_name ="Trainers"    #prevents the addition of (S) in the admin section
             verbose_name_plural = "Trainers"
             db_table = "trainers"
       


#Schedule model
class Events(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True,blank=True)
    trainer = models.ForeignKey(Trainers, on_delete=models.SET_NULL, null=True, blank=True)
    class Meta:
        verbose_name ="Events"
        verbose_name_plural = "Events"
        db_table = "events"
 
class Booking(models.Model):
    booking_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    start = models.CharField(max_length=20)
    end = models.CharField(max_length=20)
    trainer = models.CharField(max_length=100)
    book_time = models.DateTimeField(auto_now=True)


class Sessions(models.Model):
    session_name = models.CharField(max_length=255)
    start = models.DateTimeField()
    end = models.DateTimeField()
    trainer = models.CharField(max_length=255)

    def __str__(self):
        return self.id
    class Meta:
        verbose_name ="Session"
        verbose_name_plural = "Sessions"
        db_table = "sessions"
          
class Service(models.Model):
    service_name = models.CharField(max_length=60, null=False )
    description = models.TextField(null=False)
    cost = models.FloatField(null=False)
