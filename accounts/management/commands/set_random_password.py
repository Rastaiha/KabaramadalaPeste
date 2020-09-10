from django.core.management.base import BaseCommand
from accounts.models import Member
import os
import logging

logger = logging.getLogger(__file__)


class Command(BaseCommand):
    help = 'Set random password'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email of member')

    def handle(self, *args, **options):
        password = Member.objects.make_random_password()
        email = options['email']
        member = Member.objects.get(email=email)
        member.set_password(password)
        member.save()
        self.stdout.write(
            self.style.SUCCESS('Successfully changed %s password to %s' % (email, password))
        )
