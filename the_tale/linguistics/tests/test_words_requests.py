# coding: utf-8# coding: utf-8
import random

import mock

from dext.common.utils.urls import url
from dext.common.utils import s11n

from utg import relations as utg_relations
from utg import words as utg_words
from utg import data as utg_data


from the_tale.common.utils.testcase import TestCase
from the_tale.common.utils.permissions import sync_group

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user, login_page_url

from the_tale.game.logic import create_test_map

from .. import prototypes
from .. import relations
from .. import logic
from .. import storage
from ..conf import linguistics_settings
from ..forms import WORD_FIELD_PREFIX

from . import helpers



class BaseRequestsTests(TestCase):

    def setUp(self):
        super(BaseRequestsTests, self).setUp()

        create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        self.moderator = self.accounts_factory.create_account()

        group = sync_group(linguistics_settings.MODERATOR_GROUP_NAME, ['linguistics.moderate_word'])
        group.user_set.add(self.moderator._model)




class IndexRequestsTests(BaseRequestsTests):

    def test_state_errors(self):
        self.check_html_ok(self.request_html(url('linguistics:words:', state='www')), texts=['linguistics.words.state.wrong_format'])
        self.check_html_ok(self.request_html(url('linguistics:words:', state=666)), texts=['linguistics.words.state.not_found'], status_code=404)

    def test_type_errors(self):
        self.check_html_ok(self.request_html(url('linguistics:words:', type='www')), texts=['linguistics.words.type.wrong_format'])
        self.check_html_ok(self.request_html(url('linguistics:words:', type=666)), texts=['linguistics.words.type.not_found'], status_code=404)

    def create_words(self):
        type_1, type_2, type_3 = random.sample(relations.ALLOWED_WORD_TYPE.records, 3)

        word_1 = prototypes.WordPrototype.create(utg_words.Word.create_test_word(type_1.utg_type, prefix=u'w1-'))
        word_2 = prototypes.WordPrototype.create(utg_words.Word.create_test_word(type_2.utg_type, prefix=u'w2-'))
        word_3 = prototypes.WordPrototype.create(utg_words.Word.create_test_word(type_3.utg_type, prefix=u'w3-'))

        word_2.state = relations.WORD_STATE.IN_GAME
        word_2.save()

        return word_1, word_2, word_3

    def test_success(self):
        word_1, word_2, word_3 = self.create_words()

        texts = [word_1.utg_word.normal_form(),
                 word_2.utg_word.normal_form(),
                 word_3.utg_word.normal_form(),
                 ('pgf-no-words-message', 0)]

        self.check_html_ok(self.request_html(url('linguistics:words:')), texts=texts)


    def test_success__no_messages(self):
        texts = ['pgf-no-words-message']
        self.check_html_ok(self.request_html(url('linguistics:words:')), texts=texts)


    def test_filter_state(self):
        word_1, word_2, word_3 = self.create_words()

        texts = [word_1.utg_word.normal_form(),
                 (word_2.utg_word.normal_form(), 0),
                 word_3.utg_word.normal_form() ]

        self.check_html_ok(self.request_html(url('linguistics:words:', state=relations.WORD_STATE.ON_REVIEW.value)), texts=texts)

    def test_filter_type(self):
        word_1, word_2, word_3 = self.create_words()

        texts = [(word_1.utg_word.normal_form(), 0),
                 (word_2.utg_word.normal_form(), 0),
                 word_3.utg_word.normal_form() ]

        self.check_html_ok(self.request_html(url('linguistics:words:', type=word_3.type.value)), texts=texts)



