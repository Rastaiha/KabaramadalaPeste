from django.test import TestCase
from django.urls import reverse
from django.http import HttpResponse
from django.db.utils import IntegrityError
# Create your tests here.
from homepage.models import SiteConfiguration
from accounts.models import Participant
from kabaramadalapeste.models import (
    ParticipantIslandStatus, Island, Way, Peste, PesteConfiguration,
    ShortAnswerSubmit, ShortAnswerQuestion, TradeOffer, BaseSubmit, BandargahInvestment
)
from kabaramadalapeste.factory import (
    ChallengeFactory, IslandFactory, ShortAnswerQuestionFactory, TreasureFactory
)
from kabaramadalapeste.conf import settings
from accounts.factory import ParticipantFactory
from unittest import mock

from django.utils import timezone
from datetime import datetime, timedelta


class ModelsTest(TestCase):

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

    def test_create_answer_without_pis(self):
        with self.assertRaises(IntegrityError):
            ShortAnswerSubmit.objects.create()

    def test_check_short_answer_submit(self):
        pis = ParticipantIslandStatus(
            participant=self.participant,
            island=self.island
        )
        pis.assign_question()
        submit = ShortAnswerSubmit.objects.create(
            pis=pis,
        )
        submit.check_answer()
        self.assertEqual(submit.submit_status, BaseSubmit.SubmitStatus.Wrong)
        self.assertIsNotNone(submit.submitted_at)

    def test_check_short_answer_submit_wrong(self):
        pis = ParticipantIslandStatus(
            participant=self.participant,
            island=self.island
        )
        pis.assign_question()
        submit = ShortAnswerSubmit.objects.create(
            pis=pis,
            submitted_answer=ShortAnswerQuestionFactory.correct_answer
        )
        submit.check_answer()
        self.assertEqual(submit.submit_status, BaseSubmit.SubmitStatus.Correct)
        self.assertIsNotNone(submit.submitted_at)
        self.assertIsNotNone(pis.submit)

    def test_check_short_answer_submit_wrong_type(self):
        pis = ParticipantIslandStatus(
            participant=self.participant,
            island=self.island
        )
        pis.assign_question()
        pis.question.answer_type = ShortAnswerQuestion.INTEGER
        pis.question.correct_answer = 2
        submit = ShortAnswerSubmit.objects.create(
            pis=pis,
            submitted_answer='ghool'
        )
        submit.check_answer()
        self.assertEqual(submit.submit_status, BaseSubmit.SubmitStatus.Wrong)
        self.assertIsNotNone(submit.submitted_at)

    def test_check_short_answer_submit_correct_int(self):
        pis = ParticipantIslandStatus(
            participant=self.participant,
            island=self.island
        )
        pis.assign_question()
        pis.question.answer_type = ShortAnswerQuestion.INTEGER
        pis.question.correct_answer = 2
        submit = ShortAnswerSubmit.objects.create(
            pis=pis,
            submitted_answer='2'
        )
        submit.check_answer()
        self.assertEqual(submit.submit_status, BaseSubmit.SubmitStatus.Correct)
        self.assertIsNotNone(submit.submitted_at)

    def test_check_short_answer_submit_wrong_float(self):
        pis = ParticipantIslandStatus(
            participant=self.participant,
            island=self.island
        )
        pis.assign_question()
        pis.question.answer_type = ShortAnswerQuestion.FLOAT
        pis.question.correct_answer = 2.2
        submit = ShortAnswerSubmit.objects.create(
            pis=pis,
            submitted_answer=2.3
        )
        submit.check_answer()
        self.assertEqual(submit.submit_status, BaseSubmit.SubmitStatus.Wrong)
        self.assertIsNotNone(submit.submitted_at)

    def test_check_short_answer_submit_correct_float(self):
        pis = ParticipantIslandStatus(
            participant=self.participant,
            island=self.island
        )
        pis.assign_question()
        pis.question.answer_type = ShortAnswerQuestion.FLOAT
        pis.question.correct_answer = 2.2
        submit = ShortAnswerSubmit.objects.create(
            pis=pis,
            submitted_answer=2.204
        )
        submit.check_answer()
        self.assertEqual(submit.submit_status, BaseSubmit.SubmitStatus.Correct)
        self.assertIsNotNone(submit.submitted_at)


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
        config = SiteConfiguration.get_solo()
        config.is_game_running = True
        config.save()

    def test_settings_not_login(self):
        response = self.client.get(reverse('kabaramadalapeste:settings'))
        self.assertEqual(response.status_code, 302)

    def test_settings_ok(self):
        self.client.force_login(self.participant.member)
        move_price = 2000
        put_anchor_price = 100
        with self.settings(GAME_MOVE_PRICE=move_price, GAME_PUT_ANCHOR_PRICE=put_anchor_price):
            response = self.client.get(reverse('kabaramadalapeste:settings'))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['move_price'], move_price)
            self.assertEqual(response.json()['put_anchor_price'], put_anchor_price)

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
        self.assertEqual(response.json()['treasure_keys'], 'unknown')
        self.assertEqual(response.json()['submit_status'], 'No')

    def test_island_info_with_submit(self):
        for i in range(4, 8):
            self.all_participants[i].set_start_island(self.island)
            self.all_participants[i].put_anchor_on_current_island()
        self.participant.set_start_island(self.island)
        self.client.force_login(self.participant.member)
        pis = ParticipantIslandStatus.objects.get(
            participant=self.participant,
            island=self.island
        )
        ShortAnswerSubmit.objects.create(pis=pis, submit_status=BaseSubmit.SubmitStatus.Pending)
        response = self.client.get(reverse('kabaramadalapeste:island_info', kwargs={
            'island_id': self.island.island_id
        }))
        self.assertIsNotNone(response.json()['name'])
        self.assertIsNotNone(response.json()['challenge_name'])
        self.assertEqual(response.json()['participants_inside'], 4)
        self.assertEqual(response.json()['treasure_keys'], 'unknown')
        self.assertEqual(response.json()['submit_status'], BaseSubmit.SubmitStatus.Pending)

    def test_island_info_keys_visible(self):
        self.participant.set_start_island(self.island)
        self.participant.put_anchor_on_current_island()
        self.client.force_login(self.participant.member)
        response = self.client.get(reverse('kabaramadalapeste:island_info', kwargs={
            'island_id': self.island.island_id
        }))
        pis = ParticipantIslandStatus.objects.get(
            participant=self.participant,
            island=self.island
        )
        self.assertIsNotNone(response.json()['name'])
        self.assertIsNotNone(response.json()['challenge_name'])
        self.assertEqual(response.json()['participants_inside'], 1)
        self.assertDictEqual(
            response.json()['treasure_keys'],
            {key.key_type: key.amount for key in pis.treasure.keys.all()}
        )

    def test_island_info_bandargah(self):
        self.participant.set_start_island(self.all_islands[settings.GAME_BANDARGAH_ISLAND_ID - 1])
        self.participant.put_anchor_on_current_island()
        self.client.force_login(self.participant.member)
        response = self.client.get(reverse('kabaramadalapeste:island_info', kwargs={
            'island_id': settings.GAME_BANDARGAH_ISLAND_ID
        }))
        self.assertIsNotNone(response.json()['name'])
        self.assertEqual(response.json()['participants_inside'], 1)
        self.assertEqual(
            response.json()['treasure_keys'],
            'unknown'
        )

    def test_participant_info_not_login(self):
        response = self.client.get(reverse('kabaramadalapeste:participant_info'))
        self.assertEqual(response.status_code, 302)

    def test_participant_info_ok(self):
        self.participant.set_start_island(self.island)
        self.client.force_login(self.participant.member)
        response = self.client.get(reverse('kabaramadalapeste:participant_info'))
        self.assertEqual(response.json()['username'], self.participant.member.username)
        self.assertEqual(response.json()['current_island_id'], self.participant.currently_at_island.island_id)
        self.assertFalse(response.json()['currently_anchored'])
        for key, value in settings.GAME_PARTICIPANT_INITIAL_PROPERTIES.items():
            self.assertEqual(response.json()['properties'][key], value)

    def test_participant_info_ok_anchored(self):
        self.participant.set_start_island(self.island)
        self.participant.put_anchor_on_current_island()
        self.client.force_login(self.participant.member)
        response = self.client.get(reverse('kabaramadalapeste:participant_info'))
        self.assertTrue(response.json()['currently_anchored'])

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

    def test_put_anchor_again(self):
        self.participant.set_start_island(self.island)
        self.client.force_login(self.participant.member)
        self.client.post(reverse('kabaramadalapeste:put_anchor'))
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

    def test_open_treasure_twice(self):
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
        self.client.post(reverse('kabaramadalapeste:open_treasure'))
        response = self.client.post(reverse('kabaramadalapeste:open_treasure'))
        self.assertEqual(response.json()['status'], settings.ERROR_STATUS)

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

    def text_maximum_active_offers_error(self):
        self.client.force_login(self.participant.member)
        data = {
            'requested_' + settings.GAME_VISION: '1',
            'suggested_' + settings.GAME_SEKKE: '1',
        }
        for i in range(settings.GAME_MAXIMUM_ACTIVE_OFFERS):
            response = self.client.post(reverse('kabaramadalapeste:create_offer'), data=data)
            self.assertEqual(response.json()['status'], settings.OK_STATUS)
        response = self.client.post(reverse('kabaramadalapeste:create_offer'), data=data)
        self.assertEqual(response.json()['status'], settings.ERROR_STATUS)
        for offer in self.participant.created_trade_offers.all():
            offer.delete()

    def test_create_offer_not_enough_property(self):
        self.client.force_login(self.participant.member)
        data = {
            'requested_' + settings.GAME_VISION: '1',
            'suggested_' + settings.GAME_SEKKE: str(self.participant.sekke.amount + 1),
        }
        response = self.client.post(reverse('kabaramadalapeste:create_offer'), data=data)
        self.assertEqual(response.json()['status'], settings.ERROR_STATUS)

    def test_accept_challenge_not_login(self):
        response = self.client.get(reverse('kabaramadalapeste:accept_challenge'))
        self.assertEqual(response.status_code, 302)

    def test_accept_challenge_ok(self):
        self.participant.set_start_island(self.island)
        self.participant.put_anchor_on_current_island()

        self.client.force_login(self.participant.member)
        response = self.client.post(reverse('kabaramadalapeste:accept_challenge'))
        self.assertEqual(response.json()['status'], settings.OK_STATUS)

    def test_accept_challenge_twice(self):
        self.participant.set_start_island(self.island)
        self.participant.put_anchor_on_current_island()

        self.client.force_login(self.participant.member)
        self.client.post(reverse('kabaramadalapeste:accept_challenge'))
        response = self.client.post(reverse('kabaramadalapeste:accept_challenge'))
        self.assertEqual(response.json()['status'], settings.ERROR_STATUS)

    @mock.patch('accounts.views.Participant.accept_challenge_on_current_island')
    def test_accept_challenge_maximum(self, accept_mock):
        accept_mock.side_effect = Participant.MaximumChallengePerDayExceeded
        self.participant.set_start_island(self.island)
        self.participant.put_anchor_on_current_island()

        self.client.force_login(self.participant.member)
        response = self.client.post(reverse('kabaramadalapeste:accept_challenge'))
        self.assertEqual(response.json()['status'], settings.ERROR_STATUS)

    def test_delete_and_get_offers(self):
        self.client.force_login(self.participant.member)
        old_sekke = self.participant.sekke.amount
        data = {
            'requested_' + settings.GAME_VISION: '1',
            'suggested_' + settings.GAME_SEKKE: '1',
        }
        response = self.client.post(reverse('kabaramadalapeste:create_offer'), data=data)
        self.assertEqual(response.json()['status'], settings.OK_STATUS)
        response = self.client.get(reverse('kabaramadalapeste:get_my_offers'))
        self.assertEqual(len(response.json()['offers']), 1)
        pk = response.json()['offers'][0]['pk']
        response = self.client.get(reverse('kabaramadalapeste:delete_offer', kwargs={'pk':pk}))
        self.assertEqual(response.json()['status'], settings.OK_STATUS)
        self.assertEqual(old_sekke, self.participant.sekke.amount)
        response = self.client.get(reverse('kabaramadalapeste:get_my_offers'))
        self.assertEqual(len(response.json()['offers']), 0)

    def test_accept_not_enough_properties(self):
        participant1 = self.all_participants[1]
        self.client.force_login(self.participant.member)
        data = {
            'requested_' + settings.GAME_VISION: str(participant1.get_property(settings.GAME_VISION).amount + 1),
            'suggested_' + settings.GAME_SEKKE: '1',
        }
        response = self.client.post(reverse('kabaramadalapeste:create_offer'), data=data)
        self.assertEqual(response.json()['status'], settings.OK_STATUS)
        self.client.force_login(participant1.member)
        response = self.client.get(reverse('kabaramadalapeste:get_all_offers'))
        self.assertEqual(len(response.json()['offers']), 1)
        pk = response.json()['offers'][0]['pk']
        response = self.client.get(reverse('kabaramadalapeste:accept_offer', kwargs={'pk':pk}))
        self.assertEqual(response.json()['status'], settings.ERROR_STATUS)
        TradeOffer.objects.all().delete()

    def test_accept_offer(self):
        participant1 = self.all_participants[1]
        self.client.force_login(self.participant.member)
        participant1.add_property(settings.GAME_VISION, 1)
        old_sekke = self.participant.sekke.amount
        old_sekke1 = participant1.sekke.amount
        old_vision = self.participant.get_property(settings.GAME_VISION).amount
        old_vision1 = participant1.get_property(settings.GAME_VISION).amount
        data = {
            'requested_' + settings.GAME_VISION: '1',
            'suggested_' + settings.GAME_SEKKE: '1',
        }
        response = self.client.post(reverse('kabaramadalapeste:create_offer'), data=data)
        self.assertEqual(response.json()['status'], settings.OK_STATUS)
        self.client.force_login(participant1.member)
        response = self.client.get(reverse('kabaramadalapeste:get_all_offers'))
        self.assertEqual(len(response.json()['offers']), 1)
        pk = response.json()['offers'][0]['pk']
        response = self.client.get(reverse('kabaramadalapeste:accept_offer', kwargs={'pk':pk}))
        self.assertEqual(response.json()['status'], settings.OK_STATUS)
        response = self.client.get(reverse('kabaramadalapeste:get_all_offers'))
        self.assertEqual(len(response.json()['offers']), 0)
        sekke = self.participant.sekke.amount
        sekke1 = participant1.sekke.amount
        vision = self.participant.get_property(settings.GAME_VISION).amount
        vision1 = participant1.get_property(settings.GAME_VISION).amount
        self.assertEqual(sekke + 1, old_sekke)
        self.assertEqual(sekke1, old_sekke1 + 1)
        self.assertEqual(vision, old_vision + 1)
        self.assertEqual(vision1 + 1, old_vision1)

    def test_not_enough_abilities(self):
        vision = self.participant.get_safe_property(settings.GAME_VISION)
        vision.amount = 0
        vision.save()
        self.client.force_login(self.participant.member)
        data = {
            'ability_type': settings.GAME_VISION
        }
        response = self.client.post(reverse('kabaramadalapeste:use_ability'), data=data)
        self.assertEqual(response.json()['status'], settings.ERROR_STATUS)

    def test_travel_express_ok(self):
        self.participant.add_property(settings.GAME_TRAVEL_EXPRESS, 1)
        self.participant.set_start_island(self.all_islands[4])
        self.client.force_login(self.participant.member)
        data = {
            'ability_type': settings.GAME_TRAVEL_EXPRESS
        }
        response = self.client.post(reverse('kabaramadalapeste:use_ability'), data=data)
        self.assertEqual(response.json()['status'], settings.OK_STATUS)
        old_sekke = self.participant.sekke.amount
        self.client.force_login(self.participant.member)
        response = self.client.post(reverse('kabaramadalapeste:move_to', kwargs={
            'dest_island_id': self.island.island_id
        }))
        self.assertEqual(response.json()['status'], settings.OK_STATUS)
        self.assertEqual(old_sekke, self.participant.sekke.amount)
        response = self.client.post(reverse('kabaramadalapeste:move_to', kwargs={
            'dest_island_id': self.all_islands[4].island_id
        }))
        self.assertEqual(response.json()['status'], settings.OK_STATUS)
        self.assertNotEqual(old_sekke, self.participant.sekke.amount)

    def test_vision_ok(self):
        self.participant.add_property(settings.GAME_VISION, 1)
        self.participant.set_start_island(self.island)
        pis = ParticipantIslandStatus.objects.get(
            participant=self.participant,
            island=self.all_islands[1]
        )
        pis.is_treasure_visible = False
        pis.save()
        self.client.force_login(self.participant.member)
        data = {
            'ability_type': settings.GAME_VISION
        }
        response = self.client.post(reverse('kabaramadalapeste:use_ability'), data=data)
        self.assertEqual(response.json()['status'], settings.OK_STATUS)
        pis = ParticipantIslandStatus.objects.get(
            participant=self.participant,
            island=self.island
        )
        self.assertTrue(pis.is_treasure_visible)
        pis = ParticipantIslandStatus.objects.get(
            participant=self.participant,
            island=self.all_islands[4]
        )
        self.assertTrue(pis.is_treasure_visible)
        pis = ParticipantIslandStatus.objects.get(
            participant=self.participant,
            island=self.all_islands[1]
        )
        self.assertFalse(pis.is_treasure_visible)

    def test_challenge_plus_ok(self):
        self.participant.add_property(settings.GAME_CHALLENGE_PLUS, 1)
        self.participant.set_start_island(self.island)
        self.participant.put_anchor_on_current_island()
        self.client.force_login(self.participant.member)
        data = {
            'ability_type': settings.GAME_CHALLENGE_PLUS
        }
        response = self.client.post(reverse('kabaramadalapeste:use_ability'), data=data)
        self.assertEqual(response.json()['status'], settings.OK_STATUS)

        for i, island in enumerate(self.all_islands[5:5 + settings.GAME_BASE_CHALLENGE_PER_DAY + 1]):
            pis = ParticipantIslandStatus.objects.get(
                participant=self.participant,
                island=island
            )
            pis.did_accept_challenge = True
            pis.challenge_accepted_at = timezone.now()
            pis.save()

        with self.assertRaises(Participant.MaximumChallengePerDayExceeded):
            self.participant.accept_challenge_on_current_island()

    def test_bully_not_anchored(self):
        self.participant.add_property(settings.GAME_BULLY, 1)
        self.participant.set_start_island(self.island)
        self.participant.put_anchor_on_current_island()
        self.client.force_login(self.participant.member)
        data = {
            'ability_type': settings.GAME_BULLY
        }
        response = self.client.post(reverse('kabaramadalapeste:use_ability'), data=data)
        self.assertEqual(response.json()['status'], settings.OK_STATUS)
        participant1 = self.all_participants[1]
        participant1.set_start_island(self.island)
        participant1.add_property(settings.GAME_SEKKE, settings.GAME_BULLY_DAMAGE)
        old_sekke = self.participant.sekke.amount
        old_sekke1 = participant1.sekke.amount
        participant1.add_property(settings.GAME_SEKKE, settings.GAME_PUT_ANCHOR_PRICE)
        participant1.put_anchor_on_current_island()
        sekke = self.participant.sekke.amount
        sekke1 = participant1.sekke.amount
        self.assertEqual(old_sekke + settings.GAME_BULLY_DAMAGE, sekke)
        self.assertEqual(old_sekke1, sekke1 + settings.GAME_BULLY_DAMAGE)

    def test_bully_ok(self):
        self.participant.add_property(settings.GAME_BULLY, 1)
        self.participant.set_start_island(self.island)
        self.client.force_login(self.participant.member)
        data = {
            'ability_type': settings.GAME_BULLY
        }
        response = self.client.post(reverse('kabaramadalapeste:use_ability'), data=data)
        self.assertEqual(response.json()['status'], settings.ERROR_STATUS)

    def test_spade_not_login(self):
        self.participant.set_start_island(self.island)
        self.participant.put_anchor_on_current_island()
        self.participant.add_property(
            settings.GAME_SEKKE,
            (PesteConfiguration.get_solo().island_spade_cost - self.participant.sekke.amount)
        )
        response = self.client.post(reverse('kabaramadalapeste:spade'))
        self.assertEqual(response.status_code, 302)

    def test_spade_ok_not_found(self):
        self.participant.set_start_island(self.island)
        self.participant.put_anchor_on_current_island()
        self.client.force_login(self.participant.member)
        self.participant.add_property(
            settings.GAME_SEKKE,
            (PesteConfiguration.get_solo().island_spade_cost - self.participant.sekke.amount)
        )
        response = self.client.post(reverse('kabaramadalapeste:spade'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], settings.OK_STATUS)
        self.assertFalse(response.json()['found'])

    def test_spade_ok_found(self):
        Peste.objects.create(
            island=self.island,
        )
        self.participant.set_start_island(self.island)
        self.participant.put_anchor_on_current_island()
        self.client.force_login(self.participant.member)
        self.participant.add_property(
            settings.GAME_SEKKE,
            (PesteConfiguration.get_solo().island_spade_cost - self.participant.sekke.amount)
        )
        response = self.client.post(reverse('kabaramadalapeste:spade'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], settings.OK_STATUS)
        self.assertTrue(response.json()['found'])

    def test_spade_not_enough(self):
        self.participant.set_start_island(self.island)
        self.participant.put_anchor_on_current_island()
        self.client.force_login(self.participant.member)
        self.participant.add_property(
            settings.GAME_SEKKE,
            (PesteConfiguration.get_solo().island_spade_cost - self.participant.sekke.amount) - 1
        )
        response = self.client.post(reverse('kabaramadalapeste:spade'))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['status'], settings.ERROR_STATUS)

    def test_spade_twice(self):
        self.participant.set_start_island(self.island)
        self.participant.put_anchor_on_current_island()
        self.client.force_login(self.participant.member)
        self.participant.add_property(
            settings.GAME_SEKKE,
            (PesteConfiguration.get_solo().island_spade_cost - self.participant.sekke.amount)
        )
        self.client.post(reverse('kabaramadalapeste:spade'))
        response = self.client.post(reverse('kabaramadalapeste:spade'))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['status'], settings.ERROR_STATUS)

    def test_spade_not_on_island(self):
        self.client.force_login(self.participant.member)
        self.participant.add_property(
            settings.GAME_SEKKE,
            (PesteConfiguration.get_solo().island_spade_cost - self.participant.sekke.amount)
        )
        self.client.post(reverse('kabaramadalapeste:spade'))
        response = self.client.post(reverse('kabaramadalapeste:spade'))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['status'], settings.ERROR_STATUS)

    def test_spade_not_anchored(self):
        self.participant.set_start_island(self.island)
        self.client.force_login(self.participant.member)
        self.participant.add_property(
            settings.GAME_SEKKE,
            (PesteConfiguration.get_solo().island_spade_cost - self.participant.sekke.amount)
        )
        self.client.post(reverse('kabaramadalapeste:spade'))
        response = self.client.post(reverse('kabaramadalapeste:spade'))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['status'], settings.ERROR_STATUS)

    def test_bandargah_ok(self):
        bandar = Island.objects.get(island_id=settings.GAME_BANDARGAH_ISLAND_ID)
        self.participant.add_property(settings.GAME_SEKKE, 3000)
        old_sekke = self.participant.sekke.amount
        self.participant.set_start_island(bandar)
        self.client.force_login(self.participant.member)
        data = {
            'amount': '3000'
        }
        response = self.client.post(reverse('kabaramadalapeste:invest_bandargah'), data=data)
        self.assertEqual(response.json()['status'], settings.OK_STATUS)
        self.assertEqual(1, BandargahInvestment.objects.all().count())
        self.assertEqual(old_sekke, self.participant.sekke.amount + 3000)
        BandargahInvestment.objects.all().delete()

    @mock.patch('kabaramadalapeste.views.render')
    def test_island_page_ok(self, render_mock):
        render_mock.return_value = HttpResponse('OK')
        self.participant.set_start_island(self.island)
        self.participant.put_anchor_on_current_island()

        self.client.force_login(self.participant.member)
        response = self.client.get(reverse('kabaramadalapeste:island'))
        render_mock.assert_called_once()
        self.assertEqual(response.status_code, 200)

    def test_island_page_not_anchored(self):
        self.participant.set_start_island(self.island)

        self.client.force_login(self.participant.member)
        response = self.client.get(reverse('kabaramadalapeste:island'))
        self.assertEqual(response.status_code, 302)

    def test_island_page_not_on_island(self):
        self.client.force_login(self.participant.member)
        response = self.client.get(reverse('kabaramadalapeste:island'))
        self.assertEqual(response.status_code, 302)
