# Generated by Django 3.0.4 on 2020-03-27 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kabaramadalapeste', '0024_pesteconfiguration'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bully',
            options={'verbose_name_plural': 'Bullies'},
        ),
        migrations.AlterModelOptions(
            name='participantislandstatus',
            options={'verbose_name_plural': 'Participant island statuses'},
        ),
        migrations.AlterField(
            model_name='bandargahconfiguration',
            name='max_interval_investments',
            field=models.IntegerField(default=1000000),
        ),
        migrations.AlterField(
            model_name='bandargahconfiguration',
            name='min_interval_investments',
            field=models.IntegerField(default=300000),
        ),
    ]