class NewRequestsTests(BaseRequestsTests):

    def setUp(self):
        super(NewRequestsTests, self).setUp()
        self.request_login(self.account_1.email)

        result, account_id, bundle_id = register_user('test_user2', 'test_user2@test.com', '111111')
        self.account_2 = AccountPrototype.get_by_id(account_id)

    def test_logic_required(self):
        self.request_logout()
        word_type = utg_relations.WORD_TYPE.records[0]
        requested_url = url('linguistics:words:new', type=word_type.value, parent='xxx')
        self.check_redirect(requested_url, login_page_url(requested_url))

    def test_type_errors(self):
        self.check_html_ok(self.request_html(url('linguistics:words:new')), texts=['linguistics.words.type.not_specified'])
        self.check_html_ok(self.request_html(url('linguistics:words:new', type='www')), texts=['linguistics.words.type.wrong_format'])
        self.check_html_ok(self.request_html(url('linguistics:words:new', type=666)), texts=['linguistics.words.type.not_found'], status_code=404)

    def test_parent_errors(self):
        word_type = utg_relations.WORD_TYPE.records[0]
        self.check_html_ok(self.request_html(url('linguistics:words:new', type=word_type.value, parent='xxx')), texts=['linguistics.words.parent.wrong_format'])
        self.check_html_ok(self.request_html(url('linguistics:words:new', type=word_type.value, parent=666)), texts=['linguistics.words.parent.not_found'], status_code=404)

    def test_displaying_fields_for_all_forms(self):
        for word_type in utg_relations.WORD_TYPE.records:
            requested_url = url('linguistics:words:new', type=word_type.value)

            texts = []

            for key, index in utg_data.WORDS_CACHES[word_type].iteritems():
                if logic.key_is_synomym(key):
                    continue
                texts.append(('%s_%d ' % (WORD_FIELD_PREFIX, index)))

            self.check_html_ok(self.request_html(requested_url), texts=texts)


    def test_displaying_fields_for_all_forms__with_parent(self):
        for word_type in utg_relations.WORD_TYPE.records:
            word = prototypes.WordPrototype.create(utg_words.Word.create_test_word(word_type, prefix=u'w-'), author=self.account_1)
            requested_url = url('linguistics:words:new', type=word.type.value, parent=word.id)

            texts = []

            for key, index in utg_data.WORDS_CACHES[word_type].iteritems():
                if logic.key_is_synomym(key):
                    continue
                texts.append(('%s_%d ' % (WORD_FIELD_PREFIX, index)))
                texts.append(word.utg_word.forms[index])

            for static_property, required in word.type.properties.iteritems():
                texts.append(('%s_%s ' % (WORD_FIELD_PREFIX, static_property.__name__), 1))

            self.check_html_ok(self.request_html(requested_url), texts=texts)


    def test_can_not_replace_onreview_word_from_another_author(self):
        for word_type in utg_relations.WORD_TYPE.records:
            parent_word = utg_words.Word.create_test_word(word_type, prefix=u'parent-')

            parent = prototypes.WordPrototype.create(parent_word, author=self.account_2)

            requested_url = url('linguistics:words:new', type=word_type.value, parent=parent.id)

            texts = ['linguistics.words.new.can_not_edit_anothers_word']

            self.check_html_ok(self.request_html(requested_url), texts=texts)


    def test_not_equal_types(self):
        for word_type in utg_relations.WORD_TYPE.records:
            wrong_type = random.choice(utg_relations.WORD_TYPE.records)
            while wrong_type == word_type:
                wrong_type = random.choice(utg_relations.WORD_TYPE.records)

            word = prototypes.WordPrototype.create(utg_words.Word.create_test_word(word_type, prefix=u'w-'))

            requested_url = url('linguistics:words:new', type=wrong_type.value, parent=word.id)

            self.check_html_ok(self.request_html(requested_url), texts=['linguistics.words.new.unequal_types'])


    @mock.patch('the_tale.linguistics.prototypes.WordPrototype.has_child', lambda self: True)
    def test_has_on_review_copy(self):
        for word_type in utg_relations.WORD_TYPE.records:
            word = prototypes.WordPrototype.create(utg_words.Word.create_test_word(word_type, prefix=u'w-'))
            requested_url = url('linguistics:words:new', type=word.type.value, parent=word.id)
            self.check_html_ok(self.request_html(requested_url), texts=['linguistics.words.new.has_on_review_copy'])


