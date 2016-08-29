# coding: utf-8
import random

import mock

from the_tale.amqp_environment import environment

from the_tale.common.utils import testcase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user

from the_tale.common.postponed_tasks.prototypes import POSTPONED_TASK_LOGIC_RESULT, PostponedTaskPrototype
from the_tale.common.postponed_tasks.tests.helpers import FakePostpondTaskPrototype

from the_tale.game import names

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map

from the_tale.game.cards import effects
from the_tale.game.cards import objects
from the_tale.game.cards.postponed_tasks import UseCardTask

from the_tale.game.places.prototypes import BuildingPrototype


class UseCardTaskTests(testcase.TestCase):

    def setUp(self):
        super(UseCardTaskTests, self).setUp()

        self.place_1, self.place_2, self.place_3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user_1', 'test_user_1@test.com', '111111')

        self.account = AccountPrototype.get_by_id(account_id)
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.building_1 = BuildingPrototype.create(person=self.place_1.persons[0], utg_name=names.generator.get_test_name('building-1-name'))

        environment.deinitialize()
        environment.initialize()

        self.highlevel = environment.workers.highlevel
        self.highlevel.process_initialize(0, 'highlevel')


        self.task_data = {'place_id': self.place_1.id,
                          'person_id': self.place_1.persons[0].id,
                          'building_id': self.building_1.id}

    def test_create(self):

        for card_effect in effects.EFFECTS.values():
            card = objects.Card(card_effect.TYPE)
            self.hero.cards.add_card(card)

            with self.check_delta(PostponedTaskPrototype._db_count, 1):
                task = card.activate(self.hero, data=self.task_data)

            self.assertTrue(task.internal_logic.state.is_UNPROCESSED)

    def test_serialization(self):
        card_effect = random.choice(effects.EFFECTS.values())
        card = objects.Card(card_effect.TYPE)
        self.hero.cards.add_card(card)

        task = card.activate(self.hero, data=self.task_data).internal_logic

        self.assertEqual(task.serialize(), UseCardTask.deserialize(task.serialize()).serialize())

    def test_response_data(self):
        card_effect = random.choice(effects.EFFECTS.values())
        card = objects.Card(card_effect.TYPE)
        self.hero.cards.add_card(card)

        with mock.patch.object(card_effect, 'use', lambda **kwargs: (UseCardTask.RESULT.SUCCESSED, None, ())):
            task = card.activate(self.hero, data=self.task_data).internal_logic
            task.process(FakePostpondTaskPrototype(), self.storage)

        self.assertEqual(task.processed_data, {})

    def test_process_can_not_process(self):

        card_effect = random.choice(effects.EFFECTS.values())
        card = objects.Card(card_effect.TYPE)
        self.hero.cards.add_card(card)

        task = card.activate(self.hero, data=self.task_data).internal_logic

        with mock.patch.object(card_effect, 'use', lambda **kwargs: (UseCardTask.RESULT.FAILED, None, ())):
            self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
            self.assertEqual(task.state, UseCardTask.STATE.CAN_NOT_PROCESS)

    def test_process_success(self):
        card_effect = random.choice(effects.EFFECTS.values())
        card = objects.Card(card_effect.TYPE)
        self.hero.cards.add_card(card)

        task = card.activate(self.hero, data=self.task_data).internal_logic

        with mock.patch.object(card_effect, 'use', lambda **kwargs: (UseCardTask.RESULT.SUCCESSED, None, ())):
            self.assertEqual(task.process(FakePostpondTaskPrototype(), storage=self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        self.assertEqual(task.state, UseCardTask.STATE.PROCESSED)

    def test_process_second_step_error(self):

        card_effect = random.choice(effects.EFFECTS.values())
        card = objects.Card(card_effect.TYPE)
        self.hero.cards.add_card(card)

        task = card.activate(self.hero, data=self.task_data).internal_logic

        with mock.patch.object(card_effect, 'use', lambda **kwargs: (UseCardTask.RESULT.CONTINUE, UseCardTask.STEP.HIGHLEVEL, ())):
            self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.CONTINUE)

        self.assertTrue(task.step.is_HIGHLEVEL)
        self.assertEqual(task.state, UseCardTask.STATE.UNPROCESSED)

        with mock.patch.object(card_effect, 'use', lambda **kwargs: (UseCardTask.RESULT.FAILED, None, ())):
            self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)

        self.assertEqual(task.state, UseCardTask.STATE.CAN_NOT_PROCESS)
