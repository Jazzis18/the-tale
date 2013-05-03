# coding: utf-8
import mock

from dext.settings import settings

from common.utils import testcase

from bank.tests.helpers import BankTestsMixin

from bank.prototypes import AccountPrototype, InvoicePrototype
from bank.relations import ENTITY_TYPE, CURRENCY_TYPE, INVOICE_STATE
from bank.conf import bank_settings
from bank.exceptions import BankError
from bank.transaction import Transaction


class TransactionTests(testcase.TestCase, BankTestsMixin):

    def setUp(self):
        super(TransactionTests, self).setUp()

    def create_transaction(self):
        return Transaction.create(recipient_type=ENTITY_TYPE.GAME_ACCOUNT,
                                  recipient_id=2,
                                  sender_type=ENTITY_TYPE.GAME_LOGIC,
                                  sender_id=3,
                                  currency=CURRENCY_TYPE.PREMIUM,
                                  amount=113)


    def test_create(self):
        with mock.patch('bank.workers.bank_processor.Worker.cmd_freeze_invoice') as cmd_freeze_invoice:
            transaction = self.create_transaction()
        self.assertEqual(cmd_freeze_invoice.call_count, 1)
        self.assertEqual(InvoicePrototype._model_class.objects.all().count(), 1)
        self.assertEqual(transaction.invoice_id, InvoicePrototype._model_class.objects.all()[0].id)
        self.assertTrue(InvoicePrototype._model_class.objects.all()[0].state._is_REQUESTED)

    def test_confirm(self):
        transaction = self.create_transaction()
        with mock.patch('bank.workers.bank_processor.Worker.cmd_confirm_invoice') as cmd_confirm_invoice:
            transaction.confirm()
        self.assertEqual(cmd_confirm_invoice.call_count, 1)

    def test_cancel(self):
        transaction = self.create_transaction()
        with mock.patch('bank.workers.bank_processor.Worker.cmd_cancel_invoice') as cmd_count_invoice:
            transaction.cancel()
        self.assertEqual(cmd_count_invoice.call_count, 1)