# coding: utf-8
import mock

from dext.common.utils.urls import url

from the_tale.common.utils.testcase import TestCase
from the_tale.common.postponed_tasks.prototypes import PostponedTaskPrototype

from the_tale.game.logic import create_test_map

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user, login_page_url, get_system_user

from the_tale.accounts.personal_messages.prototypes import MessagePrototype
from the_tale.accounts.personal_messages.models import Message
from the_tale.accounts.personal_messages import conf

class BaseRequestsTests(TestCase):

    def setUp(self):
        super(BaseRequestsTests, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user1', 'test_user1@test.com', '111111')
        self.account1 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user2', 'test_user2@test.com', '111111')
        self.account2 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user3', 'test_user3@test.com', '111111')
        self.account3 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user4', 'test_user4@test.com', '111111')
        self.account4 = AccountPrototype.get_by_id(account_id)


class IndexRequestsTests(BaseRequestsTests):

    def setUp(self):
        super(IndexRequestsTests, self).setUp()

        self.messages_1_2 = [MessagePrototype.create(self.account1, self.account2, 'message_1_2 1'),
                             MessagePrototype.create(self.account1, self.account2, 'message_1_2 2'),
                             MessagePrototype.create(self.account1, self.account2, 'message_1_2 3')]

        self.messages_2_1 = [MessagePrototype.create(self.account2, self.account1, 'message_2_1 1'),
                             MessagePrototype.create(self.account2, self.account1, 'message_2_1 2')]

        self.messages_3_1 = [MessagePrototype.create(self.account3, self.account1, 'message_3_1 1')]
        self.messages_3_2 = [MessagePrototype.create(self.account3, self.account2, 'message_3_2 1')]

    def test_initialize(self):
        self.assertEqual(Message.objects.all().count(), 7)

    def test_unlogined_index(self):
        request_url = url('accounts:messages:')
        self.check_redirect(request_url, login_page_url(request_url))

    def test_fast_account(self):
        self.request_login(self.account1.email)
        self.account1.is_fast = True
        self.account1.save()
        self.check_html_ok(self.request_html(url('accounts:messages:')), texts=['common.fast_account'])

    def test_unlogined_sent(self):
        request_url = url('accounts:messages:sent')
        self.check_redirect(request_url, login_page_url(request_url))

    def test_index(self):
        self.request_login(self.account1.email)
        texts = [('message_2_1 1', 1),
                 ('message_2_1 2', 1),
                 ('message_3_1 1', 1),]

        self.check_html_ok(self.request_html(url('accounts:messages:')), texts=texts)

    def test_index_no_messages(self):
        self.request_login('test_user4@test.com')
        self.check_html_ok(self.request_html(url('accounts:messages:')), texts=[('pgf-no-messages', 1)])

    def test_sent(self):
        self.request_login(self.account1.email)
        texts = [('message_1_2 1', 1),
                 ('message_1_2 2', 1),
                 ('message_1_2 3', 1),]

        self.check_html_ok(self.request_html(url('accounts:messages:sent')), texts=texts)

    def test_sent_no_messages(self):
        self.request_login('test_user4@test.com')
        self.check_html_ok(self.request_html(url('accounts:messages:sent')), texts=[('pgf-no-messages', 1)])

    def test_index_second_page(self):
        for i in xrange(conf.settings.MESSAGES_ON_PAGE):
            MessagePrototype.create(self.account2, self.account1, 'test message_2_1 %d' % i)

        texts = []
        for i in xrange(conf.settings.MESSAGES_ON_PAGE):
            texts.append(('test message_2_1 %d' % i, 1))

        self.request_login(self.account1.email)
        self.check_html_ok(self.request_html(url('accounts:messages:')), texts=texts)

    def test_index_big_page_number(self):
        self.request_login(self.account1.email)
        self.check_redirect(url('accounts:messages:')+'?page=2', url('accounts:messages:')+'?page=1')



class NewRequestsTests(BaseRequestsTests):

    def setUp(self):
        super(NewRequestsTests, self).setUp()
        self.request_login(self.account1.email)

    def test_unlogined(self):
        self.request_logout()
        request_url = url('accounts:messages:new')
        self.check_redirect(request_url, login_page_url(request_url))

    def test_fast_account(self):
        self.request_login(self.account1.email)
        self.account1.is_fast = True
        self.account1.save()
        self.check_html_ok(self.post_ajax_html(url('accounts:messages:new'), {'recipients': self.account2.id}), texts=['common.fast_account'])

    @mock.patch('the_tale.accounts.prototypes.AccountPrototype.is_ban_forum', True)
    def test_banned_account(self):
        self.request_login(self.account1.email)
        self.check_html_ok(self.post_ajax_html(url('accounts:messages:new'), {'recipients': self.account2.id}), texts=['common.ban_forum'])

    def test_wrong_recipient_id(self):
        self.check_html_ok(self.post_ajax_html(url('accounts:messages:new'), {'recipients': 'aaa'}),
                           texts=[('pgf-error-form_errors', 1)])

    def test_recipient_not_found(self):
        self.check_html_ok(self.post_ajax_html(url('accounts:messages:new'), {'recipients': 666}),
                           texts=[('pgf-error-unexisted_account', 1)])

    def test_answer_wrong_message_id(self):
        MessagePrototype.create(self.account2, self.account1, 'message_2_1 1')
        self.check_html_ok(self.post_ajax_html(url('accounts:messages:new', answer_to='aaa'), {'recipients': self.account2.id}),
                           texts=[('pgf-error-answer_to.wrong_format', 1)])

    def test_answer_to_not_found(self):
        MessagePrototype.create(self.account2, self.account1, 'message_2_1 1')
        self.check_html_ok(self.post_ajax_html(url('accounts:messages:new', answer_to=666), {'recipients': self.account2.id}),
                           texts=[('pgf-error-answer_to.wrong_value', 1)])

    def test_answer_to_no_permissions(self):
        message = MessagePrototype.create(self.account2, self.account3, 'message_2_3 1')
        self.check_html_ok(self.post_ajax_html(url('accounts:messages:new', answer_to=message.id), {'recipients': self.account2.id}),
                           texts=[('pgf-error-no_permissions_to_answer_to', 1)])

    def test_success(self):
        self.check_html_ok(self.post_ajax_html(url('accounts:messages:new'), {'recipients': self.account2.id}),
                           texts=[('pgf-new-message-form', 1)])

    def test_success_multiply_accoutns(self):
        self.check_html_ok(self.post_ajax_html(url('accounts:messages:new'), {'recipients': ('%d,%d' % (self.account2.id, self.account3.id))}),
                           texts=[('pgf-new-message-form', 1),
                                  (self.account2.nick, 1),
                                  (self.account3.nick, 1) ])


    def test_answer_to(self):
        message = MessagePrototype.create(self.account2, self.account1, 'message_2_1 1')
        self.check_html_ok(self.post_ajax_html(url('accounts:messages:new', answer_to=message.id), {'recipients': self.account2.id}),
                           texts=[('pgf-new-message-form', 1),
                                  ('message_2_1 1', 1)])

    def test_sent_to_system_user(self):
        recipients = '%d,%d' % (self.account2.id, get_system_user().id)
        self.check_html_ok(self.post_ajax_html(url('accounts:messages:new'), {'recipients': recipients}),
                           texts=[('pgf-error-system_user', 1)])

    def test_sent_to_fast_user(self):
        self.account3.is_fast = True
        self.account3.save()
        recipients = '%d,%d' % (self.account2.id, self.account3.id)
        self.check_html_ok(self.post_ajax_html(url('accounts:messages:new'), {'recipients': recipients}),
                           texts=[('pgf-error-fast_account', 1)])


class CreateRequestsTests(BaseRequestsTests):

    def setUp(self):
        super(CreateRequestsTests, self).setUp()
        self.request_login(self.account1.email)

    def test_unlogined(self):
        self.request_logout()
        self.check_ajax_error(self.post_ajax_json(url('accounts:messages:create'), {'text': 'test-message'}), 'common.login_required')
        self.assertEqual(Message.objects.all().count(), 0)

    def test_fast_account(self):
        self.request_login(self.account1.email)
        self.account1.is_fast = True
        self.account1.save()
        self.check_ajax_error(self.post_ajax_json(url('accounts:messages:create'), {'text': 'test-message'}), 'common.fast_account')

    @mock.patch('the_tale.accounts.prototypes.AccountPrototype.is_ban_forum', True)
    def test_banned_account(self):
        self.request_login(self.account1.email)
        self.check_ajax_error(self.post_ajax_json(url('accounts:messages:create'), {'text': 'test-message'}), 'common.ban_forum')

    def test_wrong_recipient_id(self):
        self.check_ajax_error(self.post_ajax_json(url('accounts:messages:create'), {'text': 'test-message', 'recipients': 'aaa'}),
                              'form_errors')
        self.assertEqual(Message.objects.all().count(), 0)

    def test_recipient_not_found(self):
        self.check_ajax_error(self.post_ajax_json(url('accounts:messages:create'), {'text': 'test-message', 'recipients': '666'}),
                              'unexisted_account')
        self.assertEqual(Message.objects.all().count(), 0)

    def test_form_errors(self):
        self.check_ajax_error(self.post_ajax_json(url('accounts:messages:create'), {'text': '', 'recipients': self.account2.id}),
                              'form_errors')
        self.assertEqual(Message.objects.all().count(), 0)

    def test_success(self):

        with mock.patch('the_tale.accounts.workers.accounts_manager.Worker.cmd_task') as cmd_task:
            with self.check_delta(PostponedTaskPrototype._db_count, 1):
                self.check_ajax_processing(self.post_ajax_json(url('accounts:messages:create'), {'text': 'test-message', 'recipients': self.account2.id}))

        task = PostponedTaskPrototype._db_latest()

        self.assertEqual(cmd_task.call_args_list, [mock.call(task.id)])

        self.assertEqual(task.internal_logic.message, 'test-message')
        self.assertEqual(task.internal_logic.account_id, self.account1.id)
        self.assertEqual(task.internal_logic.recipients, [self.account2.id])


    def test_success_multiply_accoutns(self):
        with self.check_delta(PostponedTaskPrototype._db_count, 1):
            self.check_ajax_processing(self.post_ajax_json(url('accounts:messages:create'), {'text': 'test-message', 'recipients': ('%d,%d' % (self.account2.id, self.account3.id))}))

        task = PostponedTaskPrototype._db_latest()

        self.assertEqual(task.internal_logic.message, 'test-message')
        self.assertEqual(task.internal_logic.account_id, self.account1.id)
        self.assertEqual(task.internal_logic.recipients, [self.account2.id, self.account3.id])

    def test_sent_to_system_user(self):
        self.check_ajax_error(self.post_ajax_json(url('accounts:messages:create'), {'text': 'test-message', 'recipients': ('%d,%d' % (self.account2.id, get_system_user().id))}),
                              'system_user')
        self.assertEqual(Message.objects.all().count(), 0)

    def test_sent_to_fast_user(self):
        self.account3.is_fast = True
        self.account3.save()
        self.check_ajax_error(self.post_ajax_json(url('accounts:messages:create'), {'text': 'test-message', 'recipients': ('%d,%d' % (self.account2.id, self.account3.id))}),
                              'fast_account')
        self.assertEqual(Message.objects.all().count(), 0)


class DeleteRequestsTests(BaseRequestsTests):

    def setUp(self):
        super(DeleteRequestsTests, self).setUp()
        self.message = MessagePrototype.create(self.account1, self.account2, 'message_1_2 1')

    def test_unlogined(self):
        self.request_logout()
        self.check_ajax_error(self.post_ajax_json(url('accounts:messages:delete', self.message.id)), 'common.login_required')

    def test_fast_account(self):
        self.request_login(self.account1.email)
        self.account1.is_fast = True
        self.account1.save()
        self.check_ajax_error(self.post_ajax_json(url('accounts:messages:delete', self.message.id)), 'common.fast_account')

    def test_delete_no_permissions(self):
        self.request_login('test_user3@test.com')
        self.check_ajax_error(self.post_ajax_json(url('accounts:messages:delete', self.message.id)), 'no_permissions')

    def test_delete_from_sender(self):
        self.request_login(self.account1.email)
        self.check_ajax_ok(self.post_ajax_json(url('accounts:messages:delete', self.message.id)))
        message = MessagePrototype.get_by_id(self.message.id)
        self.assertTrue(message.hide_from_sender)
        self.assertFalse(message.hide_from_recipient)

    def test_delete_from_recipient(self):
        self.request_login(self.account2.email)
        self.check_ajax_ok(self.post_ajax_json(url('accounts:messages:delete', self.message.id)))
        message = MessagePrototype.get_by_id(self.message.id)
        self.assertFalse(message.hide_from_sender)
        self.assertTrue(message.hide_from_recipient)



class DeleteAllRequestsTests(BaseRequestsTests):

    def setUp(self):
        super(DeleteAllRequestsTests, self).setUp()
        self.message = MessagePrototype.create(self.account1, self.account2, 'message_1_2 1')
        self.message_2 = MessagePrototype.create(self.account2, self.account1, 'message_2_1 1')

    def test_unlogined(self):
        self.request_logout()
        self.check_ajax_error(self.post_ajax_json(url('accounts:messages:delete-all')), 'common.login_required')

    def test_fast_account(self):
        self.request_login(self.account1.email)
        self.account1.is_fast = True
        self.account1.save()
        self.check_ajax_error(self.post_ajax_json(url('accounts:messages:delete-all')), 'common.fast_account')

    def test_delete(self):
        self.request_login(self.account1.email)
        self.check_ajax_ok(self.post_ajax_json(url('accounts:messages:delete-all')))

        self.message.reload()
        self.message_2.reload()

        self.assertTrue(self.message.hide_from_sender)
        self.assertFalse(self.message.hide_from_recipient)
        self.assertFalse(self.message_2.hide_from_sender)
        self.assertTrue(self.message_2.hide_from_recipient)
