from django.shortcuts import render


def homepage(request):
    return render(request, 'homepages/landing_page.html')
