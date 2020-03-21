from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class Member(AbstractUser):
    is_participant = models.BooleanField(default=True)


class Participant(models.Model):
    member = models.OneToOneField(Member, related_name='participant', on_delete=models.CASCADE)
    school = models.CharField(max_length=50)
    city = models.CharField(max_length=20)
    document = models.ImageField(upload_to='documents/')


class Judge(models.Model):
    member = models.OneToOneField(Member, related_name='judge', on_delete=models.CASCADE)
