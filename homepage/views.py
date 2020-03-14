from django.shortcuts import render


def homepage(request):
    return render(request, 'homepages/landing_page.html')


def our_team(request):
    return render(request, 'homepages/our_team.html')


def about_us(request):
    return render(request, 'homepages/about_us.html')
