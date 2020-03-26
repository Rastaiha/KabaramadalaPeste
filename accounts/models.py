from django.db import models, transaction
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils import timezone
from datetime import timedelta
from kabaramadalapeste import models as game_models
from kabaramadalapeste.conf import settings as game_settings
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags, strip_spaces_between_tags


from enum import Enum

from collections import defaultdict

import logging
import random
import re
logger = logging.getLogger(__file__)

# Create your models here.


class Gender(Enum):
    Man = 'Man'
    Woman = 'Woman'


class ParticipantStatus(Enum):
    Pending = 'Pending'
    Verified = 'Verified'
    Rejected = 'Rejected'


class Member(AbstractUser):
    is_participant = models.BooleanField(default=True)

    class Meta:
        db_table = "auth_user"

    def __str__(self):
        return self.username


class Participant(models.Model):
    class CantResetStartIsland(Exception):
        pass

    class ParticipantIsNotOnIsland(Exception):
        pass

    class DidNotAnchored(Exception):
        pass

    class PropertiesAreNotEnough(Exception):
        pass

    class MaximumActiveOffersExceeded(Exception):
        pass

    class MaximumChallengePerDayExceeded(Exception):
        pass

    class BadInput(Exception):
        pass

    member = models.OneToOneField(Member, related_name='participant', on_delete=models.CASCADE)
    school = models.CharField(max_length=200)
    city = models.CharField(max_length=40)
    document = models.ImageField(upload_to='documents/')
    gender = models.CharField(max_length=10, default=Gender.Man, choices=[(tag.value, tag.name) for tag in Gender])
    phone_number = models.CharField(max_length=12, blank=True, null=True)
    is_activated = models.BooleanField(default=False)
    document_status = models.CharField(max_length=30,
                                       default='Pending',
                                       choices=[(tag.value, tag.name) for tag in ParticipantStatus])

    currently_at_island = models.ForeignKey('kabaramadalapeste.Island',
                                            on_delete=models.SET_NULL,
                                            related_name="current_participants",
                                            null=True)

    def __str__(self):
        return str(self.member)

    def get_property(self, property_type):
        if self.properties.filter(property_type__exact=property_type).count() == 0:
            property_item = game_models.ParticipantPropertyItem.objects.create(
                participant=self,
                property_type=property_type,
                amount=0
            )
            property_item.save()
        return self.properties.get(property_type__exact=property_type)

    def get_safe_property(self, property_type):
        if self.properties.filter(property_type__exact=property_type).count() == 0:
            property_item = game_models.ParticipantPropertyItem.objects.create(
                participant=self,
                property_type=property_type,
                amount=0
            )
            property_item.save()
        return self.properties.select_for_update().get(property_type__exact=property_type)

    def reduce_property(self, property_type, amount):
        if amount < 0:
            raise Participant.BadInput
        property_item = self.get_safe_property(property_type)
        if property_item.amount < amount:
            raise Participant.PropertiesAreNotEnough
        property_item.amount = property_item.amount - amount
        property_item.save()

    def reduce_multiple_property(self, property_types, amounts):
        if len(property_types) != len(amounts):
            raise Participant.BadInput
        dic = defaultdict(int)
        for i, property_type in enumerate(property_types):
            if amounts[i] < 0:
                raise Participant.BadInput
            dic[property_type] += amounts[i]
        for property_type in dic:
            if self.get_property(property_type).amount < dic[property_type]:
                raise Participant.PropertiesAreNotEnough
        for property_type in dic:
            self.reduce_property(property_type, dic[property_type])

    def add_property(self, property_type, amount):
        if amount < 0:
            raise Participant.BadInput
        property_item = self.get_safe_property(property_type)
        property_item.amount = property_item.amount + amount
        property_item.save()

    @property
    def sekke(self):
        """
        Warning changes on this property wont be applied if you want to make changes use get_safe_sekke
        """
        return self.get_property(game_settings.GAME_SEKKE)

    def get_safe_sekke(self):
        return self.get_safe_property(game_settings.GAME_SEKKE)

    def today_challenges_opened_count(self):
        today_begin = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_begin + timedelta(days=1)
        return game_models.ParticipantIslandStatus.objects.filter(
            participant=self,
            did_accept_challenge=True,
            challenge_accepted_at__gte=today_begin,
            challenge_accepted_at__lt=today_end,
        ).count()


    def today_challenge_pluses_count(self):
        today_begin = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_begin + timedelta(days=1)
        return game_models.AbilityUsage.objects.filter(
            participant=self,
            ability_type__exact=game_settings.GAME_CHALLENGE_PLUS,
            datetime__gte=today_begin,
            datetime__lt=today_end,
        ).count()

    def can_open_new_challenge(self):
        return self.today_challenges_opened_count() < \
               game_settings.GAME_BASE_CHALLENGE_PER_DAY + self.today_challenge_pluses_count()

    def init_pis(self):
        if game_models.ParticipantIslandStatus.objects.filter(participant=self).count():
            logger.info('Participant currently has some PIS. We cant init again.')
            return
        treasures_shuffled = list(game_models.Treasure.objects.all())
        random.shuffle(treasures_shuffled)
        with transaction.atomic():
            for island in game_models.Island.objects.all():
                pis = game_models.ParticipantIslandStatus.objects.create(
                    participant=self,
                    island=island,
                )
                if island.island_id != game_settings.GAME_BANDARGAH_ISLAND_ID:
                    pis.treasure = treasures_shuffled.pop()
                    pis.save()
                    pis.assign_question()

    def init_properties(self):
        if self.properties.count():
            logger.info('Participant currently has some properties. We cant init again.')
            return
        for property_type, amount in game_settings.GAME_PARTICIPANT_INITIAL_PROPERTIES.items():
            if amount > 0:
                self.properties.create(
                    participant=self,
                    property_type=property_type,
                    amount=amount
                )
            else:
                logger.warning('Property could not be negative we continue setting other properties')

    def set_start_island(self, dest_island):
        if self.currently_at_island:
            raise Participant.CantResetStartIsland
        with transaction.atomic():
            dest_pis = game_models.ParticipantIslandStatus.objects.get(
                participant=self,
                island=dest_island
            )
            dest_pis.currently_in = True
            dest_pis.did_reach = True
            dest_pis.reached_at = timezone.now()
            dest_pis.save()

            self.currently_at_island = dest_island
            self.save()

    def get_current_island(self):
        if not self.currently_at_island:
            raise Participant.ParticipantIsNotOnIsland
        return self.currently_at_island

    def move(self, dest_island):
        if not self.currently_at_island:
            raise Participant.ParticipantIsNotOnIsland
        if not self.currently_at_island.is_neighbor_with(dest_island):
            raise game_models.Island.IslandsNotConnected

        with transaction.atomic():
            active_expresses = game_models.AbilityUsage.objects.filter(
                participant=self,
                ability_type=game_settings.GAME_TRAVEL_EXPRESS,
                is_active=True
            ).all()
            if active_expresses.count() == 0:
                self.reduce_property(game_settings.GAME_SEKKE, game_settings.GAME_MOVE_PRICE)
            else:
                express = active_expresses[0]
                express.is_active = False
                express.save()

            src_pis = game_models.ParticipantIslandStatus.objects.get(
                participant=self,
                island=self.currently_at_island
            )
            src_pis.currently_in = False
            src_pis.currently_anchored = False
            src_pis.save()

            dest_pis = game_models.ParticipantIslandStatus.objects.get(
                participant=self,
                island=dest_island
            )

            dest_pis.currently_in = True
            dest_pis.did_reach = True
            dest_pis.reached_at = timezone.now()
            dest_pis.save()

            self.currently_at_island = dest_island
            self.save()

    def put_anchor_on_current_island(self):
        if not self.currently_at_island:
            raise Participant.ParticipantIsNotOnIsland

        current_pis = game_models.ParticipantIslandStatus.objects.get(
            participant=self,
            island=self.currently_at_island
        )
        with transaction.atomic():
            current_pis.currently_anchored = True
            current_pis.is_treasure_visible = True
            current_pis.last_anchored_at = timezone.now()
            current_pis.save()

            self.reduce_property(game_settings.GAME_SEKKE, game_settings.GAME_PUT_ANCHOR_PRICE)

    def open_treasure_on_current_island(self):
        if not self.currently_at_island:
            raise Participant.ParticipantIsNotOnIsland
        current_pis = game_models.ParticipantIslandStatus.objects.get(
            participant=self,
            island=self.currently_at_island
        )
        if not current_pis.currently_anchored:
            raise Participant.DidNotAnchored
        treasure = current_pis.treasure
        with transaction.atomic():
            for key in treasure.keys.all():
                self.reduce_property(key.key_type, key.amount)
            for reward in treasure.rewards.all():
                self.add_property(reward.reward_type, reward.amount)
            current_pis.did_open_treasure = True
            current_pis.treasure_opened_at = timezone.now()
            current_pis.save()

    def accept_challenge_on_current_island(self):
        if not self.currently_at_island:
            raise Participant.ParticipantIsNotOnIsland
        current_pis = game_models.ParticipantIslandStatus.objects.get(
            participant=self,
            island=self.currently_at_island
        )
        if not current_pis.currently_anchored:
            raise Participant.DidNotAnchored
        if not self.can_open_new_challenge():
            raise Participant.MaximumChallengePerDayExceeded

        current_pis = game_models.ParticipantIslandStatus.objects.get(
            participant=self,
            island=self.currently_at_island
        )
        with transaction.atomic():
            current_pis.did_accept_challenge = True
            current_pis.challenge_accepted_at = timezone.now()
            current_pis.save()


