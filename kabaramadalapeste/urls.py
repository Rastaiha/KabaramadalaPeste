from django.urls import path

from .views import (
    game, game2, exchange, island, ChallengeView, IslandInfoView, MoveToIslandView,
    SetStartIslandView, PutAnchorView, OpenTreasureView,
    ParticipantInfoView, create_offer, get_all_offers,
    get_my_offers, delete_offer, accept_offer,
    AcceptChallengeView, use_ability, SettingsView, SpadeView, invest
)


urlpatterns = [
    path('settings/',
         SettingsView.as_view(), name="settings"),
    path('island_info/<int:island_id>/',
         IslandInfoView.as_view(), name="island_info"),
    path('participant_info/', ParticipantInfoView.as_view(),
         name="participant_info"),

    path('set_start_island/<int:dest_island_id>/',
         SetStartIslandView.as_view(), name="set_start_island"),
    path('move_to/<int:dest_island_id>/',
         MoveToIslandView.as_view(), name="move_to"),
    path('put_anchor/', PutAnchorView.as_view(), name="put_anchor"),
    path('open_treasure/', OpenTreasureView.as_view(), name="open_treasure"),
    path('spade/', SpadeView.as_view(), name="spade"),
    path('accept_challenge/', AcceptChallengeView.as_view(),
         name="accept_challenge"),

    path('create_offer/', create_offer, name="create_offer"),
    path('get_all_offers/', get_all_offers, name="get_all_offers"),
    path('get_my_offers/', get_my_offers, name="get_my_offers"),
    path('delete_offer/<int:pk>/', delete_offer, name="delete_offer"),
    path('accept_offer/<int:pk>/', accept_offer, name="accept_offer"),

    path('use_ability', use_ability, name="use_ability"),

    path('invest', invest, name="invest_bandargah"),

    path('', game, name="game"),
    path('low/', game2, name="game2"),
    path('exchange/', exchange, name="exchange"),
    path('island/', island, name="island"),
    path('challenge/', ChallengeView.as_view(), name="challenge"),
]
