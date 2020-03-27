from django.shortcuts import render
from django.http import JsonResponse, FileResponse, Http404
from django.contrib import messages
from django.conf import settings

from homepage.models import *
import os


def homepage(request):
    payment_status = request.GET.get('payment')
    if payment_status == settings.ERROR_STATUS:
        messages.error(request, 'پرداخت ناموفق بود')
    if payment_status == settings.OK_STATUS:
        messages.success(request, 'پرداخت با موفقیت انجام شد')

    activate_status = request.GET.get('activate')
    if activate_status == settings.ERROR_STATUS:
        messages.error(request, 'لینک فعال‌سازی درست نیست')
    if activate_status == settings.HELP_STATUS:
        if request.user.is_authenticated:
            messages.info(request, 'حساب قبلا فعال شده.')
        else:
            messages.info(request, 'حساب قبلا فعال شده، می‌تونی از صفحه‌ی ورود وارد شی.')
    if activate_status == settings.OK_STATUS:
        messages.success(request, 'حساب با موفقیت فعال شد')

    signup_status = request.GET.get('signup')
    if signup_status == settings.OK_STATUS:
        messages.success(request, 'ثبت نام با موفقیت انجام شد. برای فعال‌سازی حساب به ایمیلت مراجعه کن.')
    return render(request, 'homepages/landing_page.html', {
        'not_nav_padding': True
    })


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
            "description": team_member.description,
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


def rules_pdf(request):
    try:
        rules_file_path = os.path.join(
            settings.BASE_DIR,
            'homepage/static/misc/منشورِ قوانین کابارآمادالاپسته.pdf'
        )
        return FileResponse(open(rules_file_path, 'rb'), content_type='application/pdf')
    except FileNotFoundError:
        raise Http404()
