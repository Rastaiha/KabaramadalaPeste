from django.urls import path
from .views import game, game2, exchange


urlpatterns = [
    path('test_1234/', game, name="game"),
    path('test_12345/', game2, name="game2"),
    path('exchange/', exchange, name="exchange"),
]
