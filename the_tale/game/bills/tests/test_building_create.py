# coding: utf-8

import mock
import datetime

from the_tale.linguistics.tests import helpers as linguistics_helpers

from the_tale.game import names

from the_tale.game.places.models import Building
from the_tale.game.places import storage as places_storage
from the_tale.game.places.prototypes import BuildingPrototype

from the_tale.game.bills.relations import BILL_STATE
from the_tale.game.bills.prototypes import BillPrototype, VotePrototype
from the_tale.game.bills.bills import BuildingCreate
from the_tale.game.bills.tests.helpers import BaseTestPrototypes


class BuildingCreateTests(BaseTestPrototypes):

    def setUp(self):
        super(BuildingCreateTests, self).setUp()

        self.person_1 = sorted(self.place1.persons, key=lambda p: -p.total_politic_power_fraction)[0]
        self.person_2 = sorted(self.place2.persons, key=lambda p: -p.total_politic_power_fraction)[-1]

        self.bill_data = BuildingCreate(person_id=self.person_1.id, old_place_name_forms=self.place1.utg_name, utg_name=names.generator.get_test_name(u'building-name'))
        self.bill = BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', self.bill_data, chronicle_on_accepted='chronicle-on-accepted')


    def test_create(self):
        self.assertEqual(self.bill.data.person_id, self.person_1.id)

    def test_actors(self):
        self.assertEqual([id(a) for a in self.bill_data.actors], [id(self.person_1.place)])

    def test_update(self):
        data = linguistics_helpers.get_word_post_data(names.generator.get_test_name('new-building-name'), prefix='name')
        data.update({'caption': 'new-caption',
                     'rationale': 'new-rationale',
                     'chronicle_on_accepted': 'chronicle-on-accepted',
                     'person': self.person_2.id })

        form = self.bill.data.get_user_form_update(post=data)
        self.assertTrue(form.is_valid())

        self.bill.update(form)

        self.bill = BillPrototype.get_by_id(self.bill.id)

        self.assertEqual(self.bill.data.person_id, self.person_2.id)
        self.assertEqual(self.bill.data.base_name, u'new-building-name-нс,ед,им')

    def check_persons_from_place_in_choices(self, place, persons_ids):
        for person in place.persons:
            if not person.has_building:
                self.assertTrue(person.id in persons_ids)
            else:
                self.assertFalse(person.id in persons_ids)


    def test_user_form_choices(self):

        BuildingPrototype.create(self.place2.persons[0], utg_name=names.generator.get_test_name('r-building-name'))

        form = self.bill.data.get_user_form_update(initial={'person': self.bill.data.person_id })

        persons_ids = []

        for city_name, person_choices in form.fields['person'].choices:
            persons_ids.extend(choice_id for choice_id, choice_name in person_choices)

        self.assertTrue(self.bill.data.person_id in persons_ids)

        self.check_persons_from_place_in_choices(self.place1, persons_ids)
        self.check_persons_from_place_in_choices(self.place2, persons_ids)
        self.check_persons_from_place_in_choices(self.place3, persons_ids)


    @mock.patch('the_tale.game.bills.conf.bills_settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def test_apply(self):
        self.assertEqual(Building.objects.all().count(), 0)

        VotePrototype.create(self.account2, self.bill, False)
        VotePrototype.create(self.account3, self.bill, True)

        noun = names.generator.get_test_name('r-building-name')

        data = linguistics_helpers.get_word_post_data(noun, prefix='name')
        data.update({'approved': True})

        form = BuildingCreate.ModeratorForm(data)

        self.assertTrue(form.is_valid())
        self.bill.update_by_moderator(form)

        self.assertTrue(self.bill.apply())

        bill = BillPrototype.get_by_id(self.bill.id)
        self.assertTrue(bill.state.is_ACCEPTED)

        self.assertEqual(Building.objects.all().count(), 1)

        building = places_storage.buildings.all()[0]

        self.assertEqual(building.person.id, self.person_1.id)
        self.assertEqual(building.place.id, self.place1.id)
        self.assertEqual(building.utg_name, noun)


    @mock.patch('the_tale.game.bills.conf.bills_settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def test_duplicate_apply(self):
        self.assertEqual(Building.objects.all().count(), 0)

        VotePrototype.create(self.account2, self.bill, False)
        VotePrototype.create(self.account3, self.bill, True)

        noun = names.generator.get_test_name('building-name')
        data = linguistics_helpers.get_word_post_data(noun, prefix='name')
        data.update({'approved': True})

        form = BuildingCreate.ModeratorForm(data)

        self.assertTrue(form.is_valid())
        self.bill.update_by_moderator(form)
        self.assertTrue(self.bill.apply())

        dup_noun = names.generator.get_test_name('dup-building-name')
        data = linguistics_helpers.get_word_post_data(dup_noun, prefix='name')
        data.update({'approved': True})

        form = BuildingCreate.ModeratorForm(data)

        bill = BillPrototype.get_by_id(self.bill.id)
        bill.state = BILL_STATE.VOTING
        bill.save()

        self.assertTrue(form.is_valid())
        bill.update_by_moderator(form)

        self.assertTrue(bill.apply())

        self.assertEqual(Building.objects.all().count(), 1)
        self.assertEqual(BuildingPrototype._db_get_object(0).utg_name, noun)
        self.assertNotEqual(BuildingPrototype._db_get_object(0).utg_name, dup_noun)


    @mock.patch('the_tale.game.bills.conf.bills_settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def test_has_meaning__duplicate(self):
        self.assertEqual(Building.objects.all().count(), 0)

        VotePrototype.create(self.account2, self.bill, False)
        VotePrototype.create(self.account3, self.bill, True)

        noun = names.generator.get_test_name('building-name')
        data = linguistics_helpers.get_word_post_data(noun, prefix='name')
        data.update({'approved': True})

        form = BuildingCreate.ModeratorForm(data)

        self.assertTrue(form.is_valid())
        self.bill.update_by_moderator(form)
        self.assertTrue(self.bill.apply())

        dup_noun = names.generator.get_test_name('dup-building-name')
        data = linguistics_helpers.get_word_post_data(dup_noun, prefix='name')
        data.update({'approved': True})

        form = BuildingCreate.ModeratorForm(data)

        bill = BillPrototype.get_by_id(self.bill.id)
        bill.state = BILL_STATE.VOTING
        bill.save()

        self.assertTrue(form.is_valid())
        bill.update_by_moderator(form)

        self.assertFalse(bill.has_meaning())
