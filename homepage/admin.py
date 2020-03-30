from django.contrib import admin

# Register your models here.

from django.contrib import admin
from solo.admin import SingletonModelAdmin
from django.urls import path, reverse
from django.shortcuts import redirect
from django.http import HttpResponse
from homepage.models import *
from accounts.models import Participant


class SiteConfigAdmin(SingletonModelAdmin):
    change_form_template = 'admin/homepage/SiteConfiguration/change_form.html'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'download_scoreboard/',
                self.download_scoreboard,
                name='download_scoreboard',
            ),
        ]
        return custom_urls + urls

    def download_scoreboard(self, request, *args, **kwargs):
        s = 'نام و نام خوانوادگی,یوزرنیم,مدرسه,شهر,سکه\n'
        for participant in Participant.objects.filter(document_status='Verified', is_activated=True).all():
            s += '%s,%s,%s,%s,%d\n' % \
                 (participant.member.first_name, participant.member.username, participant.school, participant.city,
                  participant.sekke.amount)
        response = HttpResponse(s, content_type="text/csv")
        response['Content-Disposition'] = 'inline; filename=scoreboard.csv'
        return response


admin.site.register(SiteConfiguration, SiteConfigAdmin)
admin.site.register(TeamMember)
