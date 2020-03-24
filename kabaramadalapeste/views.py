from django.shortcuts import render
from django.http import Http404, JsonResponse
from django.urls import reverse

from django.contrib.auth.decorators import login_required, user_passes_test

from kabaramadalapeste.models import Island, ParticipantIslandStatus


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


@login_activated_participant_required
def island_info(request, island_id):
    island = Island.objects.get(island_id=island_id)
    pis = ParticipantIslandStatus.objects.get(participant=request.user.participant, island=island)
    return JsonResponse({
        'name': island.name,
        'challenge_name': island.challenge.name,
        'challenge_is_judgeable': island.challenge.is_judgeable,

        'did_open_treasure': pis.did_open_treasure,
        'participants_inside': ParticipantIslandStatus.objects.count(island=island, currently_anchored=True),
        'judge_estimated_minutes': 0,  # TODO: fill here
        'answer_status': '',  # TODO: fill here
    })


@login_activated_participant_required
def game(request):
    return render(request, 'kabaramadalapeste/game.html', {
        'without_nav': True,
        'without_footer': True,
    })
