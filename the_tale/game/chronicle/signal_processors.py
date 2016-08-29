# coding: utf-8

from django.dispatch import receiver

from the_tale.game.bills import signals as bills_signals
from the_tale.game.bills import relations as bill_relations

from the_tale.game.places import signals as places_signals

from the_tale.game.chronicle import records
from the_tale.game.chronicle.relations import ACTOR_ROLE


class WordFormWrapper(object):
    __slots__ = ('word', 'restrictions')

    def __init__(self, word, restrictions=()):
        self.word = word
        self.restrictions = restrictions

    @property
    def utg_name_form(self):
        from utg import words as utg_words
        return utg_words.WordForm(self.word)

    def linguistics_restrictions(self):
        return self.restrictions



def _get_bill_place_renaming_arguments(bill):
    return { 'actors': [(ACTOR_ROLE.BILL, bill),
                        (ACTOR_ROLE.PLACE, bill.data.place)],
             'substitutions': {},
             'text': bill.chronicle_on_accepted }

def _get_bill_place_description_arguments(bill):
    return { 'actors': [(ACTOR_ROLE.BILL, bill),
                        (ACTOR_ROLE.PLACE, bill.data.place)],
             'substitutions': {},
             'text': bill.chronicle_on_accepted }

def _get_bill_place_modifier_arguments(bill):
    return { 'actors': [(ACTOR_ROLE.BILL, bill),
                        (ACTOR_ROLE.PLACE, bill.data.place)],
             'substitutions': {},
             'text': bill.chronicle_on_accepted }

def _get_bill_person_remove_arguments(bill):
    return { 'actors': [(ACTOR_ROLE.BILL, bill),
                        (ACTOR_ROLE.PLACE, bill.data.person.place),
                        (ACTOR_ROLE.PERSON, bill.data.person)],
             'substitutions': {},
             'text': bill.chronicle_on_accepted }

def _get_bill_person_move_arguments(bill):
    return { 'actors': [(ACTOR_ROLE.BILL, bill),
                        (ACTOR_ROLE.PLACE, bill.data.place),
                        (ACTOR_ROLE.PLACE, bill.data.new_place),
                        (ACTOR_ROLE.PERSON, bill.data.person)],
             'substitutions': {},
             'text': bill.chronicle_on_accepted }

def _get_bill_person_chronicle_arguments(bill):
    return { 'actors': [(ACTOR_ROLE.BILL, bill),
                        (ACTOR_ROLE.PLACE, bill.data.person.place),
                        (ACTOR_ROLE.PERSON, bill.data.person)],
             'substitutions': {},
             'text': bill.chronicle_on_accepted }

def _get_bill_place_chronicle_arguments(bill):
    return { 'actors': [(ACTOR_ROLE.BILL, bill),
                        (ACTOR_ROLE.PLACE, bill.data.place)],
             'substitutions': {},
             'text': bill.chronicle_on_accepted }

def _get_bill_building_arguments(bill):
    return { 'actors': [(ACTOR_ROLE.BILL, bill),
                        (ACTOR_ROLE.PLACE, bill.data.person.place),
                        (ACTOR_ROLE.PERSON, bill.data.person)],
             'substitutions': {},
             'text': bill.chronicle_on_accepted }

def _get_bill_building_rename_arguments(bill):
    return { 'actors': [(ACTOR_ROLE.BILL, bill),
                        (ACTOR_ROLE.PLACE, bill.data.person.place),
                        (ACTOR_ROLE.PERSON, bill.data.person)],
             'substitutions': {},
             'text': bill.chronicle_on_accepted }

def _get_bill_place_resource_exchange_arguments(bill):
    return { 'actors': [(ACTOR_ROLE.BILL, bill),
                        (ACTOR_ROLE.PLACE, bill.data.place_1),
                        (ACTOR_ROLE.PLACE, bill.data.place_2)],
             'substitutions': {},
             'text': bill.chronicle_on_accepted}

def _get_bill_place_resource_conversion_arguments(bill):
    return { 'actors': [(ACTOR_ROLE.BILL, bill),
                        (ACTOR_ROLE.PLACE, bill.data.place)],
             'substitutions': {},
             'text': bill.chronicle_on_accepted }

def _get_bill_decline_bill_arguments(bill):
    if bill.data.declined_bill.data.type.is_PLACE_RESOURCE_EXCHANGE:
        actors = [(ACTOR_ROLE.BILL, bill),
                  (ACTOR_ROLE.PLACE, bill.data.declined_bill.data.place_1),
                  (ACTOR_ROLE.PLACE, bill.data.declined_bill.data.place_2)]
    elif bill.data.declined_bill.data.type.is_PLACE_RESOURCE_CONVERSION:
        actors = [(ACTOR_ROLE.BILL, bill),
                  (ACTOR_ROLE.PLACE, bill.data.declined_bill.data.place)]

    actors_ids = [(role, actor.id) for role, actor in actors]

    declined_bill_actors = BILL_ARGUMENT_GETTERS[bill.data.declined_bill.data.type](bill.data.declined_bill)['actors']

    for role, actor in declined_bill_actors:
        if (role, actor.id) not in actors_ids:
            actors.append((role, actor))

    return { 'actors': actors,
             'substitutions': {},
             'text': bill.chronicle_on_accepted}


