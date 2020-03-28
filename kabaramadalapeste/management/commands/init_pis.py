from django.core.management.base import BaseCommand
from accounts.models import Participant
from django.db import transaction


class Command(BaseCommand):
    help = 'Displays current time'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        i = 0
        n = Participant.objects.all().count()
        for participant in Participant.objects.all():
            print('Participant<%s> number %d out of %d (%0.1f%%)' % (participant.member.email, i, n, i/n*100))
            participant.init_pis()
            participant.init_properties()
            i += 1
