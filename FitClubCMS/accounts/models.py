from django.db import models
from django.conf import settings


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
    photo = models.ImageField(upload_to='users/%Y/%m/%d/', blank=True)

    def __str__(self):
        return f'Profile of {self.user.username}'

