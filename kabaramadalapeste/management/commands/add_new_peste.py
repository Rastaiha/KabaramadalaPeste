from django.core.management.base import BaseCommand
from kabaramadalapeste.models import *
from django.db import transaction


class Command(BaseCommand):
    help = 'Adds new PESTE to game'

    def add_arguments(self, parser):
        parser.add_argument('island_id', type=int, help='island_id of peste island')

    @transaction.atomic
    def handle(self, *args, **kwargs):
        for island in Island.objects.all():
            if island.island_id == settings.GAME_BANDARGAH_ISLAND_ID:
                continue
            base_dir = os.path.join(settings.BASE_DIR, 'kabaramadalapeste/initial_data')
            clue_file = os.path.join(base_dir, 'clues2/%s.txt' % island.island_id)
            island.peste_guidance = open(clue_file).read()
            island.save()
            if island.island_id == kwargs['island_id']:
                peste = Peste.objects.create(island=island)
                peste.save()
        ParticipantIslandStatus.objects.update(did_spade=False)
        ParticipantIslandStatus.objects.update(spaded_at=None)
