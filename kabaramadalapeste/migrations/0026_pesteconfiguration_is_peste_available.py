# Generated by Django 3.0.4 on 2020-03-27 21:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kabaramadalapeste', '0025_auto_20200327_1942'),
    ]

    operations = [
        migrations.AddField(
            model_name='pesteconfiguration',
            name='is_peste_available',
            field=models.BooleanField(default=False),
        ),
    ]
