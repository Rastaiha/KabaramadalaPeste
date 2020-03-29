from django.shortcuts import render, redirect
from django.http import Http404, JsonResponse
from django.urls import reverse
from django.views import View
from django.utils.decorators import method_decorator
from django.db import transaction
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.contrib.sites.shortcuts import get_current_site
from accounts.models import Participant

from kabaramadalapeste.cache import ParticipantsDataCache
from kabaramadalapeste.models import (
    Island, ParticipantIslandStatus, TradeOffer, TradeOfferRequestedItem, PesteConfiguration,
    TradeOfferSuggestedItem, AbilityUsage, BandargahInvestment, BandargahConfiguration, Bully,
    ShortAnswerQuestion, JudgeableSubmit, ShortAnswerSubmit, BaseSubmit, Peste, GameEventLog
)
from kabaramadalapeste.conf import settings
from kabaramadalapeste.forms import (
    EmptySubmitForm, ShortStringSubmitForm, ShortIntSubmitForm,
    ShortFloatSubmitForm, JudgeableFileSubmitForm, ProfilePictureUploadForm
)

from homepage.models import SiteConfiguration

import datetime
import sys
import logging

logger = logging.getLogger(__file__)


def check_user_is_activated_participant(user):
    try:
        return user.is_participant and user.participant.is_activated and user.participant.document_status == 'Verified'
    except Exception:
        return False


activated_participant_required = user_passes_test(
    check_user_is_activated_participant,
    login_url='/accounts/login'
)


def login_activated_participant_required(view_func):
    return login_required(activated_participant_required(view_func))


def check_game_is_running(user):
    return SiteConfiguration.get_solo().is_game_running


game_running_required = user_passes_test(
    check_game_is_running,
    login_url='/'
)


default_error_response = JsonResponse({
    'status': settings.ERROR_STATUS,
    'message': 'خطایی رخ داد. موضوع رو بهمون بگو.'
}, status=400)


@method_decorator(game_running_required, name='dispatch')
@method_decorator(login_activated_participant_required, name='dispatch')
class SettingsView(View):
    def get(self, request):
        try:
            return JsonResponse({
                'move_price': settings.GAME_MOVE_PRICE,
                'put_anchor_price': settings.GAME_PUT_ANCHOR_PRICE,
                'island_spade_cost': PesteConfiguration.get_solo().island_spade_cost
            })
        except Exception as e:
            logger.error(e, exc_info=True)
            return default_error_response


@method_decorator(game_running_required, name='dispatch')
@method_decorator(login_activated_participant_required, name='dispatch')
class IslandInfoView(View):
    def get(self, request, island_id):
        try:
            island = Island.objects.get(island_id=island_id)
            pis = ParticipantIslandStatus.objects.get(
                participant=request.user.participant, island=island)
            treasure_keys = 'unknown'
            treasure_keys_persian = 'مشخص نیست'
            if pis.is_treasure_visible and pis.treasure:
                treasure_keys = {
                    key.key_type: key.amount for key in pis.treasure.keys.all()
                }
                treasure_keys_persian = pis.treasure.get_keys_persian_string()
            submit_status = pis.submit.submit_status if pis.submit else 'No'
            estimated_judge_time = 15
            if not pis.island.challenge or not pis.island.challenge.is_judgeable:
                estimated_judge_time = 0
            submits = JudgeableSubmit.objects.exclude(submit_status='Pending').filter(pis__island__island_id=island_id).all()
            if submits.count() > 0:
                s = 0
                t = 0
                for submit in submits:
                    s += (submit.judged_at - submit.submitted_at).seconds//60
                    t += 1
                estimated_judge_time = 5 + s//t
            return JsonResponse({
                'name': island.name,
                'challenge_name': island.challenge.name if island.challenge else '',
                'challenge_is_judgeable': island.challenge.is_judgeable if island.challenge else '',
                'treasure_keys': treasure_keys,
                'treasure_keys_persian': treasure_keys_persian,
                'did_open_treasure': pis.did_open_treasure,
                'did_accept_challenge': pis.did_accept_challenge,
                'currently_anchored': pis.currently_anchored,
                'did_spade': pis.did_spade,
                'participants_inside': ParticipantIslandStatus.objects.filter(
                    island=island, currently_anchored=True
                ).count(),
                'is_spade_available': PesteConfiguration.get_solo().is_peste_available,
                'judge_estimated_minutes': estimated_judge_time,
                'submit_status': submit_status,
            })
        except Exception as e:
            logger.error(e, exc_info=True)
            return default_error_response


