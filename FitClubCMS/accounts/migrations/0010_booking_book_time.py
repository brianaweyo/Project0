# Generated by Django 4.2.1 on 2023-06-16 08:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_alter_booking_end_alter_booking_start'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='book_time',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
