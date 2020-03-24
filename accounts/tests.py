from django.test import TestCase

from accounts.factory import ParticipantFactory
from accounts.models import Participant
from kabaramadalapeste.factory import (
    IslandFactory, ChallengeFactory
)
from kabaramadalapeste.models import (
    Way, ParticipantIslandStatus, Island,
    ParticipantPropertyItem
)
from kabaramadalapeste.conf import settings


# Create your tests here.
class ParticipantTest(TestCase):

    def setUp(self):
        [ChallengeFactory() for i in range(4)]
        self.participant = ParticipantFactory()
        self.all_islands = [IslandFactory() for i in range(10)]
        self.island = self.all_islands[0]
        for i in range(3, 7):
            Way.objects.create(
                first_end=self.island,
                second_end=self.all_islands[i]
            )

    def test_init_pis(self):
        self.participant.init_pis()
        self.assertEqual(ParticipantIslandStatus.objects.count(), Island.objects.count())

    def test_set_start_island(self):
        self.participant.init_pis()
        self.participant.init_properties()
        prev_sekke = self.participant.sekke.amount
        self.participant.set_start_island(self.island)
        after_sekke = self.participant.sekke.amount
        pis_dest = ParticipantIslandStatus.objects.get(
            participant=self.participant,
            island=self.island
        )
        self.assertEqual(prev_sekke - after_sekke, 0)
        self.assertTrue(pis_dest.did_reach)
        self.assertTrue(pis_dest.currently_in)
        self.assertIsNotNone(pis_dest.reached_at)
        self.assertEqual(self.participant.currently_at_island, self.island)

    def test_move_first(self):
        self.participant.init_pis()
        self.participant.init_properties()
        self.participant.set_start_island(self.all_islands[4])

        prev_sekke = self.participant.sekke.amount
        self.participant.move(self.island)
        after_sekke = self.participant.sekke.amount
        pis_dest = ParticipantIslandStatus.objects.get(
            participant=self.participant,
            island=self.island
        )
        self.assertEqual(prev_sekke - after_sekke, settings.GAME_MOVE_PRICE)
        self.assertTrue(pis_dest.did_reach)
        self.assertTrue(pis_dest.currently_in)
        self.assertIsNotNone(pis_dest.reached_at)
        self.assertEqual(self.participant.currently_at_island, self.island)

    def test_move_free(self):
        self.participant.init_pis()
        self.participant.init_properties()
        self.participant.set_start_island(self.all_islands[4])
        prev_sekke = self.participant.sekke.amount
        self.participant.move(self.island, is_free=True)
        after_sekke = self.participant.sekke.amount
        self.assertEqual(prev_sekke - after_sekke, 0)

    def test_move_less_sekke(self):
        self.participant.init_pis()
        self.participant.init_properties()
        self.participant.set_start_island(self.all_islands[4])
        safe_sekke = self.participant.get_safe_sekke()
        safe_sekke.amount = settings.GAME_MOVE_PRICE - 1
        safe_sekke.save()

        with self.assertRaises(Participant.ProprtiesAreNotEnough):
            self.participant.move(self.island)

    def test_move_less_sekke_free(self):
        self.participant.init_pis()
        self.participant.init_properties()
        self.participant.set_start_island(self.all_islands[4])
        safe_sekke = self.participant.get_safe_sekke()
        safe_sekke.amount = settings.GAME_MOVE_PRICE - 1
        safe_sekke.save()

        self.participant.move(self.island, is_free=True)

    def test_move_not_linked(self):
        self.participant.init_pis()
        self.participant.init_properties()
        self.participant.set_start_island(self.all_islands[4])
        prev_sekke = self.participant.sekke.amount
        self.participant.move(self.island)
        after_sekke = self.participant.sekke.amount
        with self.assertRaises(Island.IslandsNotConnected):
            self.participant.move(self.all_islands[2])
            self.assertEqual(prev_sekke - after_sekke, 0)

    def test_move_second(self):
        self.participant.init_pis()
        self.participant.init_properties()
        self.participant.set_start_island(self.all_islands[4])
        self.participant.put_anchor_on_current_island()
        self.participant.move(self.island)
        pis_src = ParticipantIslandStatus.objects.get(
            participant=self.participant,
            island=self.all_islands[4]
        )
        pis_dest = ParticipantIslandStatus.objects.get(
            participant=self.participant,
            island=self.island
        )
        self.assertFalse(pis_src.currently_in)
        self.assertFalse(pis_src.currently_anchored)

        self.assertTrue(pis_dest.did_reach)
        self.assertTrue(pis_dest.currently_in)
        self.assertIsNotNone(pis_dest.reached_at)
        self.assertEqual(self.participant.currently_at_island, self.island)

    def test_put_anchor_ok(self):
        self.participant.init_pis()
        self.participant.init_properties()
        self.participant.set_start_island(self.island)
        prev_sekke = self.participant.sekke.amount
        self.participant.put_anchor_on_current_island()
        after_sekke = self.participant.sekke.amount

        pis_current = ParticipantIslandStatus.objects.get(
            participant=self.participant,
            island=self.island
        )

        self.assertTrue(pis_current.currently_anchored)
        self.assertIsNotNone(pis_current.last_anchored_at)
        self.assertEqual(prev_sekke - after_sekke, settings.GAME_PUT_ANCHOR_PRICE)

    def test_put_anchor_not_set_start_island(self):
        self.participant.init_pis()
        self.participant.init_properties()
        with self.assertRaises(Participant.ParticipantIsNotOnIsland):
            self.participant.put_anchor_on_current_island()

    def test_put_anchor_not_enough_sekke(self):
        self.participant.init_pis()
        self.participant.init_properties()
        self.participant.set_start_island(self.island)
        safe_sekke = self.participant.get_safe_sekke()
        safe_sekke.amount = settings.GAME_PUT_ANCHOR_PRICE - 1
        safe_sekke.save()
        with self.assertRaises(Participant.ProprtiesAreNotEnough):
            self.participant.put_anchor_on_current_island()

    def test_init_properties(self):
        PARTICIPANT_INITIAL_PROPERTIES = {
            settings.GAME_SEKKE: 100,
            settings.GAME_KEY1: 2
        }
        with self.settings(GAME_PARTICIPANT_INITIAL_PROPERTIES=PARTICIPANT_INITIAL_PROPERTIES):
            self.participant.init_properties()
            self.assertEqual(ParticipantPropertyItem.objects.count(), 2)

    def test_init_properties_negative(self):
        PARTICIPANT_INITIAL_PROPERTIES = {
            settings.GAME_SEKKE: -100,
            settings.GAME_KEY1: 2
        }
        with self.settings(GAME_PARTICIPANT_INITIAL_PROPERTIES=PARTICIPANT_INITIAL_PROPERTIES):
            self.participant.init_properties()
            self.assertEqual(ParticipantPropertyItem.objects.count(), 1)
