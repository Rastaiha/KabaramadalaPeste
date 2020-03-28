from django.core.management.base import BaseCommand
from accounts.models import Participant
import logging
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags, strip_spaces_between_tags
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
import re
logger = logging.getLogger(__file__)


class Command(BaseCommand):
    help = 'Send email to participants'

    def add_arguments(self, parser):
        parser.add_argument('emails', nargs='*', type=str)
        parser.add_argument('-t', '--test', action='store_true', help='Test send to specific email')
        parser.add_argument('-T', '--title', type=str, help='Email title')
        parser.add_argument('-F', '--file', type=str, help='Email title')

    def send_one(self, email, participant, title, from_file):
        html_content = strip_spaces_between_tags(render_to_string(from_file, {
            'user': participant.member,
            'login_url': '%s%s' % (settings.DOMAIN, reverse('accounts:login')),
            'domain': settings.DOMAIN,
        }))
        text_content = re.sub('<style[^<]+?</style>', '', html_content)
        text_content = strip_tags(text_content)

        msg = EmailMultiAlternatives(title, text_content, 'Rastaiha <info@rastaiha.ir>', [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        self.stdout.write(
            self.style.SUCCESS('Successfully sent email for %s' % email)
        )

    def handle(self, *args, **options):
        from_file = 'auth/greet.html'
        title = 'اطلاعات شروع بازی'
        if options['file']:
            from_file = options['file']
        if options['title']:
            title = options['title']

        if options['test']:
            self.stdout.write('salam')
            par = Participant.objects.filter(is_activated=True, document_status='Verified').first()
            for email in options['emails']:
                self.send_one(email, par, title, from_file)

            self.stdout.write(
                self.style.SUCCESS('Sent %s emails' % len(options['emails']))
            )
            return
        for par in Participant.objects.filter(is_activated=True, document_status='Verified'):
            self.send_one(par.member.email, par, title, from_file)
        self.stdout.write(
            self.style.SUCCESS(
                'Sent %s emails' % Participant.objects.filter(is_activated=True, document_status='Verified').count())
        )
