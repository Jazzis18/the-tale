# coding: utf-8

from the_tale.common.utils import testcase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map

from the_tale.game.cards import effects

from the_tale.game.postponed_tasks import ComplexChangeTask

from the_tale.game.cards.tests.helpers import CardsTestMixin
from the_tale.game.artifacts.relations import RARITY as ARTIFACT_RARITY


class GetArtifactMixin(CardsTestMixin):
    CARD = None
    RARITIES = None
    HAS_USELESS = False

    def setUp(self):
        super(GetArtifactMixin, self).setUp()
        create_test_map()

        result, account_1_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.account_1 = AccountPrototype.get_by_id(account_1_id)

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account_1)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

        self.card = self.CARD()


    def test_use(self):

        rarities = set()

        has_useless = False

        for i in xrange(10000):
            result, step, postsave_actions = self.card.use(**self.use_attributes(storage=self.storage, hero=self.hero))
            self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

            artifact = self.hero.bag.values()[0]
            self.hero.bag.pop_artifact(artifact)

            rarities.add(artifact.rarity)
            has_useless = has_useless or artifact.type.is_USELESS

        self.assertEqual(has_useless, self.HAS_USELESS)
        self.assertEqual(rarities, self.RARITIES)


    def test_use__full_bag(self):
        with self.check_delta(lambda: self.hero.bag.occupation, 1000):
            for i in xrange(1000):
                result, step, postsave_actions = self.card.use(**self.use_attributes(storage=self.storage, hero=self.hero))
                self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))


    def test_use_when_trading(self):
        from the_tale.game.actions.prototypes import ActionTradingPrototype

        action_idl = self.hero.actions.current_action
        action_trade = ActionTradingPrototype.create(hero=self.hero)

        result, step, postsave_actions = self.card.use(**self.use_attributes(storage=self.storage, hero=self.hero))
        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertEqual(self.hero.bag.occupation, 1)

        self.assertTrue(action_trade.replane_required)

        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.hero.actions.current_action, action_idl)

        self.assertEqual(self.hero.bag.occupation, 1)



class GetArtifactCommonTests(GetArtifactMixin, testcase.TestCase):
    CARD = effects.GetArtifactCommon
    RARITIES = set([ARTIFACT_RARITY.NORMAL, ARTIFACT_RARITY.RARE, ARTIFACT_RARITY.EPIC])
    HAS_USELESS = True

class GetArtifactUncommonTests(GetArtifactMixin, testcase.TestCase):
    CARD = effects.GetArtifactUncommon
    RARITIES = set([ARTIFACT_RARITY.NORMAL, ARTIFACT_RARITY.RARE, ARTIFACT_RARITY.EPIC])

class GetArtifactRareTests(GetArtifactMixin, testcase.TestCase):
    CARD = effects.GetArtifactRare
    RARITIES = set([ARTIFACT_RARITY.RARE, ARTIFACT_RARITY.EPIC])

class GetArtifactEpicTests(GetArtifactMixin, testcase.TestCase):
    CARD = effects.GetArtifactEpic
    RARITIES = set([ARTIFACT_RARITY.EPIC])
