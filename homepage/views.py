from django.shortcuts import render
from django.http import JsonResponse

from homepage.models import *

import json


def homepage(request):
    return render(request, 'homepages/landing_page.html')


def our_team(request):
    return render(request, 'homepages/our_team.html')


def about_us(request):
    return render(request, 'homepages/about_us.html')


def get_all_members_api(request):
    data = []
    for team_member in TeamMember.objects.all():
        data.append({
            "name": team_member.full_name,
            "title": team_member.team_type,
            'image': team_member.profile_picture.url
        })
    return JsonResponse({'data': data})


def get_countdown_api(request):
    return JsonResponse({
        'year': SiteConfiguration.get_solo().countdown_date.year,
        'month': SiteConfiguration.get_solo().countdown_date.month - 1,
        'day': SiteConfiguration.get_solo().countdown_date.day,
        'hour': SiteConfiguration.get_solo().countdown_date.hour
    })
