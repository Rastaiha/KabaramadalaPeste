# Generated by Django 3.0.4 on 2020-03-24 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homepage', '0003_teammember_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteconfiguration',
            name='is_signup_enabled',
            field=models.BooleanField(default=True),
        ),
    ]
