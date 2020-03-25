from django.shortcuts import render
from django.http import Http404, JsonResponse
from django.urls import reverse
from django.views import View
from django.utils.decorators import method_decorator

from django.contrib.auth.decorators import login_required, user_passes_test

from accounts.models import Participant

from kabaramadalapeste.models import Island, ParticipantIslandStatus, TradeOffer, TradeOfferRequestedItem, \
    TradeOfferSuggestedItem
from kabaramadalapeste.conf import settings

import datetime


def check_user_is_activated_participant(user):
    try:
        return user.is_participant and user.participant.is_activated,
    except Exception:
        return False


activated_participant_required = user_passes_test(
    check_user_is_activated_participant,
    login_url='/accounts/login'
)


def login_activated_participant_required(view_func):
    return login_required(activated_participant_required(view_func))


default_error_response = JsonResponse({
    'status': settings.ERROR_STATUS,
    'message': 'خطایی رخ داد. موضوع رو بهمون بگو.'
})


@method_decorator(login_activated_participant_required, name='dispatch')
class IslandInfoView(View):
    def get(self, request, island_id):
        try:
            island = Island.objects.get(island_id=island_id)
            pis = ParticipantIslandStatus.objects.get(participant=request.user.participant, island=island)
            return JsonResponse({
                'name': island.name,
                'challenge_name': island.challenge.name,
                'challenge_is_judgeable': island.challenge.is_judgeable,

                'did_open_treasure': pis.did_open_treasure,
                'participants_inside': ParticipantIslandStatus.objects.filter(
                    island=island, currently_anchored=True
                ).count(),
                'judge_estimated_minutes': 0,  # TODO: fill here
                'answer_status': '',  # TODO: fill here
            })
        except Exception:
            return default_error_response


@method_decorator(login_activated_participant_required, name='dispatch')
class SetStartIslandView(View):
    def post(self, request, dest_island_id):
        dest_island = Island.objects.get(island_id=dest_island_id)
        try:
            request.user.participant.set_start_island(dest_island)
            return JsonResponse({
                'status': settings.OK_STATUS
            })
        except Participant.CantResetStartIsland:
            return JsonResponse({
                'status': settings.ERROR_STATUS,
                'message': 'قبلا انتخاب کردی که از کدوم جزیره شروع کنی. نمی‌تونی دوباره انتخاب کنی.'
            })
        except Exception:
            return default_error_response


@method_decorator(login_activated_participant_required, name='dispatch')
class MoveToIslandView(View):
    def post(self, request, dest_island_id):
        dest_island = Island.objects.get(island_id=dest_island_id)
        try:
            request.user.participant.move(dest_island)
            return JsonResponse({
                'status': settings.OK_STATUS
            })
        except Participant.ParticipantIsNotOnIsland:
            return JsonResponse({
                'status': settings.ERROR_STATUS,
                'message': 'کشتیت روی جزیره‌ای نیست. نمی‌تونی حرکت کنی. اول انتخاب کن می‌خوای از کجا شروع کنی.'
            })
        except Island.IslandsNotConnected:
            return JsonResponse({
                'status': settings.ERROR_STATUS,
                'message': 'به جزیره‌ی مقصد از اینجا راه مستقیم نیست.'
            })
        except Participant.PropertiesAreNotEnough:
            return JsonResponse({
                'status': settings.ERROR_STATUS,
                'message': 'سکه‌هات برای حرکت کافی نیست.'
            })
        except Exception:
            return default_error_response


@method_decorator(login_activated_participant_required, name='dispatch')
class PutAnchorView(View):
    def post(self, request):
        try:
            request.user.participant.put_anchor_on_current_island()
            return JsonResponse({
                'status': settings.OK_STATUS
            })
        except Participant.ParticipantIsNotOnIsland:
            return JsonResponse({
                'status': settings.ERROR_STATUS,
                'message': 'کشتیت روی جزیره‌ای نیست. نمی‌تونی لنگر بندازی. اول انتخاب کن می‌خوای از کجا شروع کنی.'
            })
        except Participant.PropertiesAreNotEnough:
            return JsonResponse({
                'status': settings.ERROR_STATUS,
                'message': 'سکه‌هات برای لنگر انداختن کافی نیست.'
            })
        except Exception:
            return default_error_response


@login_activated_participant_required
def create_offer(request):
    if request.method == 'POST':
        try:
            if TradeOffer.objects.filter(
                creator_participant__member__username__exact=request.user.username,
                status__exact=settings.GAME_OFFER_ACTIVE
            ).count() >= settings.GAME_MAXIMUM_ACTIVE_OFFERS:
                raise Participant.MaximumActiveOffersExceeded
            suggested_types = []
            requested_types = []
            suggested_amounts = []
            requested_amounts = []
            for property_type in settings.GAME_PARTICIPANT_PROPERTY_TYPE_CHOICES:
                if 'requested_' + property_type in request.POST:
                    requested_types.append(property_type)
                    requested_amounts.append(request.POST['requested_' + property_type])
                if 'suggested_' + property_type in request.POST:
                    suggested_types.append(property_type)
                    suggested_amounts.append(request.POST['suggested_' + property_type])
            request.user.participant.reduce_multiple_property(suggested_types, suggested_amounts)
            trade_offer = TradeOffer.objects.create(
                creator_participant=request.user.participant,
                creation_datetime=datetime.datetime.now(),
                status=settings.GAME_OFFER_ACTIVE,
                accepted_participant=None,
                close_datetime=None
            )
            for i in range(len(suggested_types)):
                trade_suggested_item = TradeOfferSuggestedItem(
                    offer=trade_offer,
                    property_type=suggested_types[i],
                    amount=int(suggested_amounts[i])
                )
                trade_suggested_item.save()
            for i in range(len(requested_types)):
                trade_requested_item = TradeOfferRequestedItem(
                    offer=trade_offer,
                    property_type=requested_types[i],
                    amount=int(requested_amounts[i])
                )
                trade_requested_item.save()
            trade_offer.save()
            return JsonResponse({
                'status': settings.OK_STATUS
            })
        except Participant.MaximumActiveOffersExceeded:
            return JsonResponse({
                'status': settings.ERROR_STATUS,
                'message': 'به حداکثر تعداد پیش‌نهاداتت رسیدی.'
            })
        except Participant.PropertiesAreNotEnough:
            return JsonResponse({
                'status': settings.ERROR_STATUS,
                'message': 'منابع کافی برای دادن این پیشنهاد رو نداری.'
            })
        except Exception:
            return default_error_response


@login_activated_participant_required
def game(request):
    return render(request, 'kabaramadalapeste/game.html', {
        'without_nav': True,
        'without_footer': True,
    })


def game2(request):
    return render(request, 'kabaramadalapeste/game.html', {
        'without_nav': True,
        'without_footer': True,
        'low_q': True
    })


def exchange(request):
    return render(request, 'kabaramadalapeste/exchange.html', {
        'without_nav': True,
        'without_footer': True,
    })
