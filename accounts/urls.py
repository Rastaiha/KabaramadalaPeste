from django.shortcuts import render
from django.urls import path

from .views import signup, login, logout

urlpatterns = [
    path('signup/', signup, name="signup"),
    path('logout/', logout, name="logout"),
    path('login/', login, name="login")
]
