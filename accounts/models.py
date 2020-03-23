from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from kabaramadalapeste import models as game_models


from enum import Enum
import logging
logger = logging.getLogger(__file__)

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
    school = models.CharField(max_length=200)
    city = models.CharField(max_length=40)
    document = models.ImageField(upload_to='documents/')
    gender = models.CharField(max_length=10, default=Gender.Man, choices=[(tag.value, tag.name) for tag in Gender])
    phone_number = models.CharField(max_length=12, blank=True, null=True)
    is_activated = models.BooleanField(default=False)

    currently_at_island = models.ForeignKey('kabaramadalapeste.Island',
                                            on_delete=models.SET_NULL,
                                            related_name="current_participants",
                                            null=True)

    def __str__(self):
        return str(self.member)

    def init_pis(self):
        if game_models.ParticipantIslandStatus.objects.filter(participant=self).count():
            logger.info('Participant currently has some PIS. We cant init again.')
            return
        # TODO: handle random Treasure assignment
        # TODO: handle random question assignment
        for island in game_models.Island.objects.all():
            game_models.ParticipantIslandStatus.objects.create(
                participant=self,
                island=island,
            )

    def move(self, dest_island):
        if self.currently_at_island and not self.currently_at_island.is_neighbor_with(dest_island):
            raise game_models.Island.IslandsNotConnected
        dest_pis = game_models.ParticipantIslandStatus.objects.get(
            participant=self,
            island=dest_island
        )
        dest_pis.did_reach = True
        dest_pis.reached_at = timezone.now()
        self.currently_at_island = dest_island
        dest_pis.save()
        self.save()


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
