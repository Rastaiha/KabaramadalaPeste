from django.core.management.base import BaseCommand
from accounts.models import Participant
from django.db import transaction


class Command(BaseCommand):
    help = 'Displays current time'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        for participant in Participant.objects.all():
            participant.init_pis()
            participant.init_properties()
