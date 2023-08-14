from accounts.models import *
from django.db.models import Q, Count, Sum


def get_number_of_teams_traveling():
    return Team.objects.all().values("id", "group_name").annotate(
        sum_move=Count('participant__logs__id', filter=Q(participant__logs__event_type="Move"), distinct=True)).order_by('-sum_move')


def get_number_of_coins_of_each_team():
    return Team.objects.all().values("id", "group_name").annotate(
        sum_coin=Sum('participant__properties__amount', filter=Q(participant__properties__property_type="SK"))
    ).order_by('-sum_coin')


def get_number_of_bully_of_each_team():
    return Team.objects.all().values("id", "group_name").annotate(
        sum_BLY=Count('participant__logs__id', filter=Q(participant__logs__event_type="Bully target"), distinct=True)
    ).order_by('-sum_BLY')


def get_number_of_kheftgiri_of_each_team():
    return Team.objects.all().values("id", "group_name").annotate(
        count_BLY=Count('participant__member__notifications__id',
                        filter=Q(participant__member__notifications__verb="sb_fall_in_your_bully"), distinct=True)
    ).order_by('-count_BLY')


def get_number_of_challenge_of_each_team():
    return Team.objects.all().values("id", "group_name").annotate(
        count_challenge_accept=Count('participant__member__notifications__id',
                                     filter=Q(
                                         participant__member__notifications__verb="correct_judged_answer"
                                     ) | Q(
                                         participant__member__notifications__verb="correct_short_answer"),
                                     distinct=True)).order_by('-count_challenge_accept')
