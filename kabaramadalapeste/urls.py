from django.urls import path
from .views import game, exchange


urlpatterns = [
    path('', game),
    path('exchange/', exchange),
]
