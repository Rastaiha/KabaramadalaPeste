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

    ABILITY_TYPY_CHOICES = [
        (VISION, 'vision'),
        (TRAVEL_EXPRESS, 'travel express'),
        (CHALLENGE_PLUS, 'challenge plus'),
        (PROPHECY, 'prophecy'),
        (BULLY, 'bully'),
    ]

    TREASURE_REWARD_TYPE_CHOICES = [
        (SEKKE, 'sekke'),
    ] + TREASURE_KEY_TYPE_CHOICES + ABILITY_TYPY_CHOICES

    class Meta:
        prefix = 'game'