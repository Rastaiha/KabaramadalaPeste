import csv
from django.core.management.base import BaseCommand
from django.db import transaction
from accounts.models import Member, Participant, Team
from django.conf import settings
import os
import logging

logger = logging.getLogger(__file__)


class Command(BaseCommand):
    help = 'Create participants, members, and teams from csv'

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)
        self.base_dir = None
        self.participants_file = None

    def init(self, *args, **kwargs):
        self.base_dir = os.path.join(settings.BASE_DIR, 'accounts/initial_data')
        self.participants_file = os.path.join(self.base_dir, 'participants.csv')
        super().init(*args, **kwargs)

    def add_arguments(self, parser):
        pass

    @transaction.atomic
    def handle(self, *args, **options):
        with open(self.participants_file, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            start_count = Participant.objects.count()
            self.stdout.write(f'Participant currently has {start_count} records')
            headers = next(reader)
            self.stdout.write('Headers: ' + ', '.join(headers))
            for row in reader:
                member, _ = Member.objects.get_or_create(
                    username=row[1],
                    email=row[1] + "@gmail.com",
                    first_name=row[0]
                )
                member.set_password(row[2])
                member.save()

                team, created = Team.objects.get_or_create(group_name=row[3])
                if created:
                    team.chat_room_link = row[4]
                    team.active = True
                    team.save()

                Participant.objects.get_or_create(
                    member=member,
                    document_status='Verified',
                    is_activated=True,
                    team=team,
                )

            new_count = Participant.objects.count() - start_count
            self.stdout.write(f'Created {new_count} new Participants')
            self.stdout.write(f'Participant currently has {Participant.objects.count()} records')
