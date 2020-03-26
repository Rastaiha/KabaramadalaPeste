from django.shortcuts import render
from django.http import Http404, JsonResponse
from django.urls import reverse
from django.views import View
from django.utils.decorators import method_decorator
from django.db import transaction
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone

from accounts.models import Participant

from kabaramadalapeste.models import Island, ParticipantIslandStatus, TradeOffer, TradeOfferRequestedItem, \
    TradeOfferSuggestedItem, AbilityUsage
from kabaramadalapeste.conf import settings

import datetime
import sys
import logging

logger = logging.getLogger(__file__)


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
}, status=400)


@method_decorator(login_activated_participant_required, name='dispatch')
class SettingsView(View):
    def get(self, request):
        try:
            return JsonResponse({
                'move_price': settings.GAME_MOVE_PRICE,
                'put_anchor_price': settings.GAME_PUT_ANCHOR_PRICE
            })
        except Exception as e:
            logger.error(e, exc_info=True)
            return default_error_response


@method_decorator(login_activated_participant_required, name='dispatch')
class IslandInfoView(View):
    def get(self, request, island_id):
        try:
            island = Island.objects.get(island_id=island_id)
            pis = ParticipantIslandStatus.objects.get(
                participant=request.user.participant, island=island)
            treasure_keys = 'unknown'
            if pis.is_treasure_visible and pis.treasure:
                treasure_keys = {
                    key.key_type: key.amount for key in pis.treasure.keys.all()
                }
            submit_status = pis.submit.submit_status if pis.submit else 'No'
            return JsonResponse({
                'name': island.name,
                'challenge_name': island.challenge.name if island.challenge else '',
                'challenge_is_judgeable': island.challenge.is_judgeable if island.challenge else '',
                'treasure_keys': treasure_keys,
                'did_open_treasure': pis.did_open_treasure,
                'participants_inside': ParticipantIslandStatus.objects.filter(
                    island=island, currently_anchored=True
                ).count(),
                'judge_estimated_minutes': 0,  # TODO: fill here
                'submit_status': submit_status,
            })
        except Exception as e:
            logger.error(e, exc_info=True)
            return default_error_response


@method_decorator(login_activated_participant_required, name='dispatch')
class ParticipantInfoView(View):
    def get(self, request):
        try:
            properties_dict = {
                prop.property_type: prop.amount for prop in request.user.participant.properties.all()
            }
            current_island_id = None
            currently_anchored = False
            if request.user.participant.currently_at_island:
                current_island_id = request.user.participant.currently_at_island.island_id
                pis = ParticipantIslandStatus.objects.get(
                    participant=request.user.participant,
                    island=request.user.participant.currently_at_island
                )
                currently_anchored = pis.currently_anchored
            return JsonResponse({
                'username': request.user.username,
                'current_island_id': current_island_id,
                'currently_anchored': currently_anchored,
                'properties': properties_dict
            })
        except Exception as e:
            logger.error(e, exc_info=True)
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
            }, status=400)
        except Exception as e:
            logger.error(e, exc_info=True)
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
            }, status=400)
        except Island.IslandsNotConnected:
            return JsonResponse({
                'status': settings.ERROR_STATUS,
                'message': 'به جزیره‌ی مقصد از اینجا راه مستقیم نیست.'
            }, status=400)
        except Participant.PropertiesAreNotEnough:
            return JsonResponse({
                'status': settings.ERROR_STATUS,
                'message': 'سکه‌هات برای حرکت کافی نیست.'
            }, status=400)
        except Exception as e:
            logger.error(e, exc_info=True)
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
            }, status=400)
        except Participant.PropertiesAreNotEnough:
            return JsonResponse({
                'status': settings.ERROR_STATUS,
                'message': 'سکه‌هات برای لنگر انداختن کافی نیست.'
            }, status=400)
        except Participant.CantPutAnchorAgain:
            return JsonResponse({
                'status': settings.ERROR_STATUS,
                'message': 'روی این جزیره لنگر انداختی. نمی‌تونی دوباره لنگر بندازی.'
            }, status=400)
        except Exception as e:
            logger.error(e, exc_info=True)
            return default_error_response


