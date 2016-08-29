# coding: utf-8

from rels.django import DjangoEnum

from dext.common.utils import views as dext_views
from dext.common.utils.urls import UrlBuilder, url

from the_tale import amqp_environment

from the_tale.common.postponed_tasks.prototypes import PostponedTaskPrototype

from the_tale.common.utils import api
from the_tale.common.utils import list_filter
from the_tale.common.utils import views as utils_views

from the_tale.accounts import views as accounts_views

from the_tale.game.heroes import views as heroes_views
from the_tale.game.heroes import postponed_tasks as heroes_postponed_tasks

from the_tale.game.cards import relations
from the_tale.game.cards import effects
from the_tale.game.cards import conf


########################################
# processors definition
########################################

class AccountCardProcessor(dext_views.ArgumentProcessor):
    ERROR_MESSAGE = u'У Вас нет такой карты'
    GET_NAME = 'card'
    CONTEXT_NAME = 'account_card'

    def parse(self, context, raw_value):
        try:
            card_uid = int(raw_value)
        except ValueError:
            self.raise_wrong_format()

        if not context.account_hero.cards.has_card(card_uid=card_uid):
            self.raise_wrong_value()

        return context.account_hero.cards.get_card(card_uid)


class AccountCardsProcessor(dext_views.ArgumentProcessor):
    ERROR_MESSAGE = u'У вас нет как минимум одной из указанных карт'
    GET_NAME = 'cards'
    CONTEXT_NAME = 'account_cards'

    def parse(self, context, raw_value):
        try:
            cards_uids = [int(card_id.strip()) for card_id in raw_value.split(',')]
        except ValueError:
            self.raise_wrong_format()

        for card_uid in cards_uids:
            if not context.account_hero.cards.has_card(card_uid=card_uid):
                self.raise_wrong_value()

        return [context.account_hero.cards.get_card(card_uid) for card_uid in cards_uids]


########################################
# resource and global processors
########################################
resource = dext_views.Resource(name='cards')
resource.add_processor(accounts_views.CurrentAccountProcessor())
resource.add_processor(utils_views.FakeResourceProcessor())
resource.add_processor(heroes_views.CurrentHeroProcessor())

guide_resource = dext_views.Resource(name='cards')
guide_resource.add_processor(accounts_views.CurrentAccountProcessor())
guide_resource.add_processor(utils_views.FakeResourceProcessor())

########################################
# filters
########################################

class INDEX_ORDER(DjangoEnum):
    records = ( ('RARITY', 0, u'по редкости'),
                ('NAME', 1, u'по имени') )

CARDS_FILTER = [list_filter.reset_element(),
                list_filter.choice_element(u'редкость:', attribute='rarity', choices=[(None, u'все')] + list(relations.RARITY.select('value', 'text'))),
                list_filter.choice_element(u'доступность:', attribute='availability', choices=[(None, u'все')] + list(relations.AVAILABILITY.select('value', 'text'))),
                list_filter.choice_element(u'сортировка:',
                                           attribute='order_by',
                                           choices=list(INDEX_ORDER.select('value', 'text')),
                                           default_value=INDEX_ORDER.RARITY.value)]

class CardsFilter(list_filter.ListFilter):
    ELEMENTS = CARDS_FILTER



########################################
# views
########################################

@accounts_views.LoginRequiredProcessor()
@AccountCardProcessor()
@resource('use-dialog')
def use_dialog(context):
    return dext_views.Page('cards/use_dialog.html',
                           content={'hero': context.account_hero,
                                    'card': context.account_card,
                                    'form': context.account_card.type.form(),
                                    'resource': context.resource} )

@accounts_views.LoginRequiredProcessor()
@AccountCardProcessor()
@api.Processor(versions=(conf.settings.USE_API_VERSION, ))
@resource('api', 'use', name='api-use', method='POST')
def api_use(context):
    u'''
Использовать карту из колоды игрока.

- **адрес:** /game/cards/api/use
- **http-метод:** POST
- **версии:** 1.0
- **параметры:**
    * GET: card — уникальный идентификатор карты в калоде
    * POST: person — идентификатор Мастера, если карта применяется к Мастеру
    * POST: place — идентификатор города, если карта применяется к городу
    * POST: building — идентификатор здания, если карта применяется к зданию
- **возможные ошибки**:
    * cards.use.form_errors — ошибка в одном из POST параметров

Метод является «неблокирующей операцией» (см. документацию), формат ответа соответствует ответу для всех «неблокирующих операций».
    '''
    form = context.account_card.type.form(context.django_request.POST)

    if not form.is_valid():
        raise dext_views.ViewError(code=u'form_errors', message=form.errors)

    task = context.account_card.activate(context.account_hero, data=form.get_card_data())

    return dext_views.AjaxProcessing(task.status_url)


