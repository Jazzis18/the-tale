# coding: utf-8

from dext.forms import forms, fields


from the_tale.game.places import storage as places_storage
from the_tale.game.persons import objects as persons_objects


class EmptyForm(forms.Form):
    TEMPLATE = None
    def get_card_data(self):
        return {}


class PersonForm(forms.Form):
    TEMPLATE = 'cards/person_form.html'
    person = fields.ChoiceField(label=u'Мастер')

    def __init__(self, *args, **kwargs):
        super(PersonForm, self).__init__(*args, **kwargs)
        self.fields['person'].choices = persons_objects.Person.form_choices()

    def get_card_data(self):
        return {'person_id': int(self.c.person)}


class PlaceForm(forms.Form):
    TEMPLATE = 'cards/place_form.html'
    place = fields.ChoiceField(label=u'Город')

    def __init__(self, *args, **kwargs):
        super(PlaceForm, self).__init__(*args, **kwargs)
        self.fields['place'].choices = places_storage.places.get_choices()

    def get_card_data(self):
        return {'place_id': int(self.c.place)}


class BuildingForm(forms.Form):
    TEMPLATE = 'cards/building_form.html'
    building = fields.ChoiceField(label=u'Строение')

    def __init__(self, *args, **kwargs):
        super(BuildingForm, self).__init__(*args, **kwargs)
        self.fields['building'].choices = places_storage.buildings.get_choices()

    def get_card_data(self):
        return {'building_id': int(self.c.building)}
