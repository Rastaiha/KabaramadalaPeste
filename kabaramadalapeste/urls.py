from django.urls import path
from .views import (
    game, game2, exchange, IslandInfoView, MoveToIslandView,
    SetStartIslandView, PutAnchorView, create_offer
)


urlpatterns = [
    path('island_info/<int:island_id>', IslandInfoView.as_view(), name="island_info"),
    path('set_start_island/<int:dest_island_id>', SetStartIslandView.as_view(), name="set_start_island"),
    path('move_to/<int:dest_island_id>', MoveToIslandView.as_view(), name="move_to"),
    path('put_anchor', PutAnchorView.as_view(), name="put_anchor"),
    path('create_offer', create_offer, name="create_offer"),
    path('test_1234/', game, name="game"),
    path('test_12345/', game2, name="game2"),
    path('exchange/', exchange, name="exchange"),
]
