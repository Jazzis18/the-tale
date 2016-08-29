# coding: utf-8

from the_tale.game.abilities.relations import ABILITY_TYPE

from the_tale.game.postponed_tasks import ComplexChangeTask

from the_tale.game.places import storage as places_storage



class UseAbilityTask(ComplexChangeTask):
    TYPE = 'user-ability'

    def construct_processor(self):
        from the_tale.game.abilities.deck import ABILITIES
        return ABILITIES[ABILITY_TYPE(self.processor_id)]()

    @property
    def processed_data(self):

        data = {}

        if self.data.get('building_id') is not None:
            building = places_storage.buildings[self.data['building_id']]
            data['building'] = { 'new_building_integrity': building.integrity,
                                 'workers_to_full_repairing': building.workers_to_full_repairing }

        if self.message:
            data['message'] = self.message

        return data