class CreateRequestsTests(BaseRequestsTests):

    def setUp(self):
        super(CreateRequestsTests, self).setUp()
        self.request_login(self.account_1.email)

        result, account_id, bundle_id = register_user('test_user2', 'test_user2@test.com', '111111')
        self.account_2 = AccountPrototype.get_by_id(account_id)

    def test_login_required(self):
        self.request_logout()
        word_type = utg_relations.WORD_TYPE.records[0]
        word = utg_words.Word.create_test_word(word_type, prefix='w-')
        requested_url = url('linguistics:words:create', type=word_type.value)
        self.check_ajax_error(self.client.post(requested_url, helpers.get_word_post_data(word)), 'common.login_required')

    def test_type_errors(self):
        self.check_ajax_error(self.client.post(url('linguistics:words:create')), 'linguistics.words.type.not_specified')
        self.check_ajax_error(self.client.post(url('linguistics:words:create', type='www')), 'linguistics.words.type.wrong_format')
        self.check_ajax_error(self.client.post(url('linguistics:words:create', type=666)), 'linguistics.words.type.not_found')

    def test_create_with_all_fields(self):
        for word_type in utg_relations.WORD_TYPE.records:
            word = utg_words.Word.create_test_word(word_type, prefix='w-')
            requested_url = url('linguistics:words:create', type=word_type.value)

            with self.check_delta(prototypes.WordPrototype._db_count, 1):
                response = self.client.post(requested_url, helpers.get_word_post_data(word))

            last_prototype = prototypes.WordPrototype._db_latest()

            self.check_ajax_ok(response, data={'next_url': url('linguistics:words:show', last_prototype.id)})

            self.assertEqual(word, last_prototype.utg_word)


    def test_create__with_on_review_parent(self):
        for word_type in utg_relations.WORD_TYPE.records:
            parent_word = utg_words.Word.create_test_word(word_type, prefix=u'parent-')
            child_word = utg_words.Word.create_test_word(word_type, prefix=u'child-')

            parent = prototypes.WordPrototype.create(parent_word, author=self.account_1)

            requested_url = url('linguistics:words:create', type=word_type.value, parent=parent.id)

            with self.check_delta(prototypes.WordPrototype._db_count, 0):
                response = self.client.post(requested_url, helpers.get_word_post_data(child_word))

            last_prototype = prototypes.WordPrototype._db_latest()

            self.assertTrue(parent.created_at < last_prototype.created_at)

            self.check_ajax_ok(response, data={'next_url': url('linguistics:words:show', last_prototype.id)})

            self.assertEqual(child_word, last_prototype.utg_word)
            self.assertEqual(last_prototype.parent_id, None)

    def test_create__with_on_review_parent__by_moderator(self):
        self.request_login(self.moderator.email)

        for word_type in utg_relations.WORD_TYPE.records:
            parent_word = utg_words.Word.create_test_word(word_type, prefix=u'parent-')
            child_word = utg_words.Word.create_test_word(word_type, prefix=u'child-')

            parent = prototypes.WordPrototype.create(parent_word, author=self.account_1)

            requested_url = url('linguistics:words:create', type=word_type.value, parent=parent.id)

            with self.check_delta(prototypes.WordPrototype._db_count, 0):
                response = self.client.post(requested_url, helpers.get_word_post_data(child_word))

            last_prototype = prototypes.WordPrototype._db_latest()

            self.assertTrue(parent.created_at < last_prototype.created_at)

            self.check_ajax_ok(response, data={'next_url': url('linguistics:words:show', last_prototype.id)})

            self.assertEqual(child_word, last_prototype.utg_word)
            self.assertEqual(last_prototype.parent_id, None)


    def test_can_not_replace_onreview_word_from_another_author(self):
        for word_type in utg_relations.WORD_TYPE.records:
            parent_word = utg_words.Word.create_test_word(word_type, prefix=u'parent-')
            child_word = utg_words.Word.create_test_word(word_type, prefix=u'child-')

            parent = prototypes.WordPrototype.create(parent_word, author=self.account_2)

            requested_url = url('linguistics:words:create', type=word_type.value, parent=parent.id)

            with self.check_delta(prototypes.WordPrototype._db_count, 0):
                self.check_ajax_error(self.client.post(requested_url, helpers.get_word_post_data(child_word)),
                                      'linguistics.words.create.can_not_edit_anothers_word')

            last_prototype = prototypes.WordPrototype._db_latest()

            self.assertEqual(parent.created_at, last_prototype.created_at)
            self.assertEqual(parent_word, last_prototype.utg_word)


    def test_create__with_parent(self):
        for word_type in utg_relations.WORD_TYPE.records:
            parent_word = utg_words.Word.create_test_word(word_type, prefix=u'parent-')
            child_word = utg_words.Word.create_test_word(word_type, prefix=u'child-')

            parent = prototypes.WordPrototype.create(parent_word)
            parent.state = relations.WORD_STATE.IN_GAME
            parent.save()

            requested_url = url('linguistics:words:create', type=word_type.value, parent=parent.id)

            with self.check_delta(prototypes.WordPrototype._db_count, 1):
                response = self.client.post(requested_url, helpers.get_word_post_data(child_word))

            self.assertTrue(prototypes.WordPrototype._db_filter(id=parent.id).exists())

            last_prototype = prototypes.WordPrototype._db_latest()

            self.check_ajax_ok(response, data={'next_url': url('linguistics:words:show', last_prototype.id)})

            self.assertEqual(child_word, last_prototype.utg_word)
            self.assertEqual(last_prototype.parent_id, parent.id)


    def test_create__with_parent__full_copy(self):
        for word_type in utg_relations.WORD_TYPE.records:
            word = utg_words.Word.create_test_word(word_type)

            parent = prototypes.WordPrototype.create(word)
            parent.state = relations.WORD_STATE.IN_GAME
            parent.save()

            requested_url = url('linguistics:words:create', type=word_type.value, parent=parent.id)

            with self.check_not_changed(prototypes.WordPrototype._db_count):
                self.check_ajax_error(self.client.post(requested_url, helpers.get_word_post_data(parent.utg_word)),
                                      'linguistics.words.create.full_copy_restricted')



    def test_create__parent_not_cpecified(self):
        for word_type in utg_relations.WORD_TYPE.records:
            word = utg_words.Word.create_test_word(word_type)

            parent = prototypes.WordPrototype.create(word)
            parent.state = random.choice(relations.WORD_STATE.records)
            parent.save()

            requested_url = url('linguistics:words:create', type=word_type.value)

            with self.check_delta(prototypes.WordPrototype._db_count, 0):
                self.check_ajax_error(self.client.post(requested_url, helpers.get_word_post_data(word)),
                                      'linguistics.words.create.parent_exists')

    def test_create__copy_of_onreview__when_ingame_parent_exists(self):
        for word_type in utg_relations.WORD_TYPE.records:
            ingame_parent_word = utg_words.Word.create_test_word(word_type, prefix=u'in-game-parent-')
            onreview_parent_word = utg_words.Word.create_test_word(word_type, prefix=u'on-review-parent-')
            child_word = utg_words.Word.create_test_word(word_type, prefix=u'child-')

            ingame_parent = prototypes.WordPrototype.create(ingame_parent_word)
            ingame_parent.state = relations.WORD_STATE.IN_GAME
            ingame_parent.save()

            onreview_parent = prototypes.WordPrototype.create(onreview_parent_word, parent=ingame_parent, author=self.account_1)
            onreview_parent.state = relations.WORD_STATE.ON_REVIEW
            onreview_parent.save()

            requested_url = url('linguistics:words:create', type=word_type.value, parent=onreview_parent.id)

            with self.check_delta(prototypes.WordPrototype._db_count, 0):
                self.check_ajax_ok(self.client.post(requested_url, helpers.get_word_post_data(child_word)))

            last_prototype = prototypes.WordPrototype._db_latest()

            self.assertTrue(last_prototype.created_at > onreview_parent.created_at)

            self.assertEqual(last_prototype.parent_id, ingame_parent.id)



    def test_form_errors(self):
        for word_type in utg_relations.WORD_TYPE.records:
            requested_url = url('linguistics:words:create', type=word_type.value)

            with self.check_not_changed(prototypes.WordPrototype._db_count):
                self.check_ajax_error(self.client.post(requested_url, {}), 'linguistics.words.create.form_errors')



    def test_not_equal_types(self):
        for word_type in utg_relations.WORD_TYPE.records:
            wrong_type = random.choice(utg_relations.WORD_TYPE.records)
            while wrong_type == word_type:
                wrong_type = random.choice(utg_relations.WORD_TYPE.records)

            word = prototypes.WordPrototype.create(utg_words.Word.create_test_word(word_type, prefix=u'w-'))

            requested_url = url('linguistics:words:create', type=wrong_type.value, parent=word.id)

            self.check_ajax_error(self.client.post(requested_url, {}), 'linguistics.words.create.unequal_types')


    @mock.patch('the_tale.linguistics.prototypes.WordPrototype.has_child', lambda self: True)
    def test_has_on_review_copy(self):
        for word_type in utg_relations.WORD_TYPE.records:
            word = prototypes.WordPrototype.create(utg_words.Word.create_test_word(word_type, prefix=u'w-'))
            requested_url = url('linguistics:words:create', type=word.type.value, parent=word.id)
            self.check_ajax_error(self.client.post(requested_url, {}), 'linguistics.words.create.has_on_review_copy')



