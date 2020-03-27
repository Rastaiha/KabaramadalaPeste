from django.core.management.base import BaseCommand
from accounts.models import Participant


class Command(BaseCommand):
    help = 'Displays current time'

    def handle(self, *args, **kwargs):
        for participant in Participant.objects.all():
            participant.init_pis()
            participant.init_properties()
