from django.shortcuts import render
from django.urls import path, re_path

from .views import signup, login, logout, send_request, verify, activate, survey

urlpatterns = [
    path('logout/', logout, name="logout"),
    path('', login, name="login")
]