class ShowRequestsTests(BaseRequestsTests):

    def setUp(self):
        super(ShowRequestsTests, self).setUp()

        self.word_type = random.choice(utg_relations.WORD_TYPE.records)


    def test_word_errors(self):
        self.check_html_ok(self.request_html(url('linguistics:words:show', 'www')), texts=['linguistics.words.word.wrong_format'])
        self.check_html_ok(self.request_html(url('linguistics:words:show', 666)), texts=['linguistics.words.word.not_found'], status_code=404)

    def test_success__for_owner(self):
        self.request_login(self.account_1.email)

        word = prototypes.WordPrototype.create(utg_words.Word.create_test_word(self.word_type, prefix=u'w-', only_required=True), author=self.account_1)
        requested_url = url('linguistics:words:show', word.id)
        self.check_html_ok(self.request_html(requested_url), texts=[('pgf-has-child-message', 0),
                                                                    ('pgf-has-parent-message', 0),
                                                                    ('pgf-in-game-button', 0),
                                                                    ('pgf-remove-button', 1),
                                                                    ('pgf-edit-button', 1)])

    def test_success__in_game__for_owner(self):
        self.request_login(self.account_1.email)

        word = prototypes.WordPrototype.create(utg_words.Word.create_test_word(self.word_type, prefix=u'w-', only_required=True), author=self.account_1)
        word.state = relations.WORD_STATE.IN_GAME
        word.save()

        requested_url = url('linguistics:words:show', word.id)
        self.check_html_ok(self.request_html(requested_url), texts=[('pgf-has-child-message', 0),
                                                                    ('pgf-has-parent-message', 0),
                                                                    ('pgf-in-game-button', 0),
                                                                    ('pgf-remove-button', 0),
                                                                    ('pgf-edit-button', 1)])


    def test_success__unlogined(self):
        word = prototypes.WordPrototype.create(utg_words.Word.create_test_word(self.word_type, prefix=u'w-', only_required=True), author=self.account_1)
        requested_url = url('linguistics:words:show', word.id)
        self.check_html_ok(self.request_html(requested_url), texts=[('pgf-has-child-message', 0),
                                                                    ('pgf-has-parent-message', 0),
                                                                    ('pgf-in-game-button', 0),
                                                                    ('pgf-remove-button', 0),
                                                                    ('pgf-edit-button', 0)])

    def test_success__in_game(self):
        word = prototypes.WordPrototype.create(utg_words.Word.create_test_word(self.word_type, prefix=u'w-', only_required=True), author=self.account_1)
        word.state = relations.WORD_STATE.IN_GAME
        word.save()

        requested_url = url('linguistics:words:show', word.id)
        self.check_html_ok(self.request_html(requested_url), texts=[('pgf-has-child-message', 0),
                                                                    ('pgf-has-parent-message', 0),
                                                                    ('pgf-in-game-button', 0),
                                                                    ('pgf-remove-button', 0)])

    def test_moderator(self):
        word = prototypes.WordPrototype.create(utg_words.Word.create_test_word(self.word_type, prefix=u'w-', only_required=True), author=self.account_1)

        self.request_login(self.moderator.email)

        requested_url = url('linguistics:words:show', word.id)

        self.check_html_ok(self.request_html(requested_url), texts=[('pgf-in-game-button', 1),
                                                                    ('pgf-remove-button', 1)])

    def test_moderator__in_game(self):
        word = prototypes.WordPrototype.create(utg_words.Word.create_test_word(self.word_type, prefix=u'w-', only_required=True), author=self.account_1)
        word.state = relations.WORD_STATE.IN_GAME
        word.save()

        self.request_login(self.moderator.email)

        requested_url = url('linguistics:words:show', word.id)

        self.check_html_ok(self.request_html(requested_url), texts=[('pgf-in-game-button', 0),
                                                                    ('pgf-remove-button', 1)])

    def test_success__has_parent(self):
        word_1 = prototypes.WordPrototype.create(utg_words.Word.create_test_word(self.word_type, prefix=u'w-', only_required=True), author=self.account_1)
        word_1.state = relations.WORD_STATE.IN_GAME
        word_1.save()

        word_2 = prototypes.WordPrototype.create(utg_words.Word.create_test_word(self.word_type, prefix=u'w-', only_required=True),
                                                 parent=word_1)

        requested_url = url('linguistics:words:show', word_2.id)
        self.check_html_ok(self.request_html(requested_url), texts=[('pgf-has-child-message', 0),
                                                                    ('pgf-has-parent-message', 1)])

    def test_success__has_child(self):
        word_1 = prototypes.WordPrototype.create(utg_words.Word.create_test_word(self.word_type, prefix=u'w-', only_required=True), author=self.account_1)
        word_1.state = relations.WORD_STATE.IN_GAME
        word_1.save()

        prototypes.WordPrototype.create(utg_words.Word.create_test_word(self.word_type, prefix=u'w-', only_required=True),
                                        parent=word_1)

        requested_url = url('linguistics:words:show', word_1.id)
        self.check_html_ok(self.request_html(requested_url), texts=[('pgf-has-child-message', 1),
                                                                    ('pgf-has-parent-message', 0)])

    def test_displaying_fields_for_all_forms(self):
        for word_type in utg_relations.WORD_TYPE.records:
            word = prototypes.WordPrototype.create(utg_words.Word.create_test_word(word_type, prefix=u'w-', only_required=True))
            requested_url = url('linguistics:words:show', word.id)

            texts = []
            for property in utg_relations.PROPERTY_TYPE.records:
                if word.utg_word.properties.is_specified(property):
                    texts.append(word.utg_word.properties.get(property).text)

            for form in word.utg_word.forms:
                texts.append(form)

            self.check_html_ok(self.request_html(requested_url), texts=texts)

    def test_displaying_fields_words_with_optional_properties(self):
        word_type = utg_relations.WORD_TYPE.NOUN
        word = prototypes.WordPrototype.create(utg_words.Word.create_test_word(word_type,
                                                                               prefix=u'w-',
                                                                               properties=utg_words.Properties(utg_relations.NUMBER.PLURAL)))
        word.save()

        requested_url = url('linguistics:words:show', word.id)

        texts = []
        for form in word.utg_word.forms[:6]:
            texts.append((form, 0))
        for form in word.utg_word.forms[6:]:
            texts.append(form)

        self.check_html_ok(self.request_html(requested_url), texts=texts)


