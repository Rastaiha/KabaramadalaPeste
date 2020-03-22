from django.shortcuts import render
from django.urls import path

from .views import signup, login, logout, send_request, verify

urlpatterns = [
    path('request/', send_request, name='request'),
    path('verify/', verify, name='verify'),
    path('signup/', signup, name="signup"),
    path('logout/', logout, name="logout"),
    path('login/', login, name="login")
]
