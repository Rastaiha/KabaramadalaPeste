# Generated by Django 3.0.4 on 2020-03-30 12:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0017_participant_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='stat_image',
            field=models.ImageField(default='stats/base_stat.png', null=True, upload_to='stats/'),
        ),
    ]