class JudgeManager(models.Manager):
    @transaction.atomic
    def create_judge(self, email, password, *args, **kwargs):
        try:
            g = Group.objects.get(name="Judge")
        except Group.DoesNotExist:
            g = Group.objects.create(name="Judge")
            g.permissions.add(Permission.objects.get(codename="view_judgeablesubmit"))
            g.permissions.add(Permission.objects.get(codename="change_judgeablesubmit"))
            g.save()
        member = Member.objects.create_user(username=email, email=email, password=password)
        member.is_staff = True
        member.groups.add(g)
        member.save()
        judge = Judge.objects.create(member=member)
        return judge


class Judge(models.Model):
    objects = JudgeManager()

    member = models.OneToOneField(Member, related_name='judge', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.member)

    def send_greeting_email(self, username, password):
        html_content = strip_spaces_between_tags(render_to_string('auth/judge_greet_email.html', {
            'login_url': '%s/admin' % settings.DOMAIN,
            'username': username,
            'password': password
        }))
        text_content = re.sub('<style[^<]+?</style>', '', html_content)
        text_content = strip_tags(text_content)

        msg = EmailMultiAlternatives('اطلاعات کاربری مصحح', text_content, 'Rastaiha <info@rastaiha.ir>', [username])
        msg.attach_alternative(html_content, "text/html")
        msg.send()


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
