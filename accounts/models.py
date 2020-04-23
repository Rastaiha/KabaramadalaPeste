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
from notifications.models import Notification
from enum import Enum
from notifications.signals import notify
from easy_thumbnails.files import get_thumbnailer

from collections import defaultdict

import logging
import random
import re
from easy_thumbnails.fields import ThumbnailerImageField
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

    class DidNotAcceptChallenge(Exception):
        pass

    class PropertiesAreNotEnough(Exception):
        pass

    class MaximumActiveOffersExceeded(Exception):
        pass

    class MaximumChallengePerDayExceeded(Exception):
        pass

    class BadInput(Exception):
        pass

    class CantPutAnchorAgain(Exception):
        pass

    class CantSpadeAgain(Exception):
        pass

    class CantAcceptChallengeAgain(Exception):
        pass

    class CantOpenTreasureAgain(Exception):
        pass

    class CantSubmitChallengeAgain(Exception):
        pass

    member = models.OneToOneField(Member, related_name='participant', on_delete=models.CASCADE)
    picture = ThumbnailerImageField(upload_to='picture', default="picture/user_default.png")
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

    stat_image = models.ImageField(upload_to='stats/', null=True, default="stats/base_stat.png")
    stat_image_with_background = models.ImageField(
        upload_to='stats-back/', null=True, default="stats-back/base_stat_back.png"
    )

    def __str__(self):
        return str(self.member)

    @property
    def picture_url(self):
        try:
            pic = self.picture if self.picture else 'picture/user_default.png'
            return get_thumbnailer(pic)['avatar'].url
        except Exception:
            return ''

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

    def did_won_peste(self):
        if self.peste_set.count():
            return True
        return False

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

            game_models.GameEventLog.objects.create(
                who=self,
                when=timezone.now(),
                where=None,
                event_type=game_models.GameEventLog.EventTypes.SetStart,
                related=dest_island
            )

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
            game_models.GameEventLog.objects.create(
                who=self,
                when=timezone.now(),
                where=src_pis.island,
                event_type=game_models.GameEventLog.EventTypes.Move,
                related=dest_pis.island
            )

    def put_anchor_on_current_island(self):
        current_pis = game_models.ParticipantIslandStatus.objects.get(
            participant=self,
            island=self.get_current_island()
        )
        if current_pis.currently_anchored:
            raise Participant.CantPutAnchorAgain

        with transaction.atomic():
            self.reduce_property(game_settings.GAME_SEKKE, game_settings.GAME_PUT_ANCHOR_PRICE)

            current_pis.currently_anchored = True
            current_pis.is_treasure_visible = True
            current_pis.last_anchored_at = timezone.now()
            current_pis.save()

