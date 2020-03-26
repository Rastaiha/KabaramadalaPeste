from django.core.management.base import BaseCommand
from django.db import transaction
from kabaramadalapeste.conf import settings
from kabaramadalapeste.models import (
    Challenge, Island, Way, Treasure,
    TreasureKeyItem, TreasureRewardItem
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


class Command(BaseCommand):
    help = 'Imports game data like islands, and challenges data'

    def __init__(self):
        self.base_dir = os.path.join(settings.BASE_DIR, 'kabaramadalapeste/initial_data')
        self.challenges_file = os.path.join(self.base_dir, 'challenges.csv')
        self.islands_file = os.path.join(self.base_dir, 'islands.csv')
        self.ways_file = os.path.join(self.base_dir, 'ways.csv')
        self.treasures_file = os.path.join(self.base_dir, 'treasures.csv')

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        with transaction.atomic():
            self.import_objects(self.challenges_file, Challenge,
                                lambda row: Challenge.objects.create(
                                    challenge_id=row[0],
                                    name=row[1],
                                    is_judgeable=bool(row[2])
                                ))
            self.import_objects(self.islands_file, Island,
                                lambda row: Island.objects.create(
                                    island_id=row[0],
                                    name=row[1],
                                    challenge=Challenge.objects.get(challenge_id=row[2])
                                ))
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
            logger.info('%s currently has %s records' % (Model.__name__, start_count))
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for i, row in enumerate(reader):
                if not i:
                    logger.info('Headers: ' + ', '.join(row))
                else:
                    create_func(row)
            logger.info('Created %s new %ss' % (Model.objects.count() - start_count, Model.__name__.lower()))
            logger.info('%s currently has %s records' % (Model.__name__, Model.objects.count()))