@method_decorator(login_activated_participant_required, name='dispatch')
class OpenTreasureView(View):
    def post(self, request):
        try:
            request.user.participant.open_treasure_on_current_island()
            return JsonResponse({
                'status': settings.OK_STATUS
            })
        except Participant.ParticipantIsNotOnIsland:
            return JsonResponse({
                'status': settings.ERROR_STATUS,
                'message': 'کشتیت روی جزیره‌ای نیست. نمی‌تونی گنجش رو باز کنی. اول انتخاب کن می‌خوای از کجا شروع کنی.'
            }, status=400)
        except Participant.DidNotAnchored:
            return JsonResponse({
                'status': settings.ERROR_STATUS,
                'message': 'توی جزیره لنگر ننداختی. نمی‌تونی گنجش رو باز کنی. اول باید لنگر بندازی.'
            }, status=400)
        except Participant.PropertiesAreNotEnough:
            return JsonResponse({
                'status': settings.ERROR_STATUS,
                'message': 'دارایی‌هات برای باز کردن گنج کافی نیست.'
            }, status=400)
        except Exception as e:
            logger.error(e, exc_info=True)
            return default_error_response


@method_decorator(login_activated_participant_required, name='dispatch')
class AcceptChallengeView(View):
    def post(self, request):
        try:
            request.user.participant.accept_challenge_on_current_island()
            return JsonResponse({
                'status': settings.OK_STATUS
            })
        except Participant.ParticipantIsNotOnIsland:
            return JsonResponse({
                'status': settings.ERROR_STATUS,
                'message': 'کشتیت روی جزیره‌ای نیست. نمی‌تونی چالش رو بپذیری. اول انتخاب کن می‌خوای از کجا شروع کنی.'
            }, status=400)
        except Participant.DidNotAnchored:
            return JsonResponse({
                'status': settings.ERROR_STATUS,
                'message': 'توی جزیره لنگر ننداختی. نمی‌تونی چالشش رو بپذیری. اول باید لنگر بندازی.'
            }, status=400)
        except Participant.MaximumChallengePerDayExceeded:
            return JsonResponse({
                'status': settings.ERROR_STATUS,
                'message': 'تعداد چالش‌های روزت رو استفاده کردی. تا فردا نمی‌تونی چالش جدیدی بپذیری'
            }, status=400)
        except Exception as e:
            logger.error(e, exc_info=True)
            return default_error_response


@transaction.atomic
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
            for property_tuple in settings.GAME_PARTICIPANT_PROPERTY_TYPE_CHOICES:
                property_type = property_tuple[0]
                if 'requested_' + property_type in request.POST:
                    requested_types.append(property_type)
                    requested_amounts.append(
                        int(request.POST['requested_' + property_type]))
                if 'suggested_' + property_type in request.POST:
                    suggested_types.append(property_type)
                    suggested_amounts.append(
                        int(request.POST['suggested_' + property_type]))
            request.user.participant.reduce_multiple_property(
                suggested_types, suggested_amounts)
            trade_offer = TradeOffer.objects.create(
                creator_participant=request.user.participant,
                creation_datetime=timezone.now(),
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
            }, status=400)
        except Participant.PropertiesAreNotEnough:
            return JsonResponse({
                'status': settings.ERROR_STATUS,
                'message': 'منابع کافی برای دادن این پیشنهاد رو نداری.'
            }, status=400)
        except Exception as e:
            logger.error(e, exc_info=True)
            return default_error_response


@login_activated_participant_required
def get_all_offers(request):
    try:
        data = {'offers': []}
        for trade_offer in TradeOffer.objects.filter(status__exact=settings.GAME_OFFER_ACTIVE).order_by('?').all():
            data['offers'].append(trade_offer.to_dict())
        return JsonResponse(data)
    except Exception as e:
        logger.error(e, exc_info=True)
        return default_error_response


@login_activated_participant_required
def get_my_offers(request):
    try:
        data = {'offers': []}
        for trade_offer in TradeOffer.objects.filter(
            status__exact=settings.GAME_OFFER_ACTIVE,
            creator_participant__member__username__exact=request.user.username
        ).order_by('?').all():
            data['offers'].append(trade_offer.to_dict())
        return JsonResponse(data)
    except Exception as e:
        logger.error(e, exc_info=True)
        return default_error_response


@transaction.atomic
@login_activated_participant_required
def delete_offer(request, pk):
    try:
        trade_offer = TradeOffer.objects.get(
            pk=pk,
            creator_participant__member__username__exact=request.user.username
        )
        if trade_offer.status != settings.GAME_OFFER_ACTIVE:
            raise TradeOffer.InvalidOfferSelected
        for suggested_item in trade_offer.suggested_items.all():
            request.user.participant.add_property(
                suggested_item.property_type, suggested_item.amount)
        trade_offer.status = settings.GAME_OFFER_DELETED
        trade_offer.close_datetime = timezone.now()
        trade_offer.save()
        return JsonResponse({
            'status': settings.OK_STATUS
        })
    except TradeOffer.InvalidOfferSelected:
        return JsonResponse({
            'status': settings.ERROR_STATUS,
            'message': 'این پیشنهاد رو نمی‌تونی حذف کنی!'
        }, status=400)
    except Exception as e:
        logger.error(e, exc_info=True)
        return default_error_response


