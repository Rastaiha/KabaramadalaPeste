# Generated by Django 3.0.4 on 2020-03-25 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kabaramadalapeste', '0016_auto_20200325_1335'),
    ]

    operations = [
        migrations.AlterField(
            model_name='judgeablesubmit',
            name='submitted_answer',
            field=models.FileField(blank=True, null=True, upload_to='answers/'),
        ),
    ]
