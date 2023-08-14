from kabaramadalapeste.models import Participant
from django.utils import timezone
from datetime import timedelta


class ParticipantsDataCache:
    data = {}
    last_calculated = None
    seconds_between = 60

    @classmethod
    def clear(cls):
        cls.last_calculated = None

    @classmethod
    def calc_data(cls):
        data = {}
        for par in Participant.objects.filter(is_activated=True, document_status='Verified').exclude(currently_at_island__isnull=True):
            data[par.pk] = {
                'un': par.team_name,
                'pp': par.picture_url,
                'ii': par.currently_at_island.island_id if par.currently_at_island else None
            }
        return data

    @classmethod
    def get_data(cls):
        if cls.last_calculated is None or (timezone.now() - cls.last_calculated).seconds > cls.seconds_between:
            cls.data = cls.calc_data()
            cls.last_calculated = timezone.now()
        return cls.data
