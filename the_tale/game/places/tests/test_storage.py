# coding: utf-8
import uuid
import random

from the_tale.common.utils import testcase

from dext.settings import settings
from dext.common.utils import s11n

from the_tale.game import names

from the_tale.game.logic import create_test_map

from the_tale.game.places.models import Place
from the_tale.game.places import storage
from the_tale.game.places.prototypes import ResourceExchangePrototype
from the_tale.game.places.relations import RESOURCE_EXCHANGE_TYPE
from the_tale.game.places import exceptions

class PlacesStorageTest(testcase.TestCase):

    def setUp(self):
        super(PlacesStorageTest, self).setUp()
        self.p1, self.p2, self.p3 = create_test_map()
        self.storage = storage.PlacesStorage()
        self.storage.sync()

    def test_initialization(self):
        _storage = storage.PlacesStorage()
        self.assertEqual(_storage._data, {})
        self.assertEqual(_storage._version, None)

    def test_sync(self):
        self.assertEqual(len(self.storage._data), 3)
        self.assertTrue(self.storage._version > 0)

        self.assertNotEqual(self.p1.attrs.size, 7)

        place = Place.objects.get(id=self.p1.id)
        data = s11n.from_json(place.data)
        data['attributes']['size'] = 7
        place.data = s11n.to_json(data)
        place.save()

        self.storage.sync()
        self.assertNotEqual(self.storage[self.p1.id].attrs.size, 7)

        self.storage.sync(force=True)
        self.assertEqual(self.storage[self.p1.id].attrs.size, 7)

    def test_sync_after_settings_update(self):
        self.assertEqual(len(self.storage._data), 3)
        self.assertTrue(self.storage._version > 0)

        self.assertNotEqual(self.p1.attrs.size, 7)

        place = Place.objects.get(id=self.p1.id)
        data = s11n.from_json(place.data)
        data['attributes']['size'] = 7
        place.data = s11n.to_json(data)
        place.save()

        self.storage.sync()
        self.assertNotEqual(self.storage[self.p1.id].attrs.size, 7)

        settings[self.storage.SETTINGS_KEY] = uuid.uuid4().hex

        self.storage.sync()
        self.assertEqual(self.storage[self.p1.id].attrs.size, 7)


    def test_getitem_wrong_id(self):
        self.assertRaises(exceptions.PlacesStorageError, self.storage.__getitem__, 666)

    def test_getitem(self):
        self.assertEqual(self.storage[self.p1.id].id, self.p1.id)

    def test_get(self):
        self.assertEqual(self.storage.get(666, self.p2).id, self.p2.id)
        self.assertEqual(self.storage.get(self.p3.id, self.p1).id, self.p3.id)

    def test_all(self):
        self.assertEqual(len(self.storage.all()), 3)

    def test_random_place(self):
        places = set([self.p1.id, self.p2.id, self.p3.id])

        for i in xrange(100):
            places.discard(self.storage.random_place().id)

        self.assertFalse(places)

    def test_contains(self):
        self.assertTrue(self.p1.id in self.storage)
        self.assertFalse(666 in self.storage)



class ResourceExchangeStorageTests(testcase.TestCase):

    def setUp(self):
        super(ResourceExchangeStorageTests, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

        self.resource_1 = random.choice(RESOURCE_EXCHANGE_TYPE.records)
        self.resource_2 = random.choice(RESOURCE_EXCHANGE_TYPE.records)

    def test_create(self):
        self.assertEqual(len(storage.resource_exchanges.all()), 0)

        old_version = storage.resource_exchanges._version

        exchange = ResourceExchangePrototype.create(place_1=self.place_1,
                                                    place_2=self.place_2,
                                                    resource_1=self.resource_1,
                                                    resource_2=self.resource_2,
                                                    bill=None)

        self.assertEqual(len(storage.resource_exchanges.all()), 1)

        self.assertEqual(exchange.id, storage.resource_exchanges.all()[0].id)
        self.assertNotEqual(old_version, storage.resource_exchanges._version)

    def test_get_exchanges_for_place__no(self):
        self.assertEqual(storage.resource_exchanges.get_exchanges_for_place(self.place_2), [])

    def test_get_exchanges_for_place__multiple(self):
        exchange_1 = ResourceExchangePrototype.create(place_1=self.place_1,
                                                      place_2=self.place_2,
                                                      resource_1=self.resource_1,
                                                      resource_2=self.resource_2,
                                                      bill=None)

        ResourceExchangePrototype.create(place_1=self.place_1,
                                         place_2=self.place_3,
                                         resource_1=self.resource_1,
                                         resource_2=self.resource_2,
                                         bill=None)

        exchange_3 = ResourceExchangePrototype.create(place_1=self.place_2,
                                                      place_2=self.place_3,
                                                      resource_1=self.resource_1,
                                                      resource_2=self.resource_2,
                                                      bill=None)

        self.assertEqual(set(exchange.id for exchange in storage.resource_exchanges.get_exchanges_for_place(self.place_2)),
                         set((exchange_1.id, exchange_3.id)))


    def test_get_exchanges_for_bill_id_no(self):
        self.assertEqual(storage.resource_exchanges.get_exchange_for_bill_id(666), None)

    def test_get_exchanges_for_bill_id__exists(self):
        from the_tale.accounts.prototypes import AccountPrototype
        from the_tale.accounts.logic import register_user

        from the_tale.forum.models import Category, SubCategory
        from the_tale.game.bills.conf import bills_settings
        from the_tale.game.bills import bills
        from the_tale.game.bills.prototypes import BillPrototype

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        account = AccountPrototype.get_by_id(account_id)

        forum_category = Category.objects.create(caption='category-1', slug='category-1')
        SubCategory.objects.create(caption=bills_settings.FORUM_CATEGORY_UID + '-caption',
                                   uid=bills_settings.FORUM_CATEGORY_UID,
                                   category=forum_category)

        bill_data = bills.PlaceRenaming(place_id=self.place_1.id, name_forms=names.generator.get_test_name('new_name'))
        bill = BillPrototype.create(account, 'bill-caption', 'bill-rationale', bill_data, chronicle_on_accepted='chronicle-on-accepted')

        ResourceExchangePrototype.create(place_1=self.place_1,
                                         place_2=self.place_2,
                                         resource_1=self.resource_1,
                                         resource_2=self.resource_2,
                                         bill=None)

        exchange_2 = ResourceExchangePrototype.create(place_1=self.place_1,
                                                      place_2=self.place_3,
                                                      resource_1=self.resource_1,
                                                      resource_2=self.resource_2,
                                                      bill=bill)

        ResourceExchangePrototype.create(place_1=self.place_2,
                                         place_2=self.place_3,
                                         resource_1=self.resource_1,
                                         resource_2=self.resource_2,
                                         bill=None)

        self.assertEqual(exchange_2.id, storage.resource_exchanges.get_exchange_for_bill_id(bill.id).id)