class RemoveRequestsTests(BaseRequestsTests):

    def setUp(self):
        super(RemoveRequestsTests, self).setUp()
        self.word_type = random.choice(utg_relations.WORD_TYPE.records)
        self.word = prototypes.WordPrototype.create(utg_words.Word.create_test_word(self.word_type, prefix=u'w-', only_required=True),
                                                    author=self.account_1)

        self.account_2 = self.accounts_factory.create_account()

        self.request_login(self.account_1.email)

        self.requested_url = url('linguistics:words:remove', self.word.id)

    def test_word_errors(self):
        with self.check_not_changed(prototypes.WordPrototype._db_count):
            self.check_ajax_error(self.client.post(url('linguistics:words:remove', 'www')), 'linguistics.words.word.wrong_format')
            self.check_ajax_error(self.client.post(url('linguistics:words:remove', 666)), 'linguistics.words.word.not_found')

    def test_login_required(self):
        self.request_logout()

        with self.check_not_changed(prototypes.WordPrototype._db_count):
            self.check_ajax_error(self.client.post(self.requested_url, {}), 'common.login_required')


    def test_moderation_rights(self):
        self.word.state = relations.WORD_STATE.IN_GAME
        self.word.save()

        with self.check_not_changed(prototypes.WordPrototype._db_count):
            self.check_ajax_error(self.client.post(self.requested_url, {}), 'linguistics.words.remove.no_rights')

    def test_ownership(self):
        self.request_login(self.account_2.email)

        with self.check_not_changed(prototypes.WordPrototype._db_count):
            self.check_ajax_error(self.client.post(self.requested_url, {}), 'linguistics.words.remove.no_rights')

        self.word.state = relations.WORD_STATE.IN_GAME
        self.word.save()

        with self.check_not_changed(prototypes.WordPrototype._db_count):
            self.check_ajax_error(self.client.post(self.requested_url, {}), 'linguistics.words.remove.no_rights')


    def test_remove(self):
        self.request_login(self.moderator.email)

        with self.check_delta(prototypes.WordPrototype._db_count, -1):
            self.check_ajax_ok(self.client.post(self.requested_url))


    def test_remove_contributions(self):
        self.request_login(self.moderator.email)

        contribution_1 = prototypes.ContributionPrototype.create(type=relations.CONTRIBUTION_TYPE.WORD,
                                                                 account_id=self.account_1.id,
                                                                 entity_id=self.word.id,
                                                                 source=relations.CONTRIBUTION_SOURCE.PLAYER,
                                                                 state=relations.CONTRIBUTION_STATE.ON_REVIEW)

        contribution_2 = prototypes.ContributionPrototype.create(type=relations.CONTRIBUTION_TYPE.WORD,
                                                                 account_id=self.account_2.id,
                                                                 entity_id=self.word.id,
                                                                 source=relations.CONTRIBUTION_SOURCE.PLAYER,
                                                                 state=relations.CONTRIBUTION_STATE.IN_GAME)

        with self.check_delta(prototypes.WordPrototype._db_count, -1):
            self.check_ajax_ok(self.client.post(self.requested_url))

        self.assertFalse(prototypes.ContributionPrototype._db_filter(id=contribution_1.id).exists())
        self.assertTrue(prototypes.ContributionPrototype._db_filter(id=contribution_2.id).exists())

    def test_remove__by_ownership(self):
        self.request_login(self.account_1.email)

        self.word.state = relations.WORD_STATE.IN_GAME
        self.word.save()

        with self.check_not_changed(prototypes.WordPrototype._db_count):
            self.check_ajax_error(self.client.post(self.requested_url, {}), 'linguistics.words.remove.no_rights')

        self.word.state = relations.WORD_STATE.ON_REVIEW
        self.word.save()

        with self.check_delta(prototypes.WordPrototype._db_count, -1):
            self.check_ajax_ok(self.client.post(self.requested_url))



