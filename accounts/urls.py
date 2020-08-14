from django.shortcuts import render
from django.urls import path, re_path

from .views import signup, login, logout, send_request, verify, activate, survey

urlpatterns = [
    path('request/', send_request, name='request'),
    path('verify/', verify, name='verify'),
    path('signup/', signup, name="signup"),
    path('logout/', logout, name="logout"),
    path('login/', login, name="login"),
    path('survey/', survey, name="survey"),
    re_path(r'activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/',
            activate, name='activate')
]
