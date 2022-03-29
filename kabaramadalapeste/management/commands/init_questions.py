from django.core.management.base import BaseCommand
from django.db import transaction
from kabaramadalapeste.conf import settings
from kabaramadalapeste.models import (
    Challenge, Island, Way, Treasure,
    TreasureKeyItem, TreasureRewardItem, Peste, ChallengeRewardItem,
    JudgeableQuestion
)
import os


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
        base_dir = os.path.join(settings.BASE_DIR, 'kabaramadalapeste/initial_data')
        clue_file = os.path.join(base_dir, 'clues/%s.txt' % row[0])
        island.peste_guidance = open(clue_file).read()
        island.save()
    if int(row[3]):
        Peste.objects.create(
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
    help = 'Imports Questions (just Judgeable questions for now)'

    def __init__(self, *args, **kwargs):
        self.base_dir = os.path.join(settings.BASE_DIR, 'kabaramadalapeste/initial_data')
        self.questions = os.path.join(self.base_dir, 'Questions')
        self.Judgeable = os.path.join(self.questions, 'Judgeable')
        super(Command, self).__init__(*args, **kwargs)

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        with transaction.atomic():
            self.import_judgeables(self.Judgeable)

    def import_judgeables(self, path):
        for question_id in Range(1, 36):
            directory = os.path.join(path, question_id)
            for question_name in os.listdir(directory): 
                JudgeableQuestion.objects.create(
                    title = question_name,
                    question = os.path.join(directory, question_name),
                    
                )

        


        # with open(csv_path, newline='') as csvfile:
        #     start_count = Model.objects.count()
        #     self.stdout.write('%s currently has %s records' % (Model.__name__, start_count))
        #     reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        #     for i, row in enumerate(reader):
        #         if not i:
        #             self.stdout.write('Headers: ' + ', '.join(row))
        #         else:
        #             create_func(row)
        #     self.stdout.write('Created %s new %ss' % (Model.objects.count() - start_count, Model.__name__.lower()))
        #     self.stdout.write('%s currently has %s records' % (Model.__name__, Model.objects.count()))