BILL_ARGUMENT_GETTERS = {
    bill_relations.BILL_TYPE.PLACE_RENAMING: _get_bill_place_renaming_arguments,
    bill_relations.BILL_TYPE.PLACE_DESCRIPTION: _get_bill_place_description_arguments,
    bill_relations.BILL_TYPE.PLACE_CHANGE_MODIFIER: _get_bill_place_modifier_arguments,
    bill_relations.BILL_TYPE.PERSON_REMOVE: _get_bill_person_remove_arguments,
    bill_relations.BILL_TYPE.PERSON_MOVE: _get_bill_person_move_arguments,
    bill_relations.BILL_TYPE.BUILDING_CREATE: _get_bill_building_arguments,
    bill_relations.BILL_TYPE.BUILDING_DESTROY: _get_bill_building_arguments,
    bill_relations.BILL_TYPE.BUILDING_RENAMING: _get_bill_building_rename_arguments,
    bill_relations.BILL_TYPE.PLACE_RESOURCE_EXCHANGE: _get_bill_place_resource_exchange_arguments,
    bill_relations.BILL_TYPE.BILL_DECLINE: _get_bill_decline_bill_arguments,
    bill_relations.BILL_TYPE.PLACE_RESOURCE_CONVERSION: _get_bill_place_resource_conversion_arguments,
    bill_relations.BILL_TYPE.PERSON_CHRONICLE: _get_bill_person_chronicle_arguments,
    bill_relations.BILL_TYPE.PLACE_CHRONICLE: _get_bill_place_chronicle_arguments  }


@receiver(bills_signals.bill_processed, dispatch_uid='chronicle_bill_processed')
def chronicle_bill_processed(sender, bill, **kwargs): # pylint: disable=R0912,W0613

    if not bill.state.is_ACCEPTED:
        return

    if bill.data.type == bill_relations.BILL_TYPE.PLACE_RENAMING:
        record_type = records.PlaceChangeNameBillSuccessed

    elif bill.data.type == bill_relations.BILL_TYPE.PLACE_DESCRIPTION:
        record_type = records.PlaceChangeDescriptionBillSuccessed

    elif bill.data.type == bill_relations.BILL_TYPE.PLACE_CHANGE_MODIFIER:
        record_type = records.PlaceChangeModifierBillSuccessed

    elif bill.data.type == bill_relations.BILL_TYPE.PERSON_REMOVE:
        record_type = records.PersonRemoveBillSuccessed

    elif bill.data.type == bill_relations.BILL_TYPE.PERSON_MOVE:
        record_type = records.PersonMoveBillSuccessed

    elif bill.data.type == bill_relations.BILL_TYPE.BUILDING_CREATE:
        record_type = records.BuildingCreateBillSuccessed

    elif bill.data.type == bill_relations.BILL_TYPE.BUILDING_DESTROY:
        record_type = records.BuildingDestroyBillSuccessed

    elif bill.data.type == bill_relations.BILL_TYPE.BUILDING_RENAMING:
        record_type = records.BuildingRenamingBillSuccessed

    elif bill.data.type == bill_relations.BILL_TYPE.PLACE_RESOURCE_EXCHANGE:
        record_type = records.PlaceResourceExchangeBillSuccessed

    elif bill.data.type == bill_relations.BILL_TYPE.BILL_DECLINE:
        record_type = records.BillDeclineSuccessed

    elif bill.data.type == bill_relations.BILL_TYPE.PLACE_RESOURCE_CONVERSION:
        record_type = records.PlaceResourceConversionBillSuccessed

    elif bill.data.type == bill_relations.BILL_TYPE.PERSON_CHRONICLE:
        record_type = records.PersonChronicleBillSuccessed

    elif bill.data.type == bill_relations.BILL_TYPE.PLACE_CHRONICLE:
        record_type = records.PlaceChronicleBillSuccessed

    record_type(**BILL_ARGUMENT_GETTERS[bill.data.type](bill)).create_record()


@receiver(places_signals.place_person_arrived, dispatch_uid='chronicle_place_person_arrived')
def chronicle_place_person_arrived(sender, place, person, **kwargs): # pylint: disable=W0613
    records.PersonArrivedToPlace(actors=[(ACTOR_ROLE.PLACE, place),
                                         (ACTOR_ROLE.PERSON, person)],
                                 substitutions={'place':place,
                                                'person': person}).create_record()

@receiver(places_signals.place_race_changed, dispatch_uid='chronicle_place_race_changed')
def chronicle_place_race_changed(sender, place, old_race, new_race, **kwargs): # pylint: disable=W0613
    records.PlaceChangeRace(actors=[(ACTOR_ROLE.PLACE, place)],
                            substitutions={'place': place,
                                           'old_race': old_race,
                                           'new_race': new_race}).create_record()
