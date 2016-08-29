# coding: utf-8

import rels
from rels.django import DjangoEnum

from the_tale.common.utils.decorators import lazy_property
from the_tale.common.postponed_tasks.prototypes import PostponedLogic, POSTPONED_TASK_LOGIC_RESULT
from the_tale.common.utils.logic import random_value_by_priority

from the_tale.finances.bank.transaction import Transaction

from the_tale.amqp_environment import environment
from the_tale.accounts.prototypes import AccountPrototype, RandomPremiumRequestPrototype

from the_tale.finances.shop import relations
from the_tale.finances.shop.logic import transaction_logic
from the_tale.finances.shop.conf import payments_settings
from the_tale.finances.shop import exceptions


class BASE_BUY_TASK_STATE(DjangoEnum):
    records = ( ('TRANSACTION_REQUESTED', 1, u'запрошены средства'),
                ('TRANSACTION_REJECTED', 2, u'недостаточно средств'),
                ('TRANSACTION_FROZEN', 3, u'средства выделены'),
                ('WAIT_TRANSACTION_CONFIRMATION', 4, u'ожидает подтверждение платежа'),
                ('SUCCESSED', 5, u'операция выполнена'),
                ('ERROR_IN_FREEZING_TRANSACTION',6, u'неверное состояние транзакции при замарозке средств'),
                ('ERROR_IN_CONFIRM_TRANSACTION', 7, u'неверное состояние транзакции при подтверждении траты'),
                ('WRONG_TASK_STATE', 8, u'ошибка при обрабокте задачи — неверное состояние') )



class BaseBuyTask(PostponedLogic):
    TYPE = None
    RELATION = BASE_BUY_TASK_STATE

    def __init__(self, account_id, transaction, state=None):
        super(BaseBuyTask, self).__init__()

        if state is None:
            state = self.RELATION.TRANSACTION_REQUESTED

        self.account_id = account_id
        self.state = state if isinstance(state, rels.Record) else self.RELATION.index_value[state]
        self.transaction = Transaction.deserialize(transaction) if isinstance(transaction, dict) else transaction

    def __eq__(self, other):
        return (self.state == other.state and
                self.transaction == other.transaction and
                self.account_id == other.account_id)

    def serialize(self):
        return { 'state': self.state.value,
                 'transaction': self.transaction.serialize(),
                 'account_id': self.account_id }

    @property
    def uuid(self): return self.account_id

    @property
    def error_message(self): return self.state.text

    @lazy_property
    def account(self): return AccountPrototype.get_by_id(self.account_id) if self.account_id is not None else None

    def process_transaction_requested(self, main_task):
        transaction_state = self.transaction.get_invoice_state()

        if transaction_state.is_REQUESTED:
            return POSTPONED_TASK_LOGIC_RESULT.WAIT
        if transaction_state.is_REJECTED:
            self.state = self.RELATION.TRANSACTION_REJECTED
            main_task.comment = 'invoice %d rejected' % self.transaction.invoice_id
            return POSTPONED_TASK_LOGIC_RESULT.ERROR
        elif transaction_state.is_FROZEN:
            self.state = self.RELATION.TRANSACTION_FROZEN
            self.on_process_transaction_requested__transaction_frozen(main_task)
            return POSTPONED_TASK_LOGIC_RESULT.CONTINUE
        else:
            self.state = self.RELATION.ERROR_IN_FREEZING_TRANSACTION
            main_task.comment = 'wrong invoice %d state %r on freezing step' % (self.transaction.invoice_id, transaction_state)
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

    def on_process_transaction_requested__transaction_frozen(self, main_task):
        main_task.extend_postsave_actions((lambda: environment.workers.accounts_manager.cmd_task(main_task.id),))

    def on_process_transaction_frozen(self, storage):
        raise NotImplementedError

    def process_transaction_frozen(self, main_task, storage): # pylint: disable=W0613
        self.on_process_transaction_frozen(storage=storage)
        self.transaction.confirm()

        self.state = self.RELATION.WAIT_TRANSACTION_CONFIRMATION
        return POSTPONED_TASK_LOGIC_RESULT.WAIT

    def process_transaction_confirmation(self, main_task):
        transaction_state = self.transaction.get_invoice_state()

        if transaction_state.is_FROZEN:
            return POSTPONED_TASK_LOGIC_RESULT.WAIT
        elif transaction_state.is_CONFIRMED:
            self.state = self.RELATION.SUCCESSED
            self.process_referrals()
            return POSTPONED_TASK_LOGIC_RESULT.SUCCESS
        else:
            self.state = self.RELATION.ERROR_IN_CONFIRM_TRANSACTION
            main_task.comment = 'wrong invoice %d state %r on confirmation step' % (self.transaction.invoice_id, transaction_state)
            return POSTPONED_TASK_LOGIC_RESULT.ERROR


    def process(self, main_task, storage=None): # pylint: disable=W0613

        if self.state.is_TRANSACTION_REQUESTED:
            return self.process_transaction_requested(main_task)

        elif self.state.is_TRANSACTION_FROZEN:
            return self.process_transaction_frozen(main_task, storage=storage)

        elif self.state.is_WAIT_TRANSACTION_CONFIRMATION:
            return self.process_transaction_confirmation(main_task)

        else:
            main_task.comment = 'wrong task state %r' % self.state
            self.state = self.RELATION.WRONG_TASK_STATE
            return POSTPONED_TASK_LOGIC_RESULT.ERROR


    def process_referrals(self):
        invoice = self.transaction.get_invoice()

        if invoice.amount >= 0:
            return

        buyer = AccountPrototype.get_by_id(invoice.recipient_id)

        if buyer.referral_of_id is None:
            return

        owner = AccountPrototype.get_by_id(buyer.referral_of_id)

        transaction_logic(account=owner,
                          amount=-int(invoice.amount*payments_settings.REFERRAL_BONUS),
                          description=u'Часть от потраченного вашим рефералом',
                          uid='referral-bonus',
                          force=True)


