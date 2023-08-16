import csv
from django.core.management.base import BaseCommand
from django.db import transaction
from accounts.models import Member, Participant, Team
from django.conf import settings
import os
import logging

logger = logging.getLogger(__file__)


class Command(BaseCommand):
    help = 'Create participants from csv'

    def __init__(self, *args, **kwargs):
        self.base_dir = os.path.join(settings.BASE_DIR, 'accounts/initial_data')
        self.participants_file = os.path.join(self.base_dir, 'participants.csv')
        super(Command, self).__init__(*args, **kwargs)

    def add_arguments(self, parser):
        pass


    @transaction.atomic
    def handle(self, *args, **options):
        with open(self.participants_file, newline='') as csvfile:
            start_count = Participant.objects.count()
            self.stdout.write('Participant currently has %s records' % start_count)
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for i, row in enumerate(reader):
                if not i:
                    self.stdout.write('Headers: ' + ', '.join(row))
                else:
                    member = Member.objects.create(
                        username=row[0],
                        email=row[0]+"@gmail.com",
                    )
                    member.set_password(row[1])
                    team, _ = Team.objects.get_or_create(group_name=row[3])
                    team.active = True
                    team.save()
                    participant = Participant.objects.create(
                        member=member,
                        document_status='Verified',
                        is_activated=True,
                        team=team,
                    )
                    member.save()
                    participant.save()
            self.stdout.write('Created %s new Participants' % (Participant.objects.count() - start_count))
            self.stdout.write('Participant currently has %s records' % Participant.objects.count())
