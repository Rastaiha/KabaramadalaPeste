from django.shortcuts import render
from django.urls import path

from .views import signup

urlpatterns = [
    path('signup/', signup, name="signup")
]
