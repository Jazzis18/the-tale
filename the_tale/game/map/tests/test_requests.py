# coding: utf-8
import jinja2
import datetime

import mock

from django.test import client
from django.core.urlresolvers import reverse

from dext.common.utils.urls import url

from the_tale.common.utils.testcase import TestCase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user

from the_tale.game import names

from the_tale.game.logic import create_test_map

from the_tale.game.chronicle.prototypes import RecordPrototype as ChronicleRecordPrototype

from the_tale.game.persons import logic as persons_logic

from the_tale.game.places import modifiers as places_modifiers
from the_tale.game.places.prototypes import BuildingPrototype
from the_tale.game.places import conf as places_conf
from the_tale.game.places import logic as places_logic

from the_tale.game.map.conf import map_settings


# class RequestsTestsBase(TestCase):
#     def setUp(self):
#         super(RequestsTestsBase, self).setUp()
#         self.place_1, self.place_2, self.place_3 = create_test_map()

#         persons_logic.sync_social_connections()

#         result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

#         self.account = AccountPrototype.get_by_id(account_id)

#         self.client = client.Client()
#         self.request_login('test_user@test.com')


# class IndexTests(RequestsTestsBase):

#     def test_success(self):
#         self.check_html_ok(self.request_html(reverse('game:map:')))


# class CellInfoTests(RequestsTestsBase):

#     def test_place_info_logined(self):
#         self.check_html_ok(self.request_html(reverse('game:map:cell-info') + '?x=2&y=3'), texts=[])

#     def test_place_info_no_modifier(self):
#         texts = [('pgf-current-modifier-marker', 0)] + [(modifier.text, 1) for modifier in places_modifiers.CITY_MODIFIERS.records]
#         self.check_html_ok(self.request_html(reverse('game:map:cell-info') + ('?x=%d&y=%d' % (self.place_1.x, self.place_1.y))), texts=texts)

#     def test_place_info_modifier(self):
#         self.place_1.set_modifier(places_modifiers.CITY_MODIFIERS.TRADE_CENTER)
#         places_logic.save_place(self.place_1)

#         texts = [('pgf-current-modifier-marker', 1)]

#         self.check_html_ok(self.request_html(reverse('game:map:cell-info') + ('?x=%d&y=%d' % (self.place_1.x, self.place_1.y))), texts=texts)

#     def test_place_info_no_freeze_time_icon(self):
#         for person in self.place_1.persons:
#             person.created_at = datetime.datetime(2000, 1, 1)
#             persons_logic.save_person(person)
#         texts = [('pgf-time-before-unfreeze', 0)]
#         self.check_html_ok(self.request_html(reverse('game:map:cell-info') + ('?x=%d&y=%d' % (self.place_1.x, self.place_1.y))), texts=texts)

#     def test_place_info_freeze_time_icon(self):
#         texts = [('pgf-time-before-unfreeze', 1)]
#         person = self.place_1.persons[0]
#         person.created_at = datetime.datetime(2000, 1, 1)
#         persons_logic.save_person(person)
#         self.check_html_ok(self.request_html(reverse('game:map:cell-info') + ('?x=%d&y=%d' % (self.place_1.x, self.place_1.y))), texts=texts)

#     def test_place_new_place_message(self):
#         self.assertTrue(self.place_1.is_new)
#         self.check_html_ok(self.request_html(reverse('game:map:cell-info') + ('?x=%d&y=%d' % (self.place_1.x, self.place_1.y))), texts=['pgf-new-place-message'])

#     def test_place_new_place_message__not_new(self):
#         self.place_1.created_at -= datetime.timedelta(seconds=places_conf.places_settings.NEW_PLACE_LIVETIME)
#         places_logic.save_place(self.place_1)
#         self.check_html_ok(self.request_html(reverse('game:map:cell-info') + ('?x=%d&y=%d' % (self.place_1.x, self.place_1.y))), texts=[('pgf-new-place-message', 0)])

#     @mock.patch('the_tale.game.places.objects.Place.is_frontier', True)
#     def test_place_frontier_message(self):
#         self.check_html_ok(self.request_html(reverse('game:map:cell-info') + ('?x=%d&y=%d' % (self.place_1.x, self.place_1.y))), texts=['pgf-frontier-message'])

#     @mock.patch('the_tale.game.places.objects.Place.is_frontier', False)
#     def test_place_frontier_message__not_new(self):
#         self.check_html_ok(self.request_html(reverse('game:map:cell-info') + ('?x=%d&y=%d' % (self.place_1.x, self.place_1.y))), texts=[('pgf-frontier-message', 0)])


#     def test_place_chronicle(self):
#         texts = [jinja2.escape(record.text) for record in ChronicleRecordPrototype.get_last_actor_records(self.place_1, 1000)]
#         self.check_html_ok(self.request_html(reverse('game:map:cell-info') + ('?x=%d&y=%d' % (self.place_1.x, self.place_1.y))), texts=texts)

#     def test_building(self):
#         building = BuildingPrototype.create(self.place_1.persons[0], utg_name=names.generator.get_test_name('building-name'))
#         texts = [building.type.text, jinja2.escape(building.person.name), jinja2.escape(self.place_1.name)]
#         self.check_html_ok(self.request_html(reverse('game:map:cell-info') + ('?x=%d&y=%d' % (building.x, building.y))), texts=texts)

#     def test_outside_map(self):
#         self.check_html_ok(self.request_html(url('game:map:cell-info', x=0, y=0)), texts=[('outside_map', 0)])
#         self.check_html_ok(self.request_html(url('game:map:cell-info', x=map_settings.WIDTH-1, y=map_settings.HEIGHT-1)), texts=[('outside_map', 0)])

#         self.check_html_ok(self.request_html(url('game:map:cell-info', x=-1, y=0)), texts=[('outside_map', 1)])
#         self.check_html_ok(self.request_html(url('game:map:cell-info', x=0, y=-1)), texts=[('outside_map', 1)])
#         self.check_html_ok(self.request_html(url('game:map:cell-info', x=map_settings.WIDTH, y=map_settings.HEIGHT-1)), texts=[('outside_map', 1)])
#         self.check_html_ok(self.request_html(url('game:map:cell-info', x=map_settings.WIDTH-1, y=map_settings.HEIGHT)), texts=[('outside_map', 1)])
