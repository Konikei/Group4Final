# Generated by Django 3.2.19 on 2023-05-16 01:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0003_auto_20230516_0107'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customer',
            old_name='fname',
            new_name='name',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='lname',
        ),
    ]
