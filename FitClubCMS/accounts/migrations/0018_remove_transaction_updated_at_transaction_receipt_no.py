# Generated by Django 4.2.1 on 2023-07-05 12:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0017_email"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="transaction",
            name="updated_at",
        ),
        migrations.AddField(
            model_name="transaction",
            name="receipt_no",
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]
