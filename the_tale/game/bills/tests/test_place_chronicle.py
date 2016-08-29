# coding: utf-8

import mock
import datetime

from the_tale.game.bills.prototypes import BillPrototype, VotePrototype
from the_tale.game.bills.bills import PlaceChronicle

from the_tale.game.bills import relations

from the_tale.game.bills.tests.helpers import BaseTestPrototypes


class PlaceChronicleTests(BaseTestPrototypes):

    def setUp(self):
        super(PlaceChronicleTests, self).setUp()

        self.bill_data = PlaceChronicle(place_id=self.place1.id, old_name_forms=self.place1.utg_name, power_bonus=relations.POWER_BONUS_CHANGES.UP)
        self.bill = BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', self.bill_data, chronicle_on_accepted='chronicle-on-accepted')


    def test_create(self):
        self.assertEqual(self.bill.data.place_id, self.place1.id)
        self.assertTrue(self.bill.data.power_bonus.is_UP)

    def test_actors(self):
        self.assertEqual([id(a) for a in self.bill_data.actors], [id(self.place1)])

    def test_update(self):
        form = self.bill.data.get_user_form_update(post={'caption': 'new-caption',
                                                         'rationale': 'new-rationale',
                                                         'chronicle_on_accepted': 'chronicle-on-accepted-2',
                                                         'place': self.place2.id,
                                                         'power_bonus': relations.POWER_BONUS_CHANGES.DOWN })
        self.assertTrue(form.is_valid())

        self.bill.update(form)

        self.bill = BillPrototype.get_by_id(self.bill.id)

        self.assertEqual(self.bill.data.place_id, self.place2.id)
        self.assertTrue(self.bill.data.power_bonus.is_DOWN)


    @mock.patch('the_tale.game.bills.conf.bills_settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def check_apply(self, change_power_mock):
        VotePrototype.create(self.account2, self.bill, False)
        VotePrototype.create(self.account3, self.bill, True)

        form = PlaceChronicle.ModeratorForm({'approved': True})
        self.assertTrue(form.is_valid())
        self.bill.update_by_moderator(form)

        with mock.patch('the_tale.game.places.objects.Place.cmd_change_power') as cmd_change_power:
            self.assertTrue(self.bill.apply())

        self.assertEqual(cmd_change_power.call_args_list, change_power_mock)

        bill = BillPrototype.get_by_id(self.bill.id)
        self.assertTrue(bill.state.is_ACCEPTED)

    def test_apply_up(self):
        self.bill.data.power_bonus = relations.POWER_BONUS_CHANGES.UP
        self.check_apply([mock.call(has_place_in_preferences=False, has_person_in_preferences=False, power=6400, hero_id=None)])

    def test_apply_down(self):
        self.bill.data.power_bonus = relations.POWER_BONUS_CHANGES.DOWN
        self.check_apply([mock.call(has_place_in_preferences=False, has_person_in_preferences=False, power=-6400, hero_id=None)])

    def test_apply_not_change(self):
        self.bill.data.power_bonus = relations.POWER_BONUS_CHANGES.NOT_CHANGE
        self.check_apply([])
