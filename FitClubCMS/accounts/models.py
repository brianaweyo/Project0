from datetime import date, datetime, timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver



class Package(models.Model):
    package_id = models.AutoField(primary_key=True)
    package_name = models.CharField(max_length=255, default=None)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    package_photo = models.ImageField(upload_to="site/%Y/%m/%d/", blank=True)

    def __str__(self):
        return self.package_name


class Profile(models.Model):
    CHOICES = [("Male", "Male"), ("Female", "Female")]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    last_name = models.CharField(max_length=50)
    phone_no = models.CharField(max_length=50)
    address = models.CharField(max_length=256, null=True)
    sex = models.CharField(max_length=10, choices=CHOICES)
    date_of_birth = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to="users/%Y/%m/%d/", blank=True)
    package = models.ForeignKey(
        "Package",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def clean(self):
        if self.date_of_birth is not None:
            today = date.today()
            min_date = today - timedelta(
                days=365 * 10
            )  # Minimum date resulting in an age of 10 years
            if self.date_of_birth > min_date:
                raise ValidationError("Your age must at least be 10 year!")

    def __str__(self):
        return f"Profile of {self.user.username}"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_save_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


class Transaction(models.Model):
    transaction_id = models.AutoField(primary_key=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    package = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    transaction_date = models.DateTimeField()
    status = models.CharField(max_length=255)
    receipt_no = models.CharField(max_length=256, blank=True, null=True)
    sender_no = models.CharField(max_length=15)

    def __str__(self):
        return f"Transaction {self.transaction_id}"


class Trainers(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    trainer_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        return self.first_name

    class Meta:
        verbose_name = "Trainers"  # prevents the addition of (S) in the admin section
        verbose_name_plural = "Trainers"
        db_table = "trainers"


# Schedule model
class Events(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)
    trainer = models.ForeignKey(
        Trainers, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        verbose_name = "Events"
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
        verbose_name = "Session"
        verbose_name_plural = "Sessions"
        db_table = "sessions"


class Email(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_emails"
    )
    recipient = models.EmailField(default=settings.EMAIL_HOST_USER)
    subject = models.CharField(max_length=255)
    content = models.TextField()
    sent_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From: {self.sender.email} | To: {self.recipient} | Subject: {self.subject}"  # return self.subject
    


