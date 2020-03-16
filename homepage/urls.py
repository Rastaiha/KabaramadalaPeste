from django.shortcuts import render
from django.urls import path

from .views import homepage, our_team, about_us, get_all_members_api, get_countdown_api

urlpatterns = [
    path('', homepage, name="homepage"),
    path('test_auth_base/', lambda r: render(r, 'auth/signup.html', {
        "nol": True
    })),
    path('our_team/', our_team),
    path('about_us/', about_us),
    path('get_all_members_api/', get_all_members_api, name="get_all_members_api"),
    path('get_countdown_api/', get_countdown_api, name="get_countdown_api"),
]
