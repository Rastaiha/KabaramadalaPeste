from django.conf import settings
from appconf import AppConf


class GameConf(AppConf):
    SEKKE = 'SK'
    KEY1 = 'K1'
    KEY2 = 'K2'
    KEY3 = 'K3'

    TREASURE_KEY_TYPE_CHOICES = [
        (KEY1, 'key 1'),
        (KEY2, 'key 2'),
        (KEY3, 'key 3'),
    ]

    CHALLENGE_REWARD_TYPE_CHOICES = [
        (SEKKE, 'sekke'),
    ] + TREASURE_KEY_TYPE_CHOICES

    VISION = 'VIS'
    TRAVEL_EXPRESS = 'TXP'
    CHALLENGE_PLUS = 'CHP'
    PROPHECY = 'PRC'
    BULLY = 'BLY'

    ABILITY_TYPE_CHOICES = [
        (VISION, 'vision'),
        (TRAVEL_EXPRESS, 'travel express'),
        (CHALLENGE_PLUS, 'challenge plus'),
        (PROPHECY, 'prophecy'),
        (BULLY, 'bully'),
    ]

    TREASURE_REWARD_TYPE_CHOICES = [
        (SEKKE, 'sekke'),
    ] + TREASURE_KEY_TYPE_CHOICES + ABILITY_TYPE_CHOICES

    PARTICIPANT_PROPERTY_TYPE_CHOICES = TREASURE_REWARD_TYPE_CHOICES

    TRANSLATION_DICT = {
        SEKKE: 'سکه',
        KEY1: 'کلید نوع ۱',
        KEY2: 'کلید نوع ۲',
        KEY3: 'کلید نوع ۳',
        VISION: 'توانایی بینش غیبی',
        TRAVEL_EXPRESS: 'توانایی سفر اکسپرس',
        CHALLENGE_PLUS: 'توانایی چالش پلاس',
        BULLY: 'توانایی زورگیری'
    }

    PARTICIPANT_INITIAL_PROPERTIES = {
        SEKKE: 1500
    }

    MOVE_PRICE = 100
    PUT_ANCHOR_PRICE = 200

    BULLY_DAMAGE = 300

    DEFAULT_ISLAND_COUNT = 35
    BANDARGAH_ISLAND_ID = 20

    OFFER_DELETED = 'OD'
    OFFER_ACCEPTED = 'OA'
    OFFER_ACTIVE = 'OC'

    OFFER_STATUS_CHOICES = [
        (OFFER_DELETED, 'deleted'),
        (OFFER_ACCEPTED, 'accepted'),
        (OFFER_ACTIVE, 'active')
    ]

    MAXIMUM_ACTIVE_OFFERS = 4
    BASE_CHALLENGE_PER_DAY = 5

    class Meta:
        prefix = 'game'
