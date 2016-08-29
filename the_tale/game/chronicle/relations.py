# coding: utf-8

from rels import Column
from rels.django import DjangoEnum


class RECORD_TYPE(DjangoEnum):
    deprecated = Column(unique=False)

    records = ( ('PLACE_CHANGE_NAME_BILL_STARTED', 0, u'название города: предложен закон об изменении', True),
                ('PLACE_CHANGE_NAME_BILL_SUCCESSED', 1, u'название города: принят закон об изменении', False),
                ('PLACE_CHANGE_NAME_BILL_FAILED', 2, u'название города: отклонён закон об изменении', True),

                ('PLACE_CHANGE_DESCRIPTION_BILL_STARTED', 3, u'описание города: предложен закон об изменении', True),
                ('PLACE_CHANGE_DESCRIPTION_BILL_SUCCESSED', 4, u'описание города: принят закон об изменении', False),
                ('PLACE_CHANGE_DESCRIPTION_BILL_FAILED', 5, u'описание города: отклонён закон об изменении', True),

                ('PLACE_CHANGE_MODIFIER_BILL_STARTED', 6, u'специализация города: предложен закон об изменении', True),
                ('PLACE_CHANGE_MODIFIER_BILL_SUCCESSED', 7, u'специализация города: принят закон об изменении', False),
                ('PLACE_CHANGE_MODIFIER_BILL_FAILED', 8, u'специализация города: отклонён закон об изменении', True),

                ('PLACE_LOSED_MODIFIER', 9, u'специализация города: утеряна из-за недостатка развития', True),

                ('PERSON_REMOVE_BILL_STARTED', 10, u'житель: предложен закон об изгнании', True),
                ('PERSON_REMOVE_BILL_SUCCESSED', 11, u'житель: принят закон об изгнании', True),
                ('PERSON_REMOVE_BILL_FAILED', 12, u'житель: отклонён закон об изгнании', True),
                ('PERSON_LEFT_PLACE', 13, u'житель: покину место из-за потери влияния', True),

                ('PERSON_ARRIVED_TO_PLACE', 14, u'житель: приехал в город', False),

                ('PLACE_CHANGE_RACE', 15, u'раса города: изменение основной расы', False),

                ('BUILDING_CREATE_BILL_STARTED', 16, u'строение: предложен закон о возведении ', True),
                ('BUILDING_CREATE_BILL_SUCCESSED', 17, u'строение: принят закон о возведении', False),
                ('BUILDING_CREATE_BILL_FAILED', 18, u'строение: отклонён закон о возведении', True),

                ('BUILDING_DESTROY_BILL_STARTED', 19, u'строение: предложен закон об удалении ', True),
                ('BUILDING_DESTROY_BILL_SUCCESSED', 20, u'строение: принят закон об удалении', False),
                ('BUILDING_DESTROY_BILL_FAILED', 21, u'строение: отклонён закон об удалении', True),

                ('BUILDING_DESTROYED_BY_AMORTIZATION', 22, u'строение: разрушено из-за амортизации', True),

                ('BUILDING_RENAMING_BILL_STARTED', 23, u'строение: предложен закон о переименовании ', True),
                ('BUILDING_RENAMING_BILL_SUCCESSED', 24, u'строение: принят закон о переименовании', False),
                ('BUILDING_RENAMING_BILL_FAILED', 25, u'строение: отклонён закон о переименовании', True),

                ('PLACE_RESOURCE_EXCHANGE_BILL_STARTED', 26, u'обмен ресурсами: предложен закон', True),
                ('PLACE_RESOURCE_EXCHANGE_BILL_SUCCESSED', 27, u'обмен ресурсами: принят закон', False),
                ('PLACE_RESOURCE_EXCHANGE_BILL_FAILED', 28, u'обмен ресурсами: отклонён закон', True),

                ('BILL_DECLINE_BILL_STARTED', 29, u'отмена закона: предложен закон', True),
                ('BILL_DECLINE_BILL_SUCCESSED', 30, u'отмена закона: принят закон', False),
                ('BILL_DECLINE_BILL_FAILED', 31, u'отмена закона: отклонён закон', True),

                ('PLACE_RESOURCE_EXCHANGE_BILL_ENDED', 32, u'обмен ресурсами: действие закона окончено', True),

                ('PLACE_RESOURCE_CONVERSION_BILL_STARTED', 33, u'изменение параметров города: предложен закон', True),
                ('PLACE_RESOURCE_CONVERSION_BILL_SUCCESSED', 34, u'изменение параметров города: принят закон', False),
                ('PLACE_RESOURCE_CONVERSION_BILL_FAILED', 35, u'изменение параметров города: отклонён закон', True),
                ('PLACE_RESOURCE_CONVERSION_BILL_ENDED', 36, u'оизменение параметров города: действие закона окончено', True),

                ('PERSON_CHRONICLE_BILL_SUCCESSED', 37, u'житель: принят закон о занесении записи в летопись', False),
                ('PLACE_CHRONICLE_BILL_SUCCESSED', 38, u'город: принят закон о занесении записи в летопись', False),

                ('PERSON_MOVE_TO_PLACE', 39, u'житель: переехал в другой город', False),
              )


class ACTOR_ROLE(DjangoEnum):

    records = ( ('BILL', 0, u'закон'),
                ('PLACE', 1, u'город'),
                ('PERSON', 2, u'житель') )


class ACTOR_TYPE(DjangoEnum):

    records = ( ('BILL', 0, u'закон'),
                ('PLACE', 1, u'город'),
                ('PERSON', 2, u'житель') )