class InGameRequestsTests(BaseRequestsTests):

    def setUp(self):
        super(InGameRequestsTests, self).setUp()
        self.word_type = random.choice(utg_relations.WORD_TYPE.records)
        self.word = prototypes.WordPrototype.create(utg_words.Word.create_test_word(self.word_type, prefix=u'w-', only_required=True),
                                                    author=self.account_1)

        self.author_contribution = prototypes.ContributionPrototype.create(type=relations.CONTRIBUTION_TYPE.WORD,
                                                                           account_id=self.account_1.id,
                                                                           entity_id=self.word.id,
                                                                           source=relations.CONTRIBUTION_SOURCE.PLAYER,
                                                                           state=self.word.state.contribution_state)


        self.request_login(self.account_1.email)

        self.requested_url = url('linguistics:words:in-game', self.word.id)

    def test_word_errors(self):
        with self.check_not_changed(prototypes.WordPrototype._db_filter(state=relations.WORD_STATE.ON_REVIEW).count):
            self.check_ajax_error(self.client.post(url('linguistics:words:in-game', 'www')), 'linguistics.words.word.wrong_format')
            self.check_ajax_error(self.client.post(url('linguistics:words:in-game', 666)), 'linguistics.words.word.not_found')

    def test_login_required(self):
        self.request_logout()

        with self.check_not_changed(prototypes.WordPrototype._db_filter(state=relations.WORD_STATE.ON_REVIEW).count):
            self.check_ajax_error(self.client.post(self.requested_url, {}), 'common.login_required')


    def test_moderation_rights(self):
        with self.check_not_changed(prototypes.WordPrototype._db_filter(state=relations.WORD_STATE.ON_REVIEW).count):
            self.check_ajax_error(self.client.post(self.requested_url, {}), 'linguistics.words.moderation_rights')


    def test_already_in_game(self):
        self.request_login(self.moderator.email)

        self.word.state = relations.WORD_STATE.IN_GAME
        self.word.save()

        with self.check_not_changed(prototypes.ContributionPrototype._db_count):
            with self.check_not_changed(prototypes.WordPrototype._db_filter(state=relations.WORD_STATE.IN_GAME).count):
                with self.check_not_changed(prototypes.WordPrototype._db_filter(state=relations.WORD_STATE.ON_REVIEW).count):
                    self.check_ajax_ok(self.client.post(self.requested_url))


    def test_in_game(self):
        self.request_login(self.moderator.email)

        self.assertTrue(self.word.state.is_ON_REVIEW)

        with self.check_not_changed(prototypes.ContributionPrototype._db_count):
            with self.check_delta(prototypes.WordPrototype._db_filter(state=relations.WORD_STATE.IN_GAME).count, 1):
                with self.check_delta(prototypes.WordPrototype._db_filter(state=relations.WORD_STATE.ON_REVIEW).count, -1):
                    self.check_ajax_ok(self.client.post(self.requested_url))

        self.word.reload()

        last_contribution = prototypes.ContributionPrototype._db_latest()

        self.assertTrue(last_contribution.type.is_WORD)
        self.assertEqual(last_contribution.account_id, self.word.author_id)
        self.assertEqual(last_contribution.entity_id, self.word.id)

        self.assertTrue(self.word.state.is_IN_GAME)


    def test_in_game__author_not_moderator(self):
        self.request_login(self.moderator.email)
        self.check_ajax_ok(self.client.post(self.requested_url))

        last_contribution = prototypes.ContributionPrototype._db_latest()
        self.assertTrue(last_contribution.source.is_PLAYER)


    def test_in_game__no_parent_but_equal_word_already_in_game(self):
        self.request_login(self.moderator.email)

        self.word.state = relations.WORD_STATE.IN_GAME
        self.word.save()

        word_2 = prototypes.WordPrototype.create(utg_words.Word.create_test_word(self.word_type, prefix=u'w-', only_required=True))

        self.assertEqual(self.word.utg_word.normal_form(), word_2.utg_word.normal_form())

        with self.check_not_changed(prototypes.WordPrototype._db_filter(state=relations.WORD_STATE.IN_GAME).count):
            with self.check_not_changed(prototypes.WordPrototype._db_filter(state=relations.WORD_STATE.ON_REVIEW).count):
                with self.check_not_changed(prototypes.WordPrototype._db_count):
                    self.check_ajax_error(self.client.post(url('linguistics:words:in-game', word_2.id)),
                                          'linguistics.words.in_game.conflict_with_not_parent')

        word_2.reload()

        self.assertNotEqual(prototypes.WordPrototype.get_by_id(self.word.id), None)
        self.assertTrue(word_2.state.is_ON_REVIEW)

    def test_in_game__has_parent(self):
        self.request_login(self.moderator.email)

        self.word.state = relations.WORD_STATE.IN_GAME
        self.word.save()

        word_2 = prototypes.WordPrototype.create(utg_words.Word.create_test_word(self.word_type, prefix=u'w-', only_required=True),
                                                 parent=self.word,
                                                 author=self.account_1)

        with self.check_not_changed(prototypes.WordPrototype._db_filter(state=relations.WORD_STATE.IN_GAME).count):
            with self.check_delta(prototypes.WordPrototype._db_filter(state=relations.WORD_STATE.ON_REVIEW).count, -1):
                with self.check_delta(prototypes.WordPrototype._db_count, -1):
                    self.check_ajax_ok(self.client.post(url('linguistics:words:in-game', word_2.id)))

        word_2.reload()

        self.assertEqual(prototypes.WordPrototype.get_by_id(self.word.id), None)
        self.assertTrue(word_2.state.is_IN_GAME)


    def test_in_game__has_parent__with_contributors(self):
        result, account_id, bundle_id = register_user('account_2', 'account_2@test.com', '111111')
        account_2 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('account_3', 'account_3@test.com', '111111')
        account_3 = AccountPrototype.get_by_id(account_id)

        self.request_login(self.moderator.email)

        self.word.state = relations.WORD_STATE.IN_GAME
        self.word.save()

        prototypes.ContributionPrototype.create(type=relations.CONTRIBUTION_TYPE.WORD,
                                                account_id=account_3.id,
                                                entity_id=self.word.id,
                                                source=relations.CONTRIBUTION_SOURCE.random(),
                                                state=self.word.state.contribution_state)


        word_2 = prototypes.WordPrototype.create(utg_words.Word.create_test_word(self.word_type, prefix=u'w-', only_required=True),
                                                 parent=self.word,
                                                 author=account_2)


        with self.check_delta(prototypes.ContributionPrototype._db_filter(entity_id=self.word.id).count, -2):
            with self.check_delta(prototypes.ContributionPrototype._db_filter(entity_id=word_2.id).count, 2):
                with self.check_delta(prototypes.WordPrototype._db_count, -1):
                    self.check_ajax_ok(self.client.post(url('linguistics:words:in-game', word_2.id)))

        self.assertEqual(prototypes.ContributionPrototype._db_filter(type=relations.CONTRIBUTION_TYPE.WORD, entity_id=self.word.id).count(), 0)
        self.assertEqual(prototypes.ContributionPrototype._db_filter(type=relations.CONTRIBUTION_TYPE.WORD, entity_id=word_2.id, state=relations.CONTRIBUTION_STATE.IN_GAME).count(), 2)
        self.assertEqual(set(prototypes.ContributionPrototype._db_filter(type=relations.CONTRIBUTION_TYPE.WORD).values_list('account_id', flat=True)),
                         set([self.account_1.id, account_3.id]))

        word_2.reload()

        self.assertEqual(prototypes.WordPrototype.get_by_id(self.word.id), None)
        self.assertTrue(word_2.state.is_IN_GAME)


    def test_in_game__has_parent__with_intersected_contributors(self):
        result, account_id, bundle_id = register_user('account_2', 'account_2@test.com', '111111')
        account_2 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('account_3', 'account_3@test.com', '111111')
        account_3 = AccountPrototype.get_by_id(account_id)

        self.request_login(self.moderator.email)

        self.word.state = relations.WORD_STATE.IN_GAME
        self.word.save()

        contribution_2 = prototypes.ContributionPrototype.create(type=relations.CONTRIBUTION_TYPE.WORD,
                                                                 account_id=account_3.id,
                                                                 entity_id=self.word.id,
                                                                 source=relations.CONTRIBUTION_SOURCE.random(),
                                                                 state=self.word.state.contribution_state)


        word_2 = prototypes.WordPrototype.create(utg_words.Word.create_test_word(self.word_type, prefix=u'w-', only_required=True),
                                                 parent=self.word,
                                                 author=account_2)

        contribution_3 = prototypes.ContributionPrototype.create(type=relations.CONTRIBUTION_TYPE.WORD,
                                                                 account_id=self.account_1.id,
                                                                 entity_id=word_2.id,
                                                                 source=relations.CONTRIBUTION_SOURCE.PLAYER,
                                                                 state=word_2.state.contribution_state)


        with self.check_delta(prototypes.ContributionPrototype._db_filter().count, -1):
            with self.check_delta(prototypes.ContributionPrototype._db_filter(entity_id=self.word.id).count, -2):
                with self.check_delta(prototypes.ContributionPrototype._db_filter(entity_id=word_2.id).count, 1):
                    with self.check_delta(prototypes.WordPrototype._db_count, -1):
                        self.check_ajax_ok(self.client.post(url('linguistics:words:in-game', word_2.id)))

        self.assertEqual(prototypes.ContributionPrototype._db_filter(type=relations.CONTRIBUTION_TYPE.WORD, entity_id=self.word.id).count(), 0)
        self.assertEqual(prototypes.ContributionPrototype._db_filter(type=relations.CONTRIBUTION_TYPE.WORD, entity_id=word_2.id, state=relations.CONTRIBUTION_STATE.IN_GAME).count(), 2)
        self.assertEqual(set(prototypes.ContributionPrototype._db_filter(type=relations.CONTRIBUTION_TYPE.WORD).values_list('account_id', flat=True)),
                         set([self.account_1.id, account_3.id]))
        self.assertEqual(set(prototypes.ContributionPrototype._db_filter(type=relations.CONTRIBUTION_TYPE.WORD).values_list('id', flat=True)),
                         set([self.author_contribution.id, contribution_2.id]))

        word_2.reload()

        self.assertEqual(prototypes.WordPrototype.get_by_id(self.word.id), None)
        self.assertTrue(word_2.state.is_IN_GAME)


