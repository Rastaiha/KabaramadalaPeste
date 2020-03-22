from django.db import models
from django.contrib.auth.models import AbstractUser


from enum import Enum

# Create your models here.


class Gender(Enum):
    Man = 'Man'
    Woman = 'Woman'


class Member(AbstractUser):
    is_participant = models.BooleanField(default=True)

    def __str__(self):
        return self.first_name


class Participant(models.Model):
    member = models.OneToOneField(Member, related_name='participant', on_delete=models.CASCADE)
    school = models.CharField(max_length=50)
    city = models.CharField(max_length=20)
    document = models.ImageField(upload_to='documents/')
    gender = models.CharField(max_length=10, default=Gender.Man, choices=[(tag.value, tag.name) for tag in Gender])
    phone_number = models.CharField(max_length=12, blank=True, null=True)

    def __str__(self):
        return str(self.member)


class Judge(models.Model):
    member = models.OneToOneField(Member, related_name='judge', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.member)
