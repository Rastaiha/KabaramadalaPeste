from django.core.management.base import BaseCommand
from django.db import transaction
from accounts.factory import MemberFactory, ParticipantFactory
from accounts.models import Participant
from kabaramadalapeste.conf import settings
from kabaramadalapeste.models import (
    Challenge, Island, Way, Treasure, Bully,
    TreasureKeyItem, TreasureRewardItem, Peste, ChallengeRewardItem
)
import os
import csv
import logging

logger = logging.getLogger(__file__)


def import_treasure_row(row):
    treasure = Treasure.objects.create()
    treasure.keys.add(TreasureKeyItem(key_type=settings.GAME_KEY1, amount=row[0]), bulk=False)
    treasure.keys.add(TreasureKeyItem(key_type=settings.GAME_KEY2, amount=row[1]), bulk=False)
    treasure.keys.add(TreasureKeyItem(key_type=settings.GAME_KEY3, amount=row[2]), bulk=False)
    treasure.rewards.add(TreasureRewardItem(reward_type=settings.GAME_SEKKE, amount=row[3]), bulk=False)
    treasure.rewards.add(TreasureRewardItem(reward_type=settings.GAME_KEY1, amount=row[4]), bulk=False)
    treasure.rewards.add(TreasureRewardItem(reward_type=settings.GAME_KEY2, amount=row[5]), bulk=False)
    treasure.rewards.add(TreasureRewardItem(reward_type=settings.GAME_KEY3, amount=row[6]), bulk=False)
    # treasure.rewards.add(TreasureRewardItem(reward_type=settings.GAME_VISION, amount=row[7]), bulk=False)
    # treasure.rewards.add(TreasureRewardItem(reward_type=settings.GAME_TRAVEL_EXPRESS, amount=row[8]), bulk=False)
    # treasure.rewards.add(TreasureRewardItem(reward_type=settings.GAME_CHALLENGE_PLUS, amount=row[9]), bulk=False)
    # treasure.rewards.add(TreasureRewardItem(reward_type=settings.GAME_BULLY, amount=row[10]), bulk=False)


def import_island_row(row):
    if int(row[0]) == settings.GAME_BANDARGAH_ISLAND_ID:
        island = Island.objects.create(
            island_id=row[0],
            name=row[1],
        )
    else:
        island = Island.objects.create(
            island_id=row[0],
            name=row[1],
            challenge=Challenge.objects.get(challenge_id=row[2])
        )
        island.save()
    if int(row[3]):
        Peste.objects.create(
            island=island
        )
    if int(row[4]):
        bullier_member = Participant.objects.get(member__username=settings.GAME_BULLYMAN_USERNAME)
        Bully.objects.create(
            owner=bullier_member,
            island=island
        )


def import_challenge_row(row):
    challenge = Challenge.objects.create(
        challenge_id=row[0],
        name=row[1],
        is_judgeable=int(row[2])
    )
    challenge.rewards.add(ChallengeRewardItem(reward_type=settings.GAME_SEKKE, amount=row[3]), bulk=False)
    challenge.rewards.add(ChallengeRewardItem(reward_type=settings.GAME_KEY1, amount=row[4]), bulk=False)
    challenge.rewards.add(ChallengeRewardItem(reward_type=settings.GAME_KEY2, amount=row[5]), bulk=False)
    challenge.rewards.add(ChallengeRewardItem(reward_type=settings.GAME_KEY3, amount=row[6]), bulk=False)


class Command(BaseCommand):
    help = 'Imports game data like islands, and challenges data'

    def __init__(self, *args, **kwargs):
        self.base_dir = os.path.join(settings.BASE_DIR, 'kabaramadalapeste/initial_data')
        self.challenges_file = os.path.join(self.base_dir, 'challenges.csv')
        self.islands_file = os.path.join(self.base_dir, 'islands.csv')
        self.ways_file = os.path.join(self.base_dir, 'ways.csv')
        self.treasures_file = os.path.join(self.base_dir, 'treasures.csv')
        super(Command, self).__init__(*args, **kwargs)

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        with transaction.atomic():
            if not Participant.objects.filter(member__username=settings.GAME_BULLYMAN_USERNAME):
                bullier_member = MemberFactory(username=settings.GAME_BULLYMAN_USERNAME)
                ParticipantFactory(member=bullier_member)
            self.import_objects(self.challenges_file, Challenge,
                                import_challenge_row)
            self.import_objects(self.islands_file, Island,
                                import_island_row)
            self.import_objects(self.ways_file, Way,
                                lambda row: Way.objects.create(
                                    first_end=Island.objects.get(island_id=row[0]),
                                    second_end=Island.objects.get(island_id=row[1])
                                ))
            self.import_objects(self.treasures_file, Treasure,
                                import_treasure_row)

    def import_objects(self, csv_path, Model, create_func):
        with open(csv_path, newline='') as csvfile:
            start_count = Model.objects.count()
            self.stdout.write('%s currently has %s records' % (Model.__name__, start_count))
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for i, row in enumerate(reader):
                if not i:
                    self.stdout.write('Headers: ' + ', '.join(row))
                else:
                    create_func(row)
            self.stdout.write('Created %s new %ss' % (Model.objects.count() - start_count, Model.__name__.lower()))
            self.stdout.write('%s currently has %s records' % (Model.__name__, Model.objects.count()))
