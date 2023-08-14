from django.contrib import admin

# Register your models here.

from django.contrib import admin
from solo.admin import SingletonModelAdmin
from django.urls import path, reverse
from django.shortcuts import redirect
from django.http import HttpResponse
from homepage.models import *
from accounts.models import Participant, Team
from django.db.models import Q, Sum


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
        s = 'نام تیم,آیدی تیم,زیتون\n'
        teams = Team.objects.all().values("id", "group_name").annotate(
            sum_coin=Sum('participant__properties__amount', filter=Q(participant__properties__property_type="SK"))
        ).order_by('-sum_coin')

        for team in teams:
            s += '%s,%d,%d\n' % (team['group_name'], team['id'], team['sum_coin'] if team['sum_coin'] else 0)
        response = HttpResponse(s, content_type="text/csv")
        response['Content-Disposition'] = 'inline; filename=scoreboard.csv'
        return response


admin.site.register(SiteConfiguration, SiteConfigAdmin)
admin.site.register(TeamMember)
