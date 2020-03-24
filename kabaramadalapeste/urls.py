from django.urls import path
from .views import game, island_info


urlpatterns = [
    path('island_info/<int:island_id>', island_info),
    path('', game),
]