class BaseLogicBuyTask(BaseBuyTask):

    def on_process_transaction_requested__transaction_frozen(self, main_task):
        main_task.extend_postsave_actions((lambda: environment.workers.supervisor.cmd_logic_task(self.account_id, main_task.id),))


class BuyPremium(BaseBuyTask):
    TYPE = 'purchase-premium'

    def __init__(self, days, **kwargs):
        super(BuyPremium, self).__init__(**kwargs)
        self.days = days

    def __eq__(self, other):
        return (super(BuyPremium, self).__eq__(other) and
                self.days == other.days )

    def serialize(self):
        data = super(BuyPremium, self).serialize()
        data['days'] = self.days
        return data

    def on_process_transaction_frozen(self, **kwargs):
        self.account.prolong_premium(days=self.days)
        self.account.save()


class BaseBuyHeroMethod(BaseLogicBuyTask):
    TYPE = None
    ARGUMENTS = ()
    METHOD = None

    def __init__(self, **kwargs):
        arguments = {name: value for name, value in kwargs.iteritems() if name in self.ARGUMENTS}
        for name in arguments:
            del kwargs[name]

        super(BaseBuyHeroMethod, self).__init__(**kwargs)

        self.arguments = self.deserialize_arguments(arguments)

    def __eq__(self, other):
        return (super(BaseBuyHeroMethod, self).__eq__(other) and
                self.arguments == other.arguments )

    def serialize_arguments(self):
        return self.arguments

    @classmethod
    def deserialize_arguments(cls, arguments):
        return arguments

    def serialize(self):
        data = super(BaseBuyHeroMethod, self).serialize()
        if set(data.iterkeys()) & set(self.arguments.iterkeys()):
            raise exceptions.BuyHeroMethodSerializationError()
        data.update(self.serialize_arguments())
        return data

    def on_process_transaction_frozen(self, storage, **kwargs):
        hero = storage.accounts_to_heroes[self.account_id]
        self.invoke_method(hero)
        storage.save_bundle_data(hero.actions.current_action.bundle_id)

    def invoke_method(self, hero):
        getattr(hero, self.METHOD)(**self.arguments)


class BuyPermanentPurchase(BaseBuyTask):
    TYPE = 'purchase-permanent-purchase'

    def __init__(self, purchase_type, **kwargs):
        super(BuyPermanentPurchase, self).__init__(**kwargs)
        self.purchase_type = purchase_type if isinstance(purchase_type, rels.Record) else relations.PERMANENT_PURCHASE_TYPE.index_value[purchase_type]

    def __eq__(self, other):
        return (super(BuyPermanentPurchase, self).__eq__(other) and
                self.purchase_type == other.purchase_type )

    def serialize(self):
        data = super(BuyPermanentPurchase, self).serialize()
        data['purchase_type'] = self.purchase_type.value
        return data

    def on_process_transaction_frozen(self, **kwargs):
        self.account.permanent_purchases.insert(self.purchase_type)
        self.account.save()


class BuyRandomPremiumChest(BaseBuyHeroMethod):
    TYPE = 'purchase-random-premium-chest'
    ARGUMENTS = ('message', )
    METHOD = None

    MESSAGE = u'''
<strong>Поздравляем!</strong><br/>

Благодаря Вам один из активных игроков получит подписку!<br/>

Вы получаете <strong>%(reward)s</strong><br/>
'''

    def get_reward_type(self):
        return random_value_by_priority([(record, record.priority)
                                         for record in relations.RANDOM_PREMIUM_CHEST_REWARD.records])

    def invoke_method(self, hero):
        reward = self.get_reward_type()

        result = getattr(hero, reward.hero_method)(**reward.arguments)

        if reward.is_NORMAL_ARTIFACT or reward.is_RARE_ARTIFACT or reward.is_EPIC_ARTIFACT:
            message = self.MESSAGE % {'reward': result.html_label()}
        else:
            message = self.MESSAGE % {'reward': reward.description}

        self.arguments['message'] = message

        RandomPremiumRequestPrototype.create(hero.account_id, days=payments_settings.RANDOM_PREMIUM_DAYS)

    @property
    def processed_data(self): return {'message': self.arguments['message'] }
