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


class Command(BaseCommand):
    help = 'Imports Questions (Judgeable questions and their short answers)'

    def __init__(self, *args, **kwargs):
        from kabaramadalapeste.conf import settings
        self.base_dir = os.path.join(settings.BASE_DIR, 'media/soals')
        self.questions = os.path.join(self.base_dir, 'Questions')
        self.Judgeable = os.path.join(self.questions, 'Judgeable')
        super().__init__(*args, **kwargs)

    def handle(self, *args, **options):
        with transaction.atomic():
            self.import_judgeables()

    def import_judgeables(self):
        counter = 0
        for question_id in range(1, 36):
            try:
                directory = os.path.join(self.Judgeable, str(question_id))
                for question_name in os.listdir(directory):
                    question_path = os.path.join(directory, question_name)
                    if question_name.endswith('.txt'):
                        with open(question_path, 'r') as file:
                            short_answer = file.read().strip()
                        question = JudgeableQuestion.objects.create(
                            title=question_name.replace('.txt', ''),
                            short_answer=short_answer,  # Assuming the field is named 'short_answer'
                            challenge=Challenge.objects.get(id=question_id)
                        )
                        self.stdout.write(f'{counter}. {question.title} - Short answer imported')
                        counter += 1
            except Exception as e:
                self.stdout.write(f'Error importing question {question_id}: {e}')
