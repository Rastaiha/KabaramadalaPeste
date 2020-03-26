from django.core.management.base import BaseCommand
from accounts.models import Judge, Member
import os
import logging

logger = logging.getLogger(__file__)


class Command(BaseCommand):
    help = 'Create judges by email list'

    def add_arguments(self, parser):
        parser.add_argument('email', nargs='+', type=str)

    def handle(self, *args, **options):
        for judge_email in options['email']:
            password = Member.objects.make_random_password()
            judge = Judge.objects.create_judge(
                email=judge_email,
                password=password
            )
            self.stdout.write(
                self.style.SUCCESS('Successfully created judge %s with password %s' % (judge_email, password))
            )
            judge.send_greeting_email(
                username=judge_email,
                password=password
            )
