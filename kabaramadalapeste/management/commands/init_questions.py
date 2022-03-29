from django.core.management.base import BaseCommand
from django.db import transaction
from kabaramadalapeste.conf import settings
from kabaramadalapeste.models import (
    Challenge, Island, Way, Treasure,
    TreasureKeyItem, TreasureRewardItem, Peste, ChallengeRewardItem,
    JudgeableQuestion
)
import os
import shutil

import string
import random


def random_string(length):
    return ''.join(random.choice(string.ascii_letters) for m in range(length))


def import_judgeables(out, path):
    counter = 0
    for question_id in range(1, 36):
        directory = os.path.join(path, str(question_id))
        try:
            for question_name in os.listdir(directory):
                question_path = os.path.join(directory, question_name)
                out.write(str(counter) + '. ' + question_path + ' copied')
                JudgeableQuestion(
                    title=question_name,
                    question=question_path,
                    challenge=Challenge.objects.filter(challenge_id=question_id)[0]
                ).save()
                counter += 1
        except e:
            pass


class Command(BaseCommand):
    help = 'Imports Questions (just Judgeable questions for now)'

    def __init__(self, *args, **kwargs):
        self.base_dir = os.path.join(settings.BASE_DIR, 'media/soals')
        self.questions = os.path.join(self.base_dir, 'Questions')
        self.Judgeable = os.path.join(self.questions, 'Judgeable')
        super(Command, self).__init__(*args, **kwargs)

    def add_arguments(self, parser):
        pass

    @transaction.atomic
    def handle(self, *args, **options):
        with transaction.atomic():
            import_judgeables(self.stdout, self.Judgeable)
