# Generated by Django 3.2.19 on 2023-05-16 18:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0004_auto_20230516_0122'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='cash_available',
        ),
    ]
