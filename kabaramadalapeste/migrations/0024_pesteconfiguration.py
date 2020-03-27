# Generated by Django 3.0.4 on 2020-03-27 06:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kabaramadalapeste', '0023_bully'),
    ]

    operations = [
        migrations.CreateModel(
            name='PesteConfiguration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('island_spade_cost', models.IntegerField(default=15000)),
                ('peste_reward', models.IntegerField(default=30000)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
