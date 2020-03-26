from solo.models import SingletonModel
from django.db import models
from enum import Enum

import datetime


class TeamType(Enum):
    Technical = "فنی"
    Scientific = "علمی"
    Media = "رسانه"


class SiteConfiguration(SingletonModel):
    countdown_date = models.DateTimeField(default=datetime.datetime(2020, 3, 23, 8))
    is_signup_enabled = models.BooleanField(default=True)

    island_spade_cost = models.IntegerField(default=15000)
    peste_reward = models.IntegerField(default=30000)


class TeamMember(models.Model):
    full_name = models.CharField(max_length=50)
    team_type = models.CharField(
        max_length=10,
        default=TeamType.Technical,
        choices=[(tag.value, tag.name) for tag in TeamType])
    description = models.CharField(max_length=200, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', default='profiles/john_doe.jpeg')

    def __str__(self):
        return self.full_name