@method_decorator(game_running_required, name='dispatch')
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
                'picture_url': request.user.participant.picture_url,
                'did_won_peste': request.user.participant.did_won_peste(),
                'current_island_id': current_island_id,
                'currently_anchored': currently_anchored,
                'properties': properties_dict,
                'has_free_travel': AbilityUsage.objects.filter(
                        participant=request.user.participant,
                        ability_type=settings.GAME_TRAVEL_EXPRESS,
                        is_active=True
                    ).all().count() > 0
            })
        except Exception as e:
            logger.error(e, exc_info=True)
            return default_error_response


@method_decorator(game_running_required, name='dispatch')
@method_decorator(login_activated_participant_required, name='dispatch')
class AllParticipantsInfoView(View):
    def get(self, request):
        try:
            data = ParticipantsDataCache.get_data().copy()
            del(data[request.user.participant.pk])
            return JsonResponse(list(data.values()), safe=False)
        except Exception as e:
            logger.error(e, exc_info=True)
            return default_error_response


@method_decorator(game_running_required, name='dispatch')
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


@method_decorator(game_running_required, name='dispatch')
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


@method_decorator(game_running_required, name='dispatch')
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


@method_decorator(game_running_required, name='dispatch')
@method_decorator(login_activated_participant_required, name='dispatch')
class OpenTreasureView(View):
    def post(self, request):
        try:
            request.user.participant.open_treasure_on_current_island()
            pis = ParticipantIslandStatus.objects.get(
                participant=request.user.participant,
                island=request.user.participant.currently_at_island
            )
            treasure_rewards = {
                reward_item.reward_type: reward_item.amount for reward_item in pis.treasure.rewards.all()
            }
            return JsonResponse({
                'status': settings.OK_STATUS,
                'treasure_rewards': treasure_rewards,
                'treasure_rewards_persian': pis.treasure.get_rewards_persian_string()
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
        except Participant.CantOpenTreasureAgain:
            return JsonResponse({
                'status': settings.ERROR_STATUS,
                'message': 'قبلا این گنج رو باز کردی. نمیشه دوباره باز کنی.'
            }, status=400)
        except Exception as e:
            logger.error(e, exc_info=True)
            return default_error_response


@method_decorator(game_running_required, name='dispatch')
@method_decorator(login_activated_participant_required, name='dispatch')
class SpadeView(View):
    def post(self, request):
        try:
            found = request.user.participant.spade_on_current_island()
            return JsonResponse({
                'status': settings.OK_STATUS,
                'found': found
            })
        except Peste.PesteNotAvailable:
            return JsonResponse({
                'status': settings.ERROR_STATUS,
                'message': 'قابلیت کندوکاو در روز اول فعال نیست.'
            }, status=400)
        except Participant.ParticipantIsNotOnIsland:
            return JsonResponse({
                'status': settings.ERROR_STATUS,
                'message': 'کشتیت روی جزیره‌ای نیست. نمی‌تونی بیل بزنی. اول انتخاب کن می‌خوای از کجا شروع کنی.'
            }, status=400)
        except Participant.DidNotAnchored:
            return JsonResponse({
                'status': settings.ERROR_STATUS,
                'message': 'توی جزیره لنگر ننداختی. نمی‌تونی بیل بزنی. اول باید لنگر بندازی.'
            }, status=400)
        except Participant.PropertiesAreNotEnough:
            return JsonResponse({
                'status': settings.ERROR_STATUS,
                'message': 'دارایی‌هات برای بیل زدن کافی نیست.'
            }, status=400)
        except Participant.CantSpadeAgain:
            return JsonResponse({
                'status': settings.ERROR_STATUS,
                'message': 'قبلا اینجا رو بیل زدی. نمیشه دوباره بیل بزنی.'
            }, status=400)
        except Exception as e:
            logger.error(e, exc_info=True)
            return default_error_response


@method_decorator(game_running_required, name='dispatch')
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
        except Participant.CantAcceptChallengeAgain:
            return JsonResponse({
                'status': settings.ERROR_STATUS,
                'message': 'قبلا این چالش رو پذیرفتی. نمیشه دوباره بپذیریش.'
            }, status=400)
        except Exception as e:
            logger.error(e, exc_info=True)
            return default_error_response


@transaction.atomic
@game_running_required
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
            GameEventLog.objects.create(
                who=request.user.participant,
                when=timezone.now(),
                where=None,
                event_type=GameEventLog.EventTypes.CreateOffer,
                related=trade_offer
            )
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


@game_running_required
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


@game_running_required
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
@game_running_required
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
        GameEventLog.objects.create(
            who=request.user.participant,
            when=timezone.now(),
            where=None,
            event_type=GameEventLog.EventTypes.DeleteOffer,
            related=trade_offer
        )
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
@game_running_required
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
        GameEventLog.objects.create(
            who=request.user.participant,
            when=timezone.now(),
            where=None,
            event_type=GameEventLog.EventTypes.AcceptOffer,
            related=trade_offer
        )
        trade_offer.creator_participant.send_msg_offer_accepted(trade_offer)
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
@game_running_required
@login_activated_participant_required
def use_ability(request):
    if request.method == 'POST':
        try:
            current_island = request.user.participant.get_current_island()
            ability_type = request.POST.get('ability_type')
            if ability_type not in [ability_tuple[0] for ability_tuple in settings.GAME_ABILITY_TYPE_CHOICES]:
                raise AbilityUsage.InvalidAbility
            if ability_type == settings.GAME_BULLY:
                if current_island.island_id == settings.GAME_BANDARGAH_ISLAND_ID:
                    raise Bully.CantBeOnBandargah
                pis = ParticipantIslandStatus.objects.get(
                    participant=request.user.participant,
                    island=current_island
                )
                if not pis.currently_anchored:
                    raise Participant.DidNotAnchored
            request.user.participant.reduce_property(ability_type, 1)
            ability_usage = AbilityUsage.objects.create(
                datetime=timezone.now(),
                participant=request.user.participant,
                ability_type=ability_type
            )

            if ability_type == settings.GAME_TRAVEL_EXPRESS:
                ability_usage.is_active = True

            if ability_type == settings.GAME_VISION:
                islands = [current_island] + \
                    [island for island in current_island.neighbors]
                for island in islands:
                    pis = ParticipantIslandStatus.objects.get(
                        participant=request.user.participant,
                        island=island
                    )
                    pis.is_treasure_visible = True
                    pis.save()

            if ability_type == settings.GAME_BULLY:
                active_bullies = Bully.objects.filter(
                    island=current_island,
                    is_expired=False
                )
                for active_bully in active_bullies:
                    active_bully.expired_datetime = timezone.now()
                    active_bully.is_expired = True
                    active_bully.owner.send_msg_bully_expired(active_bully)
                bully = Bully.objects.create(
                    owner=request.user.participant,
                    is_expired=False,
                    island=current_island,
                    creation_datetime=timezone.now()
                )
                bully.save()
            ability_usage.save()
            GameEventLog.objects.create(
                who=request.user.participant,
                when=timezone.now(),
                where=current_island,
                event_type=GameEventLog.EventTypes.UseAbility,
                related=ability_usage
            )
            return JsonResponse({
                'status': settings.OK_STATUS
            })
        except AbilityUsage.InvalidAbility:
            return JsonResponse({
                'status': settings.ERROR_STATUS,
                'message': 'باید یک توانایی مجاز انتخاب کنی.'
            }, status=400)
        except Participant.ParticipantIsNotOnIsland:
            return JsonResponse({
                'status': settings.ERROR_STATUS,
                'message': 'کشتیت روی جزیره‌ای نیست. باید اول انتخاب کنی می‌خوای از کجا شروع کنی.'
            }, status=400)
        except Participant.PropertiesAreNotEnough:
            return JsonResponse({
                'status': settings.ERROR_STATUS,
                'message': 'از این توانایی چیزی برای مصرف نداری.'
            }, status=400)
        except Bully.CantBeOnBandargah:
            return JsonResponse({
                'status': settings.ERROR_STATUS,
                'message': 'این توانایی رو نمی‌تونی توی بندرگاه استفاده کنی.'
            }, status=400)
        except Participant.DidNotAnchored:
            return JsonResponse({
                'status': settings.ERROR_STATUS,
                'message': 'برای استفاده از این توانایی باید لنگر انداخته باشی.'
            }, status=400)
        except Exception as e:
            logger.error(e, exc_info=True)
            return default_error_response


@transaction.atomic
@game_running_required
@login_activated_participant_required
def invest(request):
    if request.method == 'POST':
        try:
            current_island = request.user.participant.get_current_island()
            if current_island.island_id != settings.GAME_BANDARGAH_ISLAND_ID:
                raise BandargahInvestment.LocationIsNotBandargah
            amount = int(request.POST.get('amount'))
            if amount > BandargahConfiguration.get_solo().max_possible_invest:
                raise BandargahInvestment.InvalidAmount
            if amount < BandargahConfiguration.get_solo().min_possible_invest:
                raise BandargahInvestment.InvalidAmount
            today_begin = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_begin + datetime.timedelta(days=1)
            if BandargahInvestment.objects.filter(
                participant=request.user.participant,
                datetime__gte=today_begin,
                datetime__lt=today_end,
            ).count() > 0:
                raise BandargahInvestment.CantInvestTwiceToday
            request.user.participant.reduce_property(
                settings.GAME_SEKKE, amount)
            investment = BandargahInvestment.objects.create(
                participant=request.user.participant,
                amount=amount,
                datetime=timezone.now(),
                is_applied=False
            )
            investment.save()
            GameEventLog.objects.create(
                who=request.user.participant,
                when=timezone.now(),
                where=current_island,
                event_type=GameEventLog.EventTypes.Invest,
                related=investment
            )
            return JsonResponse({
                'status': settings.OK_STATUS
            })
        except Participant.ParticipantIsNotOnIsland:
            return JsonResponse({
                'status': settings.ERROR_STATUS,
                'message': 'کشتیت روی جزیره‌ای نیست. باید اول انتخاب کنی می‌خوای از کجا شروع کنی.'
            }, status=400)
        except BandargahInvestment.LocationIsNotBandargah:
            return JsonResponse({
                'status': settings.ERROR_STATUS,
                'message': 'الان روی بندرگاه نیستی. باید اول به بندرگاه بری.'
            }, status=400)
        except BandargahInvestment.InvalidAmount:
            return JsonResponse({
                'status': settings.ERROR_STATUS,
                'message': 'مقدار سرمایه‌گذاری درست نیست. مقدار سرمایه‌گذاری باید در بازه‌ی معتبر باشه!'
            }, status=400)
        except BandargahInvestment.CantInvestTwiceToday:
            return JsonResponse({
                'status': settings.ERROR_STATUS,
                'message': 'امروز قبلا سرمایه‌گذاری کردی! روزی فقط یه بار می‌تونی سرمایه‌گذاری کنی.'
            }, status=400)
        except Participant.PropertiesAreNotEnough:
            return JsonResponse({
                'status': settings.ERROR_STATUS,
                'message': 'این مقدار سکه برای سرمایه‌گذاری نداری.'
            }, status=400)
        except Exception as e:
            logger.error(e, exc_info=True)
            return default_error_response


@game_running_required
@login_activated_participant_required
def game(request):
    return render(request, 'kabaramadalapeste/game.html', {
        'without_nav': True,
        'without_footer': True,
    })


@game_running_required
@login_activated_participant_required
def game2(request):
    return render(request, 'kabaramadalapeste/game.html', {
        'without_nav': True,
        'without_footer': True,
        'low_q': True
    })


@game_running_required
@login_activated_participant_required
def exchange(request):
    return render(request, 'kabaramadalapeste/exchange.html', {
        'without_nav': True,
        'without_footer': True,
    })


@game_running_required
@login_activated_participant_required
def island(request):
    try:
        pis = ParticipantIslandStatus.objects.get(
            participant=request.user.participant,
            island=request.user.participant.get_current_island()
        )
        if not pis.currently_anchored:
            raise Participant.DidNotAnchored
        return render(request, 'kabaramadalapeste/island.html', {
            'without_nav': True,
            'without_footer': True,
        })
    except (Participant.ParticipantIsNotOnIsland, Participant.DidNotAnchored):
        return redirect('kabaramadalapeste:game')
    except Exception as e:
        logger.error(e, exc_info=True)
        return redirect('kabaramadalapeste:game')


@login_activated_participant_required
def set_picture(request):
    if request.method == 'POST':
        form = ProfilePictureUploadForm(request.POST, request.FILES)
        if not form.is_valid():
            return redirect('kabaramadalapeste:game')
        request.user.participant.picture = form.cleaned_data['picture']
        request.user.participant.save()
    return redirect('kabaramadalapeste:game')


@method_decorator(game_running_required, name='dispatch')
@method_decorator(login_activated_participant_required, name='dispatch')
class ChallengeView(View):
    def _perform_after_general_checks(self, request, perform_func):
        try:
            pis = ParticipantIslandStatus.objects.get(
                participant=request.user.participant,
                island=request.user.participant.get_current_island()
            )
            if not pis.currently_anchored:
                raise Participant.DidNotAnchored
            if not pis.did_accept_challenge:
                raise Participant.DidNotAcceptChallenge
            if pis.submit:
                raise Participant.CantSubmitChallengeAgain

            return perform_func(request, pis)

        except (Participant.ParticipantIsNotOnIsland, Participant.DidNotAnchored):
            return redirect('kabaramadalapeste:game')
        except (Participant.DidNotAcceptChallenge, Participant.CantSubmitChallengeAgain):
            return redirect('kabaramadalapeste:island')
        except Exception as e:
            logger.error(e, exc_info=True)
            return redirect('kabaramadalapeste:island')

    def _perform_get(self, request, pis):
        return render(request, 'kabaramadalapeste/challenge.html', {
            'without_nav': True,
            'without_footer': True,
            'question_title': pis.question.title,
            'question_pdf_file': request.build_absolute_uri(pis.question.question.url),
            'question_pdf_file_without_http': ''.join([get_current_site(request).domain, pis.question.question.url]),
            'answer_type': pis.question.get_answer_type()
        })

    def get(self, request):
        return self._perform_after_general_checks(request, self._perform_get)

    @transaction.atomic
    def _perform_post(self, request, pis):
        answer_type_forms = {
            'NO': EmptySubmitForm,
            'FILE': JudgeableFileSubmitForm,
            ShortAnswerQuestion.STRING: ShortStringSubmitForm,
            ShortAnswerQuestion.INTEGER: ShortIntSubmitForm,
            ShortAnswerQuestion.FLOAT: ShortFloatSubmitForm,
        }
        answer_type = pis.question.get_answer_type()
        form = answer_type_forms[answer_type](request.POST, request.FILES)
        if not form.is_valid():
            logger.error(form.errors)
            return redirect('kabaramadalapeste:challenge')

        submit_type_classes = {
            'NO': JudgeableSubmit,
            'FILE': JudgeableSubmit,
            ShortAnswerQuestion.STRING: ShortAnswerSubmit,
            ShortAnswerQuestion.INTEGER: ShortAnswerSubmit,
            ShortAnswerQuestion.FLOAT: ShortAnswerSubmit,
        }
        SubmitClass = submit_type_classes[answer_type]
        submit = SubmitClass.objects.create(
            pis=pis,
            submitted_at=timezone.now()
        )
        if answer_type != 'NO':
            submit.submitted_answer = form.cleaned_data['answer']
        if answer_type not in ('NO', 'FILE'):
            submit.check_answer()
            if submit.submit_status == BaseSubmit.SubmitStatus.Correct:
                submit.give_rewards_to_participant()
                request.user.participant.send_msg_correct_short_answer(submit)
            elif submit.submit_status == BaseSubmit.SubmitStatus.Wrong:
                request.user.participant.send_msg_wrong_short_answer(submit)
        submit.save()
        GameEventLog.objects.create(
            who=request.user.participant,
            when=timezone.now(),
            where=pis.island,
            event_type=GameEventLog.EventTypes.Submit,
            related=submit
        )
        return redirect('kabaramadalapeste:island')

    def post(self, request):
        return self._perform_after_general_checks(request, self._perform_post)
