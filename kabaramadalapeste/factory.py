import factory
from kabaramadalapeste.models import (
    Island, Challenge, ShortAnswerQuestion
)


class IslandFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Island

    island_id = factory.Sequence(lambda n: n)
    name = factory.LazyAttribute(lambda o: 'island %s' % o.island_id)

    challenge = factory.Iterator(Challenge.objects.all())


class ChallengeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Challenge

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
