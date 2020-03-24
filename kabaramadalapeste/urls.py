from django.urls import path
from .views import game, exchange


urlpatterns = [
    path('test_1234/', game, name="game"),
    path('exchange/', exchange, name="exchange"),
]
