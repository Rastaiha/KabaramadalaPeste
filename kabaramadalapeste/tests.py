from django.test import TestCase
from django.urls import reverse

# Create your tests here.
from kabaramadalapeste.models import ParticipantIslandStatus, Island, Way
from kabaramadalapeste.factory import (
    ChallengeFactory, IslandFactory, ShortAnswerQuestionFactory, TreasureFactory
)
from kabaramadalapeste.conf import settings
from accounts.factory import ParticipantFactory


class AssignQuestionTest(TestCase):

    def setUp(self):
        [ChallengeFactory() for i in range(10)]
        [IslandFactory(__sequence=i) for i in range(settings.GAME_DEFAULT_ISLAND_COUNT)]
        [TreasureFactory(keys=2, rewards=3) for i in range(settings.GAME_DEFAULT_ISLAND_COUNT - 1)]
        [ShortAnswerQuestionFactory() for i in range(60)]
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


class ViewsTest(TestCase):
    def setUp(self):
        [ChallengeFactory() for i in range(10)]
        self.all_islands = [IslandFactory(__sequence=i) for i in range(settings.GAME_DEFAULT_ISLAND_COUNT)]
        [TreasureFactory(keys=2, rewards=3) for i in range(settings.GAME_DEFAULT_ISLAND_COUNT - 1)]
        self.island = self.all_islands[0]
        for i in range(3, 7):
            Way.objects.create(
                first_end=self.island,
                second_end=self.all_islands[i]
            )
        [ShortAnswerQuestionFactory() for i in range(60)]
        self.all_participants = [ParticipantFactory() for i in range(10)]
        for participant in self.all_participants:
            participant.init_pis()
            participant.init_properties()
        self.participant = self.all_participants[0]

    def test_island_info_not_login(self):
        response = self.client.get(reverse('kabaramadalapeste:island_info', kwargs={
            'island_id': self.island.island_id
        }))
        self.assertEqual(response.status_code, 302)

    def test_island_info(self):
        for i in range(4, 8):
            self.all_participants[i].set_start_island(self.island)
            self.all_participants[i].put_anchor_on_current_island()
        self.client.force_login(self.participant.member)
        response = self.client.get(reverse('kabaramadalapeste:island_info', kwargs={
            'island_id': self.island.island_id
        }))
        self.assertIsNotNone(response.json()['name'])
        self.assertIsNotNone(response.json()['challenge_name'])
        self.assertEqual(response.json()['participants_inside'], 4)

    def test_participant_info_not_login(self):
        response = self.client.get(reverse('kabaramadalapeste:participant_info'))
        self.assertEqual(response.status_code, 302)

    def test_participant_info_ok(self):
        self.client.force_login(self.participant.member)
        response = self.client.get(reverse('kabaramadalapeste:participant_info'))
        self.assertEqual(response.json()['username'], self.participant.member.username)
        for key, value in settings.GAME_PARTICIPANT_INITIAL_PROPERTIES.items():
            self.assertEqual(response.json()['properties'][key], value)

    def test_set_start_island_not_login(self):
        response = self.client.post(reverse('kabaramadalapeste:set_start_island', kwargs={
            'dest_island_id': self.island.island_id
        }))
        self.assertEqual(response.status_code, 302)

    def test_set_start_island_ok(self):
        self.client.force_login(self.participant.member)
        response = self.client.post(reverse('kabaramadalapeste:set_start_island', kwargs={
            'dest_island_id': self.island.island_id
        }))
        self.assertEqual(response.json()['status'], settings.OK_STATUS)

    def test_set_start_island_second_time(self):
        self.client.force_login(self.participant.member)
        self.client.post(reverse('kabaramadalapeste:set_start_island', kwargs={
            'dest_island_id': self.island.island_id
        }))
        response = self.client.post(reverse('kabaramadalapeste:set_start_island', kwargs={
            'dest_island_id': self.all_islands[4].island_id
        }))
        self.assertEqual(response.json()['status'], settings.ERROR_STATUS)

    def test_move_to_not_login(self):
        response = self.client.get(reverse('kabaramadalapeste:move_to', kwargs={
            'dest_island_id': self.island.island_id
        }))
        self.assertEqual(response.status_code, 302)

    def test_move_to_ok(self):
        self.participant.set_start_island(self.all_islands[4])

        self.client.force_login(self.participant.member)
        response = self.client.post(reverse('kabaramadalapeste:move_to', kwargs={
            'dest_island_id': self.island.island_id
        }))
        self.assertEqual(response.json()['status'], settings.OK_STATUS)

    def test_move_to_not_set_start(self):
        self.client.force_login(self.participant.member)
        response = self.client.post(reverse('kabaramadalapeste:move_to', kwargs={
            'dest_island_id': self.island.island_id
        }))
        self.assertEqual(response.json()['status'], settings.ERROR_STATUS)

    def test_move_to_not_neighbor(self):
        self.participant.set_start_island(self.all_islands[1])
        self.client.force_login(self.participant.member)
        response = self.client.post(reverse('kabaramadalapeste:move_to', kwargs={
            'dest_island_id': self.island.island_id
        }))
        self.assertEqual(response.json()['status'], settings.ERROR_STATUS)

    def test_move_to_not_enough_sekke(self):
        self.participant.set_start_island(self.all_islands[4])
        self.client.force_login(self.participant.member)

        safe_sekke = self.participant.get_safe_sekke()
        safe_sekke.amount = settings.GAME_MOVE_PRICE - 1
        safe_sekke.save()
        response = self.client.post(reverse('kabaramadalapeste:move_to', kwargs={
            'dest_island_id': self.island.island_id
        }))
        self.assertEqual(response.json()['status'], settings.ERROR_STATUS)

    def test_put_anchor_not_login(self):
        response = self.client.get(reverse('kabaramadalapeste:put_anchor'))
        self.assertEqual(response.status_code, 302)

    def test_put_anchor_ok(self):
        self.participant.set_start_island(self.island)

        self.client.force_login(self.participant.member)
        response = self.client.post(reverse('kabaramadalapeste:put_anchor'))
        self.assertEqual(response.json()['status'], settings.OK_STATUS)

    def test_put_anchor_not_set_start_island(self):
        self.client.force_login(self.participant.member)
        response = self.client.post(reverse('kabaramadalapeste:put_anchor'))
        self.assertEqual(response.json()['status'], settings.ERROR_STATUS)

    def test_put_anchor_not_enough_sekke(self):
        self.participant.set_start_island(self.all_islands[4])
        self.client.force_login(self.participant.member)

        safe_sekke = self.participant.get_safe_sekke()
        safe_sekke.amount = settings.GAME_MOVE_PRICE - 1
        safe_sekke.save()
        response = self.client.post(reverse('kabaramadalapeste:move_to', kwargs={
            'dest_island_id': self.island.island_id
        }))
        self.assertEqual(response.json()['status'], settings.ERROR_STATUS)

    def test_open_treasure_not_login(self):
        response = self.client.get(reverse('kabaramadalapeste:open_treasure'))
        self.assertEqual(response.status_code, 302)

    def test_open_treasure_ok(self):
        self.participant.set_start_island(self.island)
        self.participant.put_anchor_on_current_island()

        pis = ParticipantIslandStatus.objects.get(
            participant=self.participant,
            island=self.island
        )
        for key in pis.treasure.keys.all():
            if self.participant.get_property(key.key_type).amount < key.amount:
                self.participant.add_property(
                    key.key_type,
                    key.amount - self.participant.get_property(key.key_type).amount
                )

        self.client.force_login(self.participant.member)
        response = self.client.post(reverse('kabaramadalapeste:open_treasure'))
        self.assertEqual(response.json()['status'], settings.OK_STATUS)

    def test_open_treasure_not_set_start_island(self):
        self.client.force_login(self.participant.member)
        response = self.client.post(reverse('kabaramadalapeste:open_treasure'))
        self.assertEqual(response.json()['status'], settings.ERROR_STATUS)

    def test_open_treasure_did_not_anchor(self):
        self.participant.set_start_island(self.island)

        pis = ParticipantIslandStatus.objects.get(
            participant=self.participant,
            island=self.island
        )
        for key in pis.treasure.keys.all():
            if self.participant.get_property(key.key_type).amount < key.amount:
                self.participant.add_property(
                    key.key_type,
                    key.amount - self.participant.get_property(key.key_type).amount
                )

        self.client.force_login(self.participant.member)
        response = self.client.post(reverse('kabaramadalapeste:open_treasure'))
        self.assertEqual(response.json()['status'], settings.ERROR_STATUS)

    def test_open_treasure_not_enough_props(self):
        self.participant.set_start_island(self.island)
        self.client.force_login(self.participant.member)

        pis = ParticipantIslandStatus.objects.get(
            participant=self.participant,
            island=self.island
        )
        for key in pis.treasure.keys.all():
            if self.participant.get_property(key.key_type).amount < key.amount:
                self.participant.add_property(
                    key.key_type,
                    key.amount - self.participant.get_property(key.key_type).amount
                )
        key = pis.treasure.keys.first()
        self.participant.reduce_property(
            key.key_type,
            (self.participant.get_property(key.key_type).amount - key.amount) + 1
        )
        response = self.client.post(reverse('kabaramadalapeste:open_treasure'))
        self.assertEqual(response.json()['status'], settings.ERROR_STATUS)
