# Generated by Django 3.0.4 on 2020-03-22 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_participant_phone_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='is_activated',
            field=models.BooleanField(default=False),
        ),
    ]
