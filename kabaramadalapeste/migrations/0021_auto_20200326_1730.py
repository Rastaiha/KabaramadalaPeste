# Generated by Django 3.0.4 on 2020-03-26 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kabaramadalapeste', '0020_auto_20200326_1652'),
    ]

    operations = [
        migrations.AddField(
            model_name='participantislandstatus',
            name='did_spade',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='participantislandstatus',
            name='spaded_at',
            field=models.DateTimeField(null=True),
        ),
    ]
