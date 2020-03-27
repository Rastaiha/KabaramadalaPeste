# Generated by Django 3.0.4 on 2020-03-25 13:23

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import kabaramadalapeste.models


class Migration(migrations.Migration):

    dependencies = [
        ('kabaramadalapeste', '0014_participantislandstatus_is_treasure_visible'),
    ]

    operations = [
        migrations.AddField(
            model_name='judgeablequestion',
            name='upload_required',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='shortanswerquestion',
            name='correct_answer',
            field=models.CharField(max_length=100),
        ),
        migrations.CreateModel(
            name='ShortAnswerSubmit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('submitted_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('submit_status', models.CharField(choices=[('Pending', 'Pending'), ('Correct', 'Correct'), ('Wrong', 'Wrong')], default=kabaramadalapeste.models.BaseSubmit.SubmitStatus['Pending'], max_length=10)),
                ('judged_at', models.DateTimeField(null=True)),
                ('submitted_answer', models.CharField(max_length=100)),
                ('pis', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='shortanswersubmit', to='kabaramadalapeste.ParticipantIslandStatus')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='JudgeableSubmit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('submitted_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('submit_status', models.CharField(choices=[('Pending', 'Pending'), ('Correct', 'Correct'), ('Wrong', 'Wrong')], default=kabaramadalapeste.models.BaseSubmit.SubmitStatus['Pending'], max_length=10)),
                ('judged_at', models.DateTimeField(null=True)),
                ('submitted_answer', models.FileField(null=True, upload_to='answers/')),
                ('judge_note', models.CharField(blank=True, max_length=200, null=True)),
                ('pis', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='judgeablesubmit', to='kabaramadalapeste.ParticipantIslandStatus')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]