from django.db import models

# Create your models here.

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


class TeamMember(models.Model):
    full_name = models.CharField(max_length=50)
    team_type = models.CharField(
        max_length=10,
        default=TeamType.Technical,
        choices=[(tag.value, tag.name) for tag in TeamType])
    profile_picture = models.ImageField(upload_to='profiles/', default='profiles/john_doe.jpeg')