@accounts_views.LoginRequiredProcessor()
@resource('combine-dialog')
def combine_dialog(context):
    cards = sorted(effects.EFFECTS.values(), key=lambda x: (x.TYPE.rarity.value, x.TYPE.text))

    return dext_views.Page('cards/combine_dialog.html',
                           content={'CARDS': cards,
                                    'hero': context.account_hero,
                                    'resource': context.resource} )


@accounts_views.LoginRequiredProcessor()
@api.Processor(versions=(conf.settings.GET_API_VERSION, ))
@resource('api', 'get', name='api-get', method='post')
def api_get(context):
    u'''
Взять новую карту в колоду игрока.

- **адрес:** /game/cards/api/get
- **http-метод:** POST
- **версии:** 1.0
- **параметры:** нет
- **возможные ошибки**: нет

Метод является «неблокирующей операцией» (см. документацию), формат ответа соответствует ответу для всех «неблокирующих операций».

При завершении операции возвращается дополнительная инфрмация:

    {
      "message": "строка",      // описание результата в формате html
      "card": <card_info>       // описание полученной карты, формат см. в описании формата информации о герое
    }
    '''
    choose_task = heroes_postponed_tasks.GetCardTask(hero_id=context.account_hero.id)

    task = PostponedTaskPrototype.create(choose_task)

    amqp_environment.environment.workers.supervisor.cmd_logic_task(context.account.id, task.id)

    return dext_views.AjaxProcessing(task.status_url)


@accounts_views.LoginRequiredProcessor()
@AccountCardsProcessor()
@api.Processor(versions=(conf.settings.COMBINE_API_VERSION, ))
@resource('api', 'combine', name='api-combine', method='post')
def api_combine(context):
    u'''
Объединить карты из колоды игрока.

- **адрес:** /game/cards/api/combine
- **http-метод:** POST
- **версии:** 1.0
- **параметры:**
    * GET: cards — перечень уникальный идентификаторов карт в колоде игрока через запятую
- **возможные ошибки**:
    * cards.api-combine.wrong_cards — указанные карты нельзя объединить

Метод является «неблокирующей операцией» (см. документацию), формат ответа соответствует ответу для всех «неблокирующих операций».

При завершении операции возвращается дополнительная инфрмация:

    {
      "message": "строка",      // описание результата в формате html
      "card": <card_info>       // описание полученной карты, формат см. в описании формата информации о герое
    }
    '''
    can_combine_status = context.account_hero.cards.can_combine_cards([card.uid for card in context.account_cards])

    if not can_combine_status.is_ALLOWED:
        raise dext_views.ViewError(code=u'wrong_cards', message=can_combine_status.text)

    choose_task = heroes_postponed_tasks.CombineCardsTask(hero_id=context.account_hero.id, cards=[card.uid for card in context.account_cards])

    task = PostponedTaskPrototype.create(choose_task)

    amqp_environment.environment.workers.supervisor.cmd_logic_task(context.account.id, task.id)

    return dext_views.AjaxProcessing(task.status_url)



@dext_views.RelationArgumentProcessor(relation=relations.RARITY, default_value=None,
                                      error_message=u'неверный тип редкости карты',
                                      context_name='cards_rarity', get_name='rarity')
@dext_views.RelationArgumentProcessor(relation=relations.AVAILABILITY, default_value=None,
                                      error_message=u'неверный тип доступности карты',
                                      context_name='cards_availability', get_name='availability')
@dext_views.RelationArgumentProcessor(relation=INDEX_ORDER, default_value=INDEX_ORDER.RARITY,
                                      error_message=u'неверный тип сортировки карт',
                                      context_name='cards_order_by', get_name='order_by')
@guide_resource('')
def index(context):
    from the_tale.game.cards.relations import RARITY

    cards = effects.EFFECTS.values()

    if context.cards_availability:
        cards = [card for card in cards if card.TYPE.availability == context.cards_availability]

    if context.cards_rarity:
        cards = [card for card in cards if card.TYPE.rarity == context.cards_rarity]

    if context.cards_order_by.is_RARITY:
        cards = sorted(cards, key=lambda c: (c.TYPE.rarity.value, c.TYPE.text))
    elif context.cards_order_by.is_NAME:
        cards = sorted(cards, key=lambda c: (c.TYPE.text, c.TYPE.rarity.value))

    url_builder = UrlBuilder(url('guide:cards:'), arguments={ 'rarity': context.cards_rarity.value if context.cards_rarity else None,
                                                              'availability': context.cards_availability.value if context.cards_availability else None,
                                                              'order_by': context.cards_order_by.value})

    index_filter = CardsFilter(url_builder=url_builder, values={'rarity': context.cards_rarity.value if context.cards_rarity else None,
                                                                'availability': context.cards_availability.value if context.cards_availability else None,
                                                                'order_by': context.cards_order_by.value if context.cards_order_by else None})


    return dext_views.Page('cards/index.html',
                           content={'section': 'cards',
                                    'CARDS': cards,
                                    'index_filter': index_filter,
                                    'CARD_RARITY': RARITY,
                                    'resource': context.resource})
