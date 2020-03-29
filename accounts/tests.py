from django.test import TestCase

from accounts.factory import ParticipantFactory, MemberFactory
from accounts.models import Participant
from kabaramadalapeste.factory import (
    IslandFactory, ChallengeFactory, TreasureFactory,
    ShortAnswerQuestionFactory
)
from kabaramadalapeste.models import (
    Way, ParticipantIslandStatus, Island, Peste, PesteConfiguration,
    ParticipantPropertyItem, ShortAnswerQuestion, Treasure, GameEventLog
)
from kabaramadalapeste.conf import settings
from collections import defaultdict
from django.utils import timezone
from datetime import datetime, timedelta
from unittest import mock


# Create your tests here.
class ParticipantTest(TestCase):

    def setUp(self):
        [ChallengeFactory() for i in range(10)]
        [ShortAnswerQuestionFactory() for i in range(60)]
        self.super_member = MemberFactory(is_superuser=True)
        self.participant = ParticipantFactory()
        self.all_islands = [IslandFactory(__sequence=i) for i in range(settings.GAME_DEFAULT_ISLAND_COUNT)]
        [TreasureFactory(keys=2, rewards=4) for i in range(settings.GAME_DEFAULT_ISLAND_COUNT - 1)]
        self.island = self.all_islands[0]
        for i in range(3, 7):
            Way.objects.create(
                first_end=self.island,
                second_end=self.all_islands[i]
            )
        peste_config = PesteConfiguration.get_solo()
        peste_config.is_peste_available = True
        peste_config.save()

    def test_init_pis(self):
        self.participant.init_pis()
        self.assertEqual(ParticipantIslandStatus.objects.count(), Island.objects.count())
        treasure_ids = set()
        question_ids = set()
        for i in range(1, settings.GAME_DEFAULT_ISLAND_COUNT + 1):
            pis = ParticipantIslandStatus.objects.get(
                participant=self.participant,
                island_id=i
            )
            if i != settings.GAME_BANDARGAH_ISLAND_ID:
                self.assertIsNotNone(pis.treasure)
                treasure_ids.add(pis.treasure.id)
                question_ids.add(pis.question.id)
            else:
                self.assertIsNone(pis.treasure)
        self.assertEqual(len(treasure_ids), settings.GAME_DEFAULT_ISLAND_COUNT - 1)
        self.assertEqual(len(question_ids), settings.GAME_DEFAULT_ISLAND_COUNT - 1)

    def test_init_pis_atomic(self):
        for i, question in enumerate(ShortAnswerQuestion.objects.all()):
            if i > 30:
                question.delete()
        with self.assertRaises(ParticipantIslandStatus.CantAssignNewQuestion):
            self.participant.init_pis()
            self.assertEqual(ParticipantIslandStatus.objects.count(), 0)

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
        self.assertEqual(GameEventLog.objects.count(), 1)

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
        self.assertEqual(GameEventLog.objects.count(), 2)

    # def test_move_free(self):
    #     self.participant.init_pis()
    #     self.participant.init_properties()
    #     self.participant.set_start_island(self.all_islands[4])
    #     prev_sekke = self.participant.sekke.amount
    #     self.participant.move(self.island, is_free=True)
    #     after_sekke = self.participant.sekke.amount
    #     self.assertEqual(prev_sekke - after_sekke, 0)

    def test_move_less_sekke(self):
        self.participant.init_pis()
        self.participant.init_properties()
        self.participant.set_start_island(self.all_islands[4])
        safe_sekke = self.participant.get_safe_sekke()
        safe_sekke.amount = settings.GAME_MOVE_PRICE - 1
        safe_sekke.save()

        with self.assertRaises(Participant.PropertiesAreNotEnough):
            self.participant.move(self.island)
        self.assertEqual(GameEventLog.objects.count(), 1)

    # def test_move_less_sekke_free(self):
    #     self.participant.init_pis()
    #     self.participant.init_properties()
    #     self.participant.set_start_island(self.all_islands[4])
    #     safe_sekke = self.participant.get_safe_sekke()
    #     safe_sekke.amount = settings.GAME_MOVE_PRICE - 1
    #     safe_sekke.save()
    #
    #     self.participant.move(self.island, is_free=True)

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
        self.assertEqual(GameEventLog.objects.count(), 3)

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
        self.assertTrue(pis_current.is_treasure_visible)
        self.assertIsNotNone(pis_current.last_anchored_at)
        self.assertEqual(prev_sekke - after_sekke, settings.GAME_PUT_ANCHOR_PRICE)
        self.assertEqual(GameEventLog.objects.count(), 2)

    def test_put_anchor_not_set_start_island(self):
        self.participant.init_pis()
        self.participant.init_properties()
        with self.assertRaises(Participant.ParticipantIsNotOnIsland):
            self.participant.put_anchor_on_current_island()
        self.assertEqual(GameEventLog.objects.count(), 0)

    def test_put_anchor_again(self):
        self.participant.init_pis()
        self.participant.init_properties()
        self.participant.set_start_island(self.island)
        self.participant.put_anchor_on_current_island()
        with self.assertRaises(Participant.CantPutAnchorAgain):
            self.participant.put_anchor_on_current_island()
        self.assertEqual(GameEventLog.objects.count(), 2)

    def test_put_anchor_not_enough_sekke(self):
        self.participant.init_pis()
        self.participant.init_properties()
        self.participant.set_start_island(self.island)
        safe_sekke = self.participant.get_safe_sekke()
        safe_sekke.amount = settings.GAME_PUT_ANCHOR_PRICE - 1
        safe_sekke.save()

        pis = ParticipantIslandStatus.objects.get(
            participant=self.participant,
            island=self.island
        )
        with self.assertRaises(Participant.PropertiesAreNotEnough):
            self.participant.put_anchor_on_current_island()
        pis.refresh_from_db()
        self.assertFalse(pis.currently_anchored)
        self.assertFalse(pis.is_treasure_visible)
        self.assertIsNone(pis.last_anchored_at)
        self.assertEqual(GameEventLog.objects.count(), 1)

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

    def test_open_treasure_ok(self):
        self.participant.init_pis()
        self.participant.init_properties()
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
        before_props = {
            prop.property_type: prop.amount for prop in self.participant.properties.all()
        }
        self.participant.open_treasure_on_current_island()
        after_props = {
            prop.property_type: prop.amount for prop in self.participant.properties.all()
        }
        expected_change = defaultdict(int)
        for key in pis.treasure.keys.all():
            expected_change[key.key_type] -= key.amount
        for reward in pis.treasure.rewards.all():
            expected_change[reward.reward_type] += reward.amount
        for key, change in expected_change.items():
            self.assertEqual(after_props[key] - before_props.get(key, 0), expected_change[key])
        pis.refresh_from_db()
        self.assertTrue(pis.did_open_treasure)
        self.assertIsNotNone(pis.treasure_opened_at)
        self.assertEqual(GameEventLog.objects.count(), 3)

    def test_open_treasure_twice(self):
        self.participant.init_pis()
        self.participant.init_properties()
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
        self.participant.open_treasure_on_current_island()
        with self.assertRaises(Participant.CantOpenTreasureAgain):
            self.participant.open_treasure_on_current_island()
        self.assertEqual(GameEventLog.objects.count(), 3)

    def test_open_treasure_not_enough(self):
        self.participant.init_pis()
        self.participant.init_properties()
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
        key = pis.treasure.keys.first()
        self.participant.reduce_property(
            key.key_type,
            (self.participant.get_property(key.key_type).amount - key.amount) + 1
        )
        before_props = {
            prop.property_type: prop.amount for prop in self.participant.properties.all()
        }
        with self.assertRaises(Participant.PropertiesAreNotEnough):
            self.participant.open_treasure_on_current_island()
        after_props = {
            prop.property_type: prop.amount for prop in self.participant.properties.all()
        }
        for key in pis.treasure.keys.all():
            self.assertEqual(after_props[key.key_type] - before_props.get(key.key_type, 0), 0)
        for reward in pis.treasure.rewards.all():
            self.assertEqual(
                after_props.get(reward.reward_type, 0) - before_props.get(reward.reward_type, 0), 0
            )
        pis.refresh_from_db()
        self.assertFalse(pis.did_open_treasure)
        self.assertIsNone(pis.treasure_opened_at)
        self.assertEqual(GameEventLog.objects.count(), 2)

    def test_open_treasure_not_at_island(self):
        self.participant.init_pis()
        self.participant.init_properties()

        with self.assertRaises(Participant.ParticipantIsNotOnIsland):
            self.participant.open_treasure_on_current_island()
        self.assertEqual(GameEventLog.objects.count(), 0)

    def test_open_treasure_did_not_anchor(self):
        self.participant.init_pis()
        self.participant.init_properties()
        self.participant.set_start_island(self.island)

        with self.assertRaises(Participant.DidNotAnchored):
            self.participant.open_treasure_on_current_island()
        self.assertEqual(GameEventLog.objects.count(), 1)

    def test_accept_challenge_ok(self):
        self.participant.init_pis()
        self.participant.init_properties()
        self.participant.set_start_island(self.island)
        self.participant.put_anchor_on_current_island()

        pis = ParticipantIslandStatus.objects.get(
            participant=self.participant,
            island=self.island
        )
        self.participant.accept_challenge_on_current_island()
        pis.refresh_from_db()
        self.assertTrue(pis.did_accept_challenge)
        self.assertIsNotNone(pis.challenge_accepted_at)
        self.assertEqual(GameEventLog.objects.count(), 3)

    def test_accept_challenge_twice(self):
        self.participant.init_pis()
        self.participant.init_properties()
        self.participant.set_start_island(self.island)
        self.participant.put_anchor_on_current_island()

        self.participant.accept_challenge_on_current_island()
        with self.assertRaises(Participant.CantAcceptChallengeAgain):
            self.participant.accept_challenge_on_current_island()
        self.assertEqual(GameEventLog.objects.count(), 3)

    def test_accept_challenge_not_at_island(self):
        self.participant.init_pis()
        self.participant.init_properties()

        with self.assertRaises(Participant.ParticipantIsNotOnIsland):
            self.participant.accept_challenge_on_current_island()
        self.assertEqual(GameEventLog.objects.count(), 0)

    def test_accept_challenge_did_not_anchor(self):
        self.participant.init_pis()
        self.participant.init_properties()
        self.participant.set_start_island(self.island)

        with self.assertRaises(Participant.DidNotAnchored):
            self.participant.accept_challenge_on_current_island()
        self.assertEqual(GameEventLog.objects.count(), 1)

    @mock.patch('accounts.models.timezone.now')
    def test_accept_challenge_limit(self, now_mock):
        base_now = datetime.now().replace(tzinfo=timezone.get_current_timezone())
        now_mock.return_value = base_now

        self.participant.init_pis()
        self.participant.init_properties()
        self.participant.set_start_island(self.island)
        self.participant.put_anchor_on_current_island()

        for i, island in enumerate(self.all_islands[5:5 + settings.GAME_BASE_CHALLENGE_PER_DAY]):
            pis = ParticipantIslandStatus.objects.get(
                participant=self.participant,
                island=island
            )
            pis.did_accept_challenge = True
            if i == 0:
                pis.challenge_accepted_at = base_now.replace(
                    hour=0,
                    minute=0,
                    second=1
                )
            else:
                pis.challenge_accepted_at = base_now
            pis.save()

        with self.assertRaises(Participant.MaximumChallengePerDayExceeded):
            self.participant.accept_challenge_on_current_island()
        self.assertEqual(GameEventLog.objects.count(), 2)

    @mock.patch('accounts.models.timezone.now')
    def test_accept_challenge_ok_one_less(self, now_mock):
        base_now = datetime.now().replace(tzinfo=timezone.get_current_timezone())
        now_mock.return_value = base_now

        self.participant.init_pis()
        self.participant.init_properties()
        self.participant.set_start_island(self.island)
        self.participant.put_anchor_on_current_island()

        for i, island in enumerate(self.all_islands[5:5 + settings.GAME_BASE_CHALLENGE_PER_DAY]):
            pis = ParticipantIslandStatus.objects.get(
                participant=self.participant,
                island=island
            )
            pis.did_accept_challenge = True
            if i == 0:
                pis.challenge_accepted_at = (base_now + timedelta(days=1)).replace(
                    hour=0,
                    minute=0,
                    second=1
                )
            else:
                pis.challenge_accepted_at = base_now
            pis.save()

        self.participant.accept_challenge_on_current_island()
        pis.refresh_from_db()
        self.assertTrue(pis.did_accept_challenge)
        self.assertIsNotNone(pis.challenge_accepted_at)
        self.assertEqual(GameEventLog.objects.count(), 3)

    def test_spade_ok_no_peste(self):
        self.participant.init_pis()
        self.participant.init_properties()
        self.participant.set_start_island(self.island)
        self.participant.put_anchor_on_current_island()
        self.participant.add_property(
            settings.GAME_SEKKE,
            PesteConfiguration.get_solo().island_spade_cost - self.participant.sekke.amount
        )
        result = self.participant.spade_on_current_island()
        pis = ParticipantIslandStatus.objects.get(
            participant=self.participant,
            island=self.island
        )
        self.assertFalse(result)
        self.assertEqual(self.participant.sekke.amount, 0)
        self.assertTrue(pis.did_spade)
        self.assertIsNotNone(pis.spaded_at)
        self.assertEqual(GameEventLog.objects.count(), 3)

    def test_spade_ok_with_peste(self):
        peste = Peste.objects.create(
            island=self.island
        )
        self.participant.init_pis()
        self.participant.init_properties()
        self.participant.set_start_island(self.island)
        self.participant.put_anchor_on_current_island()
        self.participant.add_property(
            settings.GAME_SEKKE,
            PesteConfiguration.get_solo().island_spade_cost - self.participant.sekke.amount
        )
        result = self.participant.spade_on_current_island()
        pis = ParticipantIslandStatus.objects.get(
            participant=self.participant,
            island=self.island
        )
        self.assertTrue(result)
        self.assertEqual(
            self.participant.sekke.amount,
            PesteConfiguration.get_solo().peste_reward
        )
        peste.refresh_from_db()
        self.assertTrue(pis.did_spade)
        self.assertIsNotNone(pis.spaded_at)
        self.assertTrue(peste.is_found)
        self.assertIsNotNone(peste.found_by)
        self.assertIsNotNone(peste.found_at)
        self.assertEqual(GameEventLog.objects.count(), 3)

    def test_spade_ok_with_peste_found_before(self):
        other_participant = ParticipantFactory()
        peste = Peste.objects.create(
            island=self.island,
            is_found=True,
            found_by=other_participant
        )
        self.participant.init_pis()
        self.participant.init_properties()
        self.participant.set_start_island(self.island)
        self.participant.put_anchor_on_current_island()
        self.participant.add_property(
            settings.GAME_SEKKE,
            PesteConfiguration.get_solo().island_spade_cost - self.participant.sekke.amount
        )
        result = self.participant.spade_on_current_island()
        pis = ParticipantIslandStatus.objects.get(
            participant=self.participant,
            island=self.island
        )
        self.assertFalse(result)
        self.assertEqual(self.participant.sekke.amount, 0)
        self.assertTrue(pis.did_spade)
        self.assertIsNotNone(pis.spaded_at)
        self.assertTrue(peste.is_found)
        self.assertEqual(peste.found_by, other_participant)
        self.assertEqual(GameEventLog.objects.count(), 3)

    def test_spade_ok_with_peste_not_enough_property(self):
        other_participant = ParticipantFactory()
        Peste.objects.create(
            island=self.island,
            is_found=True,
            found_by=other_participant
        )
        self.participant.init_pis()
        self.participant.init_properties()
        self.participant.set_start_island(self.island)
        self.participant.put_anchor_on_current_island()
        self.participant.add_property(
            settings.GAME_SEKKE,
            (PesteConfiguration.get_solo().island_spade_cost - self.participant.sekke.amount) - 1
        )
        with self.assertRaises(Participant.PropertiesAreNotEnough):
            self.participant.spade_on_current_island()
        pis = ParticipantIslandStatus.objects.get(
            participant=self.participant,
            island=self.island
        )
        self.assertIsNone(pis.spaded_at)
        self.assertEqual(GameEventLog.objects.count(), 2)

    def test_spade_twice(self):
        other_participant = ParticipantFactory()
        Peste.objects.create(
            island=self.island,
            is_found=True,
            found_by=other_participant
        )
        self.participant.init_pis()
        self.participant.init_properties()
        self.participant.set_start_island(self.island)
        self.participant.put_anchor_on_current_island()
        self.participant.add_property(
            settings.GAME_SEKKE,
            (2 * PesteConfiguration.get_solo().island_spade_cost - self.participant.sekke.amount)
        )
        self.participant.spade_on_current_island()
        with self.assertRaises(Participant.CantSpadeAgain):
            self.participant.spade_on_current_island()
        self.assertEqual(GameEventLog.objects.count(), 3)

    def test_spade_not_at_island(self):
        self.participant.init_pis()
        self.participant.init_properties()

        with self.assertRaises(Participant.ParticipantIsNotOnIsland):
            self.participant.spade_on_current_island()
        self.assertEqual(GameEventLog.objects.count(), 0)
