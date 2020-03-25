from django.urls import path
from .views import (
    game, game2, exchange, IslandInfoView, MoveToIslandView,
    SetStartIslandView, PutAnchorView, OpenTreasureView,
    ParticipantInfoView
)


urlpatterns = [
    path('island_info/<int:island_id>', IslandInfoView.as_view(), name="island_info"),
    path('participant_info', ParticipantInfoView.as_view(), name="participant_info"),
    path('set_start_island/<int:dest_island_id>', SetStartIslandView.as_view(), name="set_start_island"),
    path('move_to/<int:dest_island_id>', MoveToIslandView.as_view(), name="move_to"),
    path('put_anchor', PutAnchorView.as_view(), name="put_anchor"),
    path('open_treasure', OpenTreasureView.as_view(), name="open_treasure"),
    path('test_1234/', game, name="game"),
    path('test_12345/', game2, name="game2"),
    path('exchange/', exchange, name="exchange"),
]
