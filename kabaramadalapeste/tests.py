from django.test import TestCase

# Create your tests here.
from kabaramadalapeste.models import ParticipantIslandStatus, Island
from kabaramadalapeste.factory import (
    ChallengeFactory, IslandFactory, ShortAnswerQuestionFactory
)
from accounts.factory import ParticipantFactory


class AssignQuestionTest(TestCase):

    def setUp(self):
        [ChallengeFactory() for i in range(4)]
        [IslandFactory() for i in range(8)]
        [ShortAnswerQuestionFactory() for i in range(30)]
        self.participant = ParticipantFactory()
        self.island = Island.objects.first()

    def test_assign_question_not_force(self):
        pis = ParticipantIslandStatus(
            participant=self.participant,
            island=self.island
        )
        pis.assign_question()
        old_question_object_id = pis.question_object_id
        for i in range(20):
            pis.assign_question()
            self.assertEqual(pis.question_object_id, old_question_object_id)

    def test_assign_question(self):
        same_challenge_island = Island.objects.filter(
            challenge=self.island.challenge,
        ).exclude(id=self.island.id).first()
        pis_old = pis = ParticipantIslandStatus(
            participant=self.participant,
            island=same_challenge_island,
            question=self.island.challenge.questions.first()
        )
        pis_old.save()
        pis = ParticipantIslandStatus(
            participant=self.participant,
            island=self.island
        )
        for i in range(20):
            pis.assign_question(force=True)
            self.assertNotEqual(pis_old.question_object_id, pis.question_object_id)
