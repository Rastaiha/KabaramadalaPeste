from django.core.management.base import BaseCommand
from kabaramadalapeste.models import *
from notifications.models import Notification
from django.db import transaction
from collections import defaultdict
import  json


class Command(BaseCommand):
    help = 'Creates stat json'

    def add_arguments(self, parser):
        parser.add_argument('day1_backup', type=str, help='address of day1 backup folder')
        parser.add_argument('destination', type=str, help='address of destination file')

    @transaction.atomic
    def handle(self, *args, **kwargs):
        day1_backup_file = open(kwargs['day1_backup'])
        heuristic_dict = defaultdict(int)
        for line in day1_backup_file.readlines()[1:]:
            l = line.split(',')
            if l[11] == 't':
                heuristic_dict[int(l[5])] += 1
        stat_dict = {}
        for participant in Participant.objects.exclude(currently_at_island=None).all():
            num_opened_treasures = ParticipantIslandStatus.objects.filter(
                participant=participant,
                did_open_treasure=True
            ).all().count()
            num_created_trades = participant.created_trade_offers.filter(status=settings.GAME_OFFER_ACCEPTED).all().count()
            num_accepted_trades = participant.accepted_trade_offers.filter(status=settings.GAME_OFFER_ACCEPTED).all().count()
            num_fall_in_bully = Notification.objects.filter(
                recipient=participant.member,
                verb='fall_in_bully'
            ).all().count()
            num_bully = Notification.objects.filter(
                recipient=participant.member,
                verb='sb_fall_in_your_bully'
            ).all().count()
            num_accepted_judgeable_challenges = JudgeableSubmit.objects.filter(
                pis__participant=participant,
                submit_status='Correct'
            ).all().count()
            num_accepted_shortanswer_challenges = ShortAnswerSubmit.objects.filter(
                pis__participant=participant,
                submit_status='Correct'
            ).all().count()
            num_logged_moves = GameEventLog.objects.filter(
                who=participant,
                event_type='Move'
            ).all().count()
            stat_dict[participant.pk] = {
                'username': participant.member.username,
                'real_name': participant.member.first_name,
                'gender': participant.gender,
                'profile_picture_url': participant.picture_url,
                'num_travels': num_logged_moves + heuristic_dict[participant.pk],
                'num_sekke': participant.sekke.amount,
                'num_bully': num_bully,
                'num_fall_in_bully': num_fall_in_bully,
                'num_accepted_challenges': num_accepted_judgeable_challenges + num_accepted_shortanswer_challenges,
                'num_trades': num_created_trades + num_accepted_trades,
                'num_opened_treasures': num_opened_treasures,
                'did_won_peste': participant.did_won_peste()
            }
        json.dump(stat_dict, open(kwargs['destination'], 'w', encoding='UTF-8'))
