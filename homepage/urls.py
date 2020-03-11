from django.shortcuts import render
from django.urls import path

from .views import homepage

urlpatterns = [
    path('', homepage, name="homepage"),
    path('test_auth_base/', lambda r: render(r, 'auth/base.html', {
        "without_nav": True
    })),
]