class DictionaryOperationsTests(BaseRequestsTests):

    def test_normal_user(self):
        self.request_login(self.account_1.email)
        self.check_html_ok(self.request_html(url('linguistics:words:dictionary-operations')), texts=[('pgf-dictionary-load-form', 0)])

    def test_moderator(self):
        self.request_login(self.moderator.email)
        self.check_html_ok(self.request_html(url('linguistics:words:dictionary-operations')), texts=[('pgf-dictionary-load-form', 0)])

    def test_superuser(self):
        superuser = self.accounts_factory.create_account(is_superuser=True)
        self.request_login(superuser.email)
        self.check_html_ok(self.request_html(url('linguistics:words:dictionary-operations')), texts=['pgf-dictionary-load-form'])


class DictionaryDownloadTests(BaseRequestsTests):

    def test_download(self):
        word_type = relations.ALLOWED_WORD_TYPE.random().utg_type

        parent_word = utg_words.Word.create_test_word(word_type, prefix=u'parent-')
        child_word = utg_words.Word.create_test_word(word_type, prefix=u'child-')
        ingame_word = utg_words.Word.create_test_word(word_type, prefix=u'ingame-')
        outgame_word = utg_words.Word.create_test_word(word_type, prefix=u'outgame-')

        parent = prototypes.WordPrototype.create(parent_word)
        parent.state = relations.WORD_STATE.IN_GAME
        parent.save()

        prototypes.WordPrototype.create(child_word, parent=parent) # child

        ingame = prototypes.WordPrototype.create(ingame_word)
        ingame.state = relations.WORD_STATE.IN_GAME
        ingame.save()

        prototypes.WordPrototype.create(outgame_word) # outgame

        response = self.client.get(url('linguistics:words:dictionary-download'))

        data = s11n.from_json(response.content)

        self.assertEqual(len(data['words']), 2)
        self.assertIn(parent.utg_word.serialize(), data['words'])
        self.assertIn(ingame.utg_word.serialize(), data['words'])


