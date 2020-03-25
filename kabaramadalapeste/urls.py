from django.urls import path
from .views import game, game2, exchange, jazire


urlpatterns = [
    path('test_1234/', game, name="game"),
    path('test_12345/', game2, name="game2"),
    path('exchange/', exchange, name="exchange"),
    path('jazire/', jazire, name="jazire"),
]
