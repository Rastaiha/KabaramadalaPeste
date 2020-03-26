import factory
from kabaramadalapeste.models import (
    Island, Challenge, ShortAnswerQuestion, Treasure,
    TreasureKeyItem, TreasureRewardItem, JudgeableQuestion
)
from kabaramadalapeste.conf import settings


class IslandFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Island

    island_id = factory.Sequence(lambda n: n + 1)
    name = factory.LazyAttribute(lambda o: 'island %s' % o.island_id)

    challenge = factory.Iterator(Challenge.objects.all())


class ChallengeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Challenge

    challenge_id = factory.Sequence(lambda n: n + 1)
    name = factory.Faker('sentence', nb_words=3)
    is_judgeable = False


class ShortAnswerQuestionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ShortAnswerQuestion

    title = factory.Faker('sentence', nb_words=4)
    question = factory.django.FileField(filename='q.pdf')
    challenge = factory.Iterator(Challenge.objects.filter(is_judgeable=False))
    answer_type = 'STR'  # factory.Iterator(models.ShortAnswerQuestion.ANSWER_TYPE_CHOICES)
    correct_answer = 'javab'


class JudgeableQuestionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = JudgeableQuestion

    title = factory.Faker('sentence', nb_words=4)
    question = factory.django.FileField(filename='q.pdf')
    challenge = factory.Iterator(Challenge.objects.filter(is_judgeable=True))


class TreasureFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Treasure

    @factory.post_generation
    def keys(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return
        if extracted:
            assert isinstance(extracted, int)
            TreasureKeyItemFactory.create_batch(size=extracted, treasure_id=self.id, **kwargs)

    @factory.post_generation
    def rewards(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return
        if extracted:
            assert isinstance(extracted, int)
            TreasureRewardItem.create_batch(size=extracted, treasure_id=self.id, **kwargs)


class TreasureKeyItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TreasureKeyItem

    key_type = factory.Iterator(map(lambda x: x[0], settings.GAME_TREASURE_KEY_TYPE_CHOICES))
    amount = factory.Faker('pyint', min_value=1, max_value=5)


class TreasureRewardItem(factory.django.DjangoModelFactory):
    class Meta:
        model = TreasureRewardItem

    reward_type = factory.Iterator(map(lambda x: x[0], settings.GAME_TREASURE_REWARD_TYPE_CHOICES))
    amount = factory.Faker('pyint', min_value=1, max_value=5)
