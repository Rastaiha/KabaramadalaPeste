# Generated by Django 3.0.4 on 2020-09-09 12:11

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0022_team_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]