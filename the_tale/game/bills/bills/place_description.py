# coding: utf-8

from dext.forms import fields

from utg import words as utg_words

from the_tale.game import names

from the_tale.common.utils import bbcode

from the_tale.game.bills import relations
from the_tale.game.bills.forms import BaseUserForm, BaseModeratorForm
from the_tale.game.bills.bills.base_bill import BaseBill

from the_tale.game.places import storage as places_storage
from the_tale.game.places import conf as places_conf
from the_tale.game.places import logic as places_logic

class UserForm(BaseUserForm):

    place = fields.ChoiceField(label=u'Город')
    new_description = bbcode.BBField(label=u'Новое описание', max_length=places_conf.settings.MAX_DESCRIPTION_LENGTH)

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['place'].choices = places_storage.places.get_choices()


class ModeratorForm(BaseModeratorForm):
    pass


class PlaceDescripton(BaseBill):

    type = relations.BILL_TYPE.PLACE_DESCRIPTION

    UserForm = UserForm
    ModeratorForm = ModeratorForm

    CAPTION = u'Изменение описания города'
    DESCRIPTION = u'Изменяет описание города. При создании нового описания постарайтесь учесть, какой расе принадлежит город, кто является его жителями и в какую сторону он развивается. Также не забывайте, что описание должно соответствовать названию города. Описание должно быть небольшим по размеру.'

    def __init__(self, place_id=None, description=None, old_name_forms=None, old_description=None):
        super(PlaceDescripton, self).__init__()
        self.place_id = place_id
        self.description = description
        self.old_name_forms = old_name_forms
        self.old_description = old_description

        if self.old_name_forms is None and self.place_id is not None:
            self.old_name_forms = self.place.utg_name

    @property
    def description_html(self): return bbcode.render(self.description)

    @property
    def old_description_html(self): return bbcode.render(self.old_description)

    @property
    def old_name(self): return self.old_name_forms.normal_form()

    @property
    def place(self): return places_storage.places[self.place_id]

    @property
    def actors(self): return [self.place]

    @property
    def user_form_initials(self):
        return {'place': self.place_id,
                'new_description': self.description}

    @property
    def place_name_changed(self):
        return self.old_name != self.place.name

    def initialize_with_user_data(self, user_form):
        self.place_id = int(user_form.c.place)
        self.description = user_form.c.new_description
        self.old_name_forms = self.place.utg_name
        self.old_description = self.place.description

    def has_meaning(self):
        return self.place.description != self.description

    def apply(self, bill=None):
        if self.has_meaning():
            self.place.description = self.description
            places_logic.save_place(self.place)

    def serialize(self):
        return {'type': self.type.name.lower(),
                'description': self.description,
                'place_id': self.place_id,
                'old_name_forms': self.old_name_forms.serialize(),
                'old_description': self.old_description}

    @classmethod
    def deserialize(cls, data):
        obj = cls()
        obj.description = data['description']
        obj.place_id = data['place_id']

        if 'old_name_forms' in data:
            obj.old_name_forms = utg_words.Word.deserialize(data['old_name_forms'])
        else:
            obj.old_name_forms = names.generator.get_fast_name(u'название неизвестно')

        obj.old_description = data.get('old_description', u'неизвестно')

        return obj