class DictionaryLoadTests(BaseRequestsTests):

    def setUp(self):
        super(DictionaryLoadTests, self).setUp()

        word_type = relations.ALLOWED_WORD_TYPE.random().utg_type

        self.parent_word = utg_words.Word.create_test_word(word_type, prefix=u'parent-')
        self.child_word = utg_words.Word.create_test_word(word_type, prefix=u'child-')
        self.ingame_word = utg_words.Word.create_test_word(word_type, prefix=u'ingame-')
        self.outgame_word = utg_words.Word.create_test_word(word_type, prefix=u'outgame-')
        self.not_removed_word = utg_words.Word.create_test_word(word_type, prefix=u'not_removed-')

        self.parent = prototypes.WordPrototype.create(self.parent_word)
        self.parent.state = relations.WORD_STATE.IN_GAME
        self.parent.save()

        self.child = prototypes.WordPrototype.create(self.child_word, parent=self.parent)

        self.ingame = prototypes.WordPrototype.create(self.ingame_word)
        self.ingame.state = relations.WORD_STATE.IN_GAME
        self.ingame.save()

        self.outgame = prototypes.WordPrototype.create(self.outgame_word)

        self.not_removed = prototypes.WordPrototype.create(self.not_removed_word)

        self.requested_url = url('linguistics:words:dictionary-load')

        self.superuser = self.accounts_factory.create_account(is_superuser=True)

    def test_login_required(self):
        self.check_ajax_error(self.client.post(self.requested_url, {}), 'common.login_required')

    def test_superuser_required(self):
        self.request_login(self.moderator.email)
        self.check_ajax_error(self.client.post(self.requested_url, {}), 'common.superuser_required')

    def test_form_errors(self):
        self.request_login(self.superuser.email)
        self.check_ajax_error(self.client.post(self.requested_url, {}), 'linguistics.words.load_dictionary.form_errors')

    def test_load(self):
        self.request_login(self.superuser.email)

        self.parent_word.forms[1] = '1'
        self.ingame_word.forms[1] = '2'
        self.outgame_word.forms[1] = '3'

        data = {'words': [self.parent_word.serialize(),
                          self.ingame_word.serialize(),
                          self.outgame_word.serialize()]}

        with self.check_changed(lambda: storage.game_dictionary.version):
            self.check_ajax_ok(self.client.post(self.requested_url, {'words': s11n.to_json(data)}))

        self.assertFalse(prototypes.WordPrototype._db_filter(id__in=[self.parent.id, self.child.id, self.ingame.id, self.outgame.id]).exists())
        self.assertTrue(prototypes.WordPrototype._db_filter(id=self.not_removed.id).exists())

        self.assertTrue(storage.game_dictionary.item.has_word('1'))
        self.assertTrue(storage.game_dictionary.item.has_word('2'))
        self.assertTrue(storage.game_dictionary.item.has_word('3'))


    def test_load__removed_only_by_normal_form(self):
        self.request_login(self.superuser.email)

        self.parent_word.forms[0] = '1'
        self.ingame_word.forms[0] = '2'
        self.outgame_word.forms[0] = '3'

        data = {'words': [self.parent_word.serialize(),
                          self.ingame_word.serialize(),
                          self.outgame_word.serialize()]}

        with self.check_changed(lambda: storage.game_dictionary.version):
            self.check_ajax_ok(self.client.post(self.requested_url, {'words': s11n.to_json(data)}))

        self.assertEqual(prototypes.WordPrototype._db_count(), 8)

        self.assertTrue(storage.game_dictionary.item.has_word('1'))
        self.assertTrue(storage.game_dictionary.item.has_word('2'))
        self.assertTrue(storage.game_dictionary.item.has_word('3'))


    def test_load__removed_by_child(self):
        self.request_login(self.superuser.email)

        data = {'words': [self.child_word.serialize()]}

        with self.check_changed(lambda: storage.game_dictionary.version):
            self.check_ajax_ok(self.client.post(self.requested_url, {'words': s11n.to_json(data)}))

        self.assertFalse(prototypes.WordPrototype._db_filter(id__in=[self.parent.id, self.child.id]).exists())
