from django.db import models


class Island(models.Model):
    island_id = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=50)
    challenge = models.ForeignKey('Challenge',
                                  on_delete=models.SET_NULL,
                                  blank=True,
                                  null=True)

    def __str__(self):
        return self.name


class Challenge(models.Model):
    name = models.CharField(max_length=50)
    is_judgeable = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class ChallengeRewardItem(models.Model):
    SEKKE = 'SK'
    KEY1 = 'K1'
    KEY2 = 'K2'
    KEY3 = 'K3'
    REWARD_TYPE_CHOICES = [
        (SEKKE, 'sekke'),
        (KEY1, 'key 1'),
        (KEY2, 'key 2'),
        (KEY3, 'key 3'),
    ]
    reward_type = models.CharField(
        max_length=2,
        choices=REWARD_TYPE_CHOICES,
        default=SEKKE,
    )
    amount = models.IntegerField(default=0)
    challenge = models.ForeignKey('Challenge',
                                  related_name='rewards',
                                  on_delete=models.SET_NULL,
                                  blank=True,
                                  null=True)

    def __str__(self):
        return '%s %s %s' % (
            self.challenge.name, self.reward_type, self.amount
        )

    class Meta:
        unique_together = (("challenge", "reward_type"),)


class BaseQuestion(models.Model):
    title = models.CharField(max_length=100)
    question = models.FileField(upload_to='soals/')

    challenge = models.ForeignKey('Challenge',
                                  related_name='%(class)s',
                                  on_delete=models.CASCADE)

    class Meta:
        abstract = True

    def __str__(self):
        return '%s for challenge: %s' % (
            self.title, self.challenge.name
        )


class ShortAnswerQuestion(BaseQuestion):
    INTEGER = 'INT'
    FLOAT = 'FLT'
    STRING = 'STR'
    ANSWER_TYPE_CHOICES = [
        (INTEGER, 'int'),
        (FLOAT, 'float'),
        (STRING, 'string')
    ]
    correct_answer = models.CharField(max_length=50)
    answer_type = models.CharField(
        max_length=3,
        choices=ANSWER_TYPE_CHOICES,
        default=STRING,
    )


class JudgeableQuestion(BaseQuestion):
    pass