@transaction.atomic
@login_activated_participant_required
def accept_offer(request, pk):
    try:
        trade_offer = TradeOffer.objects.get(
            pk=pk,
        )
        if trade_offer.creator_participant.member.username == request.user.username:
            raise TradeOffer.InvalidOfferSelected
        if trade_offer.status != settings.GAME_OFFER_ACTIVE:
            raise TradeOffer.InvalidOfferSelected
        requested_types = []
        requested_amounts = []
        for requested_item in trade_offer.requested_items.all():
            requested_types.append(requested_item.property_type)
            requested_amounts.append(requested_item.amount)
        request.user.participant.reduce_multiple_property(
            requested_types, requested_amounts)
        for suggested_item in trade_offer.suggested_items.all():
            request.user.participant.add_property(
                suggested_item.property_type, suggested_item.amount)
        for requested_item in trade_offer.requested_items.all():
            trade_offer.creator_participant.add_property(
                requested_item.property_type, requested_item.amount)
        trade_offer.status = settings.GAME_OFFER_ACCEPTED
        trade_offer.accepted_participant = request.user.participant
        trade_offer.close_datetime = timezone.now()
        trade_offer.save()
        return JsonResponse({
            'status': settings.OK_STATUS
        })
    except TradeOffer.InvalidOfferSelected:
        return JsonResponse({
            'status': settings.ERROR_STATUS,
            'message': 'این پیشنهاد رو نمی‌تونی قبول کنی!'
        }, status=400)
    except Participant.PropertiesAreNotEnough:
        return JsonResponse({
            'status': settings.ERROR_STATUS,
            'message': 'منابع کافی برای قبول کردن این پیشنهاد رو نداری.'
        }, status=400)
    except Exception as e:
        logger.error(e, exc_info=True)
        return default_error_response


@transaction.atomic
@login_activated_participant_required
def use_ability(request):
    if request.method == 'POST':
        try:
            current_island = request.user.participant.get_current_island()
            ability_type = request.POST.get('ability_type')
            if ability_type not in [ability_tuple[0] for ability_tuple in settings.GAME_ABILITY_TYPE_CHOICES]:
                raise AbilityUsage.InvalidAbility
            request.user.participant.reduce_property(ability_type, 1)
            ability_usage = AbilityUsage.objects.create(
                datetime=timezone.now(),
                participant=request.user.participant,
                ability_type=ability_type
            )

            if ability_type == settings.GAME_TRAVEL_EXPRESS:
                ability_usage.is_active = True

            if ability_type == settings.GAME_VISION:
                islands = [current_island] + [island for island in current_island.neighbors]
                for island in islands:
                    pis = ParticipantIslandStatus.objects.get(
                        participant=request.user.participant,
                        island=island
                    )
                    pis.is_treasure_visible = True
                    pis.save()
            #TODO need to fill this part for bully & prophecy
            ability_usage.save()
            return JsonResponse({
                'status': settings.OK_STATUS
            })
        except AbilityUsage.InvalidAbility:
            return JsonResponse({
                'status': settings.ERROR_STATUS,
                'message': 'باید یک توانایی مجاز انتخاب کنی.'
            })
        except Participant.ParticipantIsNotOnIsland:
            return JsonResponse({
                'status': settings.ERROR_STATUS,
                'message': 'کشتیت روی جزیره‌ای نیست. باید اول انتخاب کنی می‌خوای از کجا شروع کنی.'
            })
        except Participant.PropertiesAreNotEnough:
            return JsonResponse({
                'status': settings.ERROR_STATUS,
                'message': 'از این توانایی چیزی برای مصرف نداری.'
            })
        except Exception as e:
            logger.error(e, exc_info=True)
            return default_error_response


@login_activated_participant_required
def game(request):
    return render(request, 'kabaramadalapeste/game.html', {
        'without_nav': True,
        'without_footer': True,
    })


@login_activated_participant_required
def game2(request):
    return render(request, 'kabaramadalapeste/game.html', {
        'without_nav': True,
        'without_footer': True,
        'low_q': True
    })


@login_activated_participant_required
def exchange(request):
    return render(request, 'kabaramadalapeste/exchange.html', {
        'without_nav': True,
        'without_footer': True,
    })


@login_activated_participant_required
def island(request):
    return render(request, 'kabaramadalapeste/island.html', {
        'without_nav': True,
        'without_footer': True,
    })
