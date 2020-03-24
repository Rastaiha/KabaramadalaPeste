from django.db import models
from django.contrib.auth.models import AbstractUser


from enum import Enum

# Create your models here.


class Gender(Enum):
    Man = 'Man'
    Woman = 'Woman'


class Member(AbstractUser):
    is_participant = models.BooleanField(default=True)

    class Meta:
        db_table = "auth_user"

    def __str__(self):
        return self.username


class Participant(models.Model):
    member = models.OneToOneField(Member, related_name='participant', on_delete=models.CASCADE)
    school = models.CharField(max_length=50)
    city = models.CharField(max_length=20)
    document = models.ImageField(upload_to='documents/')
    gender = models.CharField(max_length=10, default=Gender.Man, choices=[(tag.value, tag.name) for tag in Gender])
    phone_number = models.CharField(max_length=12, blank=True, null=True)
    is_activated = models.BooleanField(default=False)
    is_document_verified = models.BooleanField(default=False)

    def __str__(self):
        return str(self.member)


class Judge(models.Model):
    member = models.OneToOneField(Member, related_name='judge', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.member)


class PaymentAttempt(models.Model):
    participant = models.ForeignKey(Participant, related_name='payment_attempts', on_delete=models.CASCADE)
    red_id = models.CharField(max_length=20, null=True, blank=True)
    status = models.CharField(max_length=20, null=True, blank=True)
    authority = models.CharField(max_length=50)
    desc = models.CharField(max_length=50)
    request_datetime = models.DateTimeField(auto_now_add=True)
    verify_datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'PaymentAttempt object (' + str(self.pk) + ') (' + str(self.participant) + ')'
