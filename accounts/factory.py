import factory
from accounts.models import (
    Participant, Member
)


class MemberFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Member
    username = factory.Sequence(lambda n: n)


class ParticipantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Participant

    member = factory.SubFactory(MemberFactory)