#            if game_models.PesteConfiguration.get_solo().is_peste_available:
#                self.send_msg_peste_guidance()

            active_bullies = self.get_current_island().bullies.all().filter(is_expired=False)
            if active_bullies.count() > 0:
                bully = active_bullies[0]
                if bully.owner.pk != self.pk:
                    game_models.GameEventLog.objects.create(
                        who=self,
                        when=timezone.now(),
                        where=current_pis.island,
                        event_type=game_models.GameEventLog.EventTypes.BullyTarget,
                        related=bully
                    )
                    try:
                        self.reduce_property(game_settings.GAME_SEKKE, game_settings.GAME_BULLY_DAMAGE)
                        self.send_msg_fall_in_bully(bully, game_settings.GAME_BULLY_DAMAGE)
                        bully.owner.add_property(game_settings.GAME_SEKKE, game_settings.GAME_BULLY_DAMAGE)
                        bully.owner.send_msg_sb_fall_in_your_bully(bully, self, game_settings.GAME_BULLY_DAMAGE)
                    except Participant.PropertiesAreNotEnough:
                        damage = self.sekke.amount
                        self.reduce_property(game_settings.GAME_SEKKE, damage)
                        self.send_msg_fall_in_bully(bully, damage)
                        bully.owner.add_property(game_settings.GAME_SEKKE, damage)
                        bully.owner.send_msg_sb_fall_in_your_bully(bully, self, damage)

            game_models.GameEventLog.objects.create(
                who=self,
                when=timezone.now(),
                where=current_pis.island,
                event_type=game_models.GameEventLog.EventTypes.Anchor
            )

    def open_treasure_on_current_island(self):
        current_pis = game_models.ParticipantIslandStatus.objects.get(
            participant=self,
            island=self.get_current_island()
        )
        if not current_pis.currently_anchored:
            raise Participant.DidNotAnchored
        if current_pis.did_open_treasure:
            raise Participant.CantOpenTreasureAgain

        treasure = current_pis.treasure
        with transaction.atomic():
            for key in treasure.keys.all():
                self.reduce_property(key.key_type, key.amount)
            for reward in treasure.rewards.all():
                self.add_property(reward.reward_type, reward.amount)
            current_pis.did_open_treasure = True
            current_pis.treasure_opened_at = timezone.now()
            current_pis.save()
            game_models.GameEventLog.objects.create(
                who=self,
                when=timezone.now(),
                where=current_pis.island,
                event_type=game_models.GameEventLog.EventTypes.OpenTreasure,
                related=treasure
            )

    def accept_challenge_on_current_island(self):
        current_pis = game_models.ParticipantIslandStatus.objects.get(
            participant=self,
            island=self.get_current_island()
        )
        if not current_pis.currently_anchored:
            raise Participant.DidNotAnchored
        if current_pis.did_accept_challenge:
            raise Participant.CantAcceptChallengeAgain
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
            game_models.GameEventLog.objects.create(
                who=self,
                when=timezone.now(),
                where=current_pis.island,
                event_type=game_models.GameEventLog.EventTypes.AcceptChallenge,
                related=current_pis.question
            )

    def spade_on_current_island(self):
        if not game_models.PesteConfiguration.get_solo().is_peste_available:
            raise game_models.Peste.PesteNotAvailable
        current_pis = game_models.ParticipantIslandStatus.objects.get(
            participant=self,
            island=self.get_current_island()
        )
        if not current_pis.currently_anchored:
            raise Participant.DidNotAnchored
        if current_pis.did_spade:
            raise Participant.CantSpadeAgain
        with transaction.atomic():
            self.reduce_property(settings.GAME_SEKKE, game_models.PesteConfiguration.get_solo().island_spade_cost)
            current_pis.did_spade = True
            current_pis.spaded_at = timezone.now()
            current_pis.save()
            event_log = game_models.GameEventLog.objects.create(
                who=self,
                when=timezone.now(),
                where=current_pis.island,
                event_type=game_models.GameEventLog.EventTypes.Spade
            )
            try:
                if self.currently_at_island.peste.is_found:
                    self.send_msg_spade_result(False)
                    return False
                self.add_property(settings.GAME_SEKKE, game_models.PesteConfiguration.get_solo().peste_reward)
                self.currently_at_island.peste.is_found = True
                self.currently_at_island.peste.found_by = self
                self.currently_at_island.peste.found_at = timezone.now()
                self.currently_at_island.peste.save()
                self.save()
                event_log.related = self.currently_at_island.peste
                event_log.save()
                self.send_msg_spade_result(True)
                for p in Participant.objects.all():
                    p.send_msg_peste_news(self)
                return True
            except game_models.Island.peste.RelatedObjectDoesNotExist:
                self.send_msg_spade_result(False)
                return False

    def send_msg_bully_expired(self, bully):
        text = 'تله‌ای که توی جزیره‌ی %s جاسازی کرده بود به علت جاسازی شدن تله‌ی جدید از بین رفت.' % (bully.island.name, )
        notify.send(
            sender=Member.objects.filter(is_superuser=True).all()[0],
            recipient=self.member,
            verb='bully_expired',
            description='تله‌ات از بین رفت',
            level='info', public=False, text=text
        )

    def send_msg_offer_accepted(self, trade_offer):
        text = 'پیشنهاد مبادله‌ات توسط %s قبول شد. %s گرفتی.' % \
               (trade_offer.accepted_participant, trade_offer.get_requested_items_persian())
        notify.send(
            sender=Member.objects.filter(is_superuser=True).all()[0],
            recipient=self.member,
            verb='offer_accepted',
            description='پیشنهاد مبادله‌ات قبول شد',
            level='info', public=False, text=text
        )

    def send_msg_fall_in_bully(self, bully, amount):
        text = 'توی تله‌ی جاسازی شده توسط %s افتادی' % (bully.owner, )
        if amount < game_settings.GAME_BULLY_DAMAGE:
            text += ' و چون پول کافی نداشتی ازت %d سکه کم شد.' % (amount, )
        else:
            text += ' و ازت %d سکه کم شد.' % (amount, )
        notify.send(
            sender=Member.objects.filter(is_superuser=True).all()[0],
            recipient=self.member,
            verb='fall_in_bully',
            description='توی تله افتادی',
            level='info', public=False, text=text
        )

    def send_msg_sb_fall_in_your_bully(self, bully, victim_participant, amount):
        text = '%s توی تله‌ی جاسازی شده در جزیره‌ی %s افتاد' % (victim_participant, bully.island.name)
        if amount < game_settings.GAME_BULLY_DAMAGE:
            text += ' و چون پول کافی نداشت بهت %d سکه اضافه شد.' % (amount, )
        else:
            text += ' و بهت %d سکه اضافه شد.' % (amount, )
        notify.send(
            sender=Member.objects.filter(is_superuser=True).all()[0],
            recipient=self.member,
            verb='sb_fall_in_your_bully',
            description='یکی تو تله‌ات افتاد',
            level='info', public=False, text=text
        )

    def send_msg_bandargah_computed(self, investment, was_successful, total_investments):
        text = 'کار امروز بندرگاه به پایان رسید! مجموع سرمایه‌گذاری‌ها %d سکه بود' % (total_investments, )
        if was_successful:
            gain = int(game_models.BandargahConfiguration.get_solo().profit_coefficient * investment.amount)
            text += ' که درون بازه‌ی سوددهی قرار گرفت'
        else:
            gain = int(game_models.BandargahConfiguration.get_solo().loss_coefficient * investment.amount)
            text += ' که درون بازه‌ی سوددهی قرار نگرفت'
        text += ' و به تو %d سکه رسید.' % (gain, )
        notify.send(
            sender=Member.objects.filter(is_superuser=True).all()[0],
            recipient=self.member,
            verb='bandargah_computed',
            description='نتیجه‌ی سرمایه‌گذاری در بندرگاه',
            level='info', public=False, text=text
        )

    def send_msg_correct_judged_answer(self, judgeablesubmit):
        if judgeablesubmit.judge_note:
            text = 'پاسخی که قبلا به چالش‌ جزیره‌ی %s داده بودی توسط داوران ارزیابی شد و درست بود. %s دریافت کردی. داور بهت گفته: %s' % \
                (judgeablesubmit.pis.island.name, judgeablesubmit.get_rewards_persian(), judgeablesubmit.judge_note)
        else:
            text = 'پاسخی که قبلا به چالش‌ جزیره‌ی %s داده بودی توسط داوران ارزیابی شد و درست بود. %s دریافت کردی.' % \
                (judgeablesubmit.pis.island.name, judgeablesubmit.get_rewards_persian())
        notify.send(
            sender=Member.objects.filter(is_superuser=True).all()[0],
            recipient=self.member,
            verb='correct_judged_answer',
            description='پاسخ صحیح',
            level='info', public=False, text=text
        )

    def send_msg_wrong_judged_answer(self, judgeablesubmit):
        if judgeablesubmit.judge_note:
            text = 'پاسخی که قبلا به چالش‌ جزیره‌ی %s داده بودی توسط داوران ارزیابی شد و اشتباه بود. داور بهت گفته: %s' % \
                (judgeablesubmit.pis.island.name, judgeablesubmit.judge_note)
        else:
            text = 'پاسخی که قبلا به چالش‌ جزیره‌ی %s داده بودی توسط داوران ارزیابی شد و اشتباه بود.' % \
                (judgeablesubmit.pis.island.name, )
        notify.send(
            sender=Member.objects.filter(is_superuser=True).all()[0],
            recipient=self.member,
            verb='wrong_judged_answer',
            description='پاسخ اشتباه',
            level='info', public=False, text=text
        )

    def send_msg_correct_short_answer(self, shortanswersubmit):
        text = 'پاسخی که به چالش‌ جزیره‌ی %s دادی صحیح بود. %s دریافت کردی.' % \
               (shortanswersubmit.pis.island.name, shortanswersubmit.get_rewards_persian())
        notify.send(
            sender=Member.objects.filter(is_superuser=True).all()[0],
            recipient=self.member,
            verb='correct_short_answer',
            description='پاسخ صحیح',
            level='info', public=False, text=text
        )

    def send_msg_wrong_short_answer(self, shortanswersubmit):
        text = 'پاسخی که به چالش‌ جزیره‌ی %s دادی اشتباه بود.' % \
               (shortanswersubmit.pis.island.name, )
        notify.send(
            sender=Member.objects.filter(is_superuser=True).all()[0],
            recipient=self.member,
            verb='wrong_short_answer',
            description='پاسخ اشتباه',
            level='info', public=False, text=text
        )

    def send_msg_peste_guidance(self):
        notify.send(
            sender=Member.objects.filter(is_superuser=True).all()[0],
            recipient=self.member,
            verb='peste_guidance',
            description='راهنمای گنج پسته',
            level='info', public=False, text=self.currently_at_island.peste_guidance
        )

    def send_msg_peste_news(self, winner_participant):
        text = 'دوستان پسته طلایی توسط %s پیدا شد دیگر کلنگ نزنید چون پسته ای در کار نیست.' % (winner_participant, )
        notify.send(
            sender=Member.objects.filter(is_superuser=True).all()[0],
            recipient=self.member,
            verb='peste_news',
            description='خبر پسته‌ی طلایی',
            level='info', public=False, text=text
        )

    @transaction.atomic
    def send_msg_spade_result(self, was_successful):
        if was_successful:
            text = 'تبریک می‌گم! پسسسسستتتتتتتتتتتتتتههههههههههه طلایی رو یافتی!'
        else:
            text = 'متاسفم. کلنگ‌زنی ناموفق بود و پسته‌ای توی این جزیره پیدا نشد.'
        notif = notify.send(
            sender=Member.objects.filter(is_superuser=True).all()[0],
            recipient=self.member,
            verb='sapde_result',
            description='نتیجه‌ی کلنگ‌زنی',
            level='info', public=False, text=text
        )[0][1][0]
        Notification.objects.filter(pk=notif.pk).mark_all_as_read()


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
        member.is_participant = False
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


class NotificationData(models.Model):
    class NotificationStatus(models.TextChoices):
        Draft = 'Draft'
        Sent = 'Sent'

    level = models.CharField(choices=Notification.LEVELS, default=Notification.LEVELS.info, max_length=20)
    text = models.TextField()

    status = models.CharField(
        choices=NotificationStatus.choices,
        default=NotificationStatus.Draft,
        max_length=20
    )
    sent_at = models.DateTimeField(null=True, blank=True)
    sent_by = models.ForeignKey(
        Member,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sent_notification_datas'
    )

    send_to_all_participants = models.BooleanField(default=False)

    recipients = models.ManyToManyField(Member, blank=True)

    @transaction.atomic
    def send_notifications(self, sender_user):
        if self.status == NotificationData.NotificationStatus.Sent:
            logger.warning('Cant resend notification data')
            return
        if self.send_to_all_participants:
            recipient = Member.objects.filter(is_participant=True)
        else:
            recipient = self.recipients.all()
        notify.send(
            sender=sender_user,
            recipient=recipient,
            verb='inform',
            action_object=self, level=self.level, public=False, text=self.text
        )
        self.status = NotificationData.NotificationStatus.Sent
        self.sent_by = sender_user
        self.sent_at = timezone.now()
        self.save()
