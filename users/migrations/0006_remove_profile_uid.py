# Generated by Django 5.1.2 on 2025-01-11 16:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_alter_profile_uid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='uid',
        ),
    ]
