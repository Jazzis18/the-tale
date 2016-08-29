# coding: utf-8

from dext.forms import fields

from utg import words as utg_words
from utg import relations as utg_relations

from the_tale.game import names

from the_tale.linguistics.forms import WordField

from the_tale.game.bills import relations
from the_tale.game.bills.forms import BaseUserForm, BaseModeratorForm
from the_tale.game.bills.bills.base_bill import BaseBill

from the_tale.game.places import storage as places_storage
from the_tale.game.places import logic as places_logic


class UserForm(BaseUserForm):

    place = fields.ChoiceField(label=u'Город')
    name = WordField(word_type=utg_relations.WORD_TYPE.NOUN, label=u'Название', skip_markers=(utg_relations.NOUN_FORM.COUNTABLE,))

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['place'].choices = places_storage.places.get_choices()


class ModeratorForm(BaseModeratorForm):
    name = WordField(word_type=utg_relations.WORD_TYPE.NOUN, label=u'Название')


class PlaceRenaming(BaseBill):

    type = relations.BILL_TYPE.PLACE_RENAMING

    UserForm = UserForm
    ModeratorForm = ModeratorForm

    CAPTION = u'Переименование города'
    DESCRIPTION = u'Изменяет название города. При выборе нового названия постарайтесь учесть, какой расе принадлежит город, кто является его жителями и в какую сторону он развивается.'

    def __init__(self, place_id=None, name_forms=None, old_name_forms=None):
        super(PlaceRenaming, self).__init__()
        self.place_id = place_id
        self.name_forms = name_forms
        self.old_name_forms = old_name_forms

        if self.old_name_forms is None and self.place_id is not None:
            self.old_name_forms = self.place.utg_name

    @property
    def place(self): return places_storage.places[self.place_id]

    @property
    def actors(self): return [self.place]

    @property
    def base_name(self): return self.name_forms.normal_form()

    @property
    def old_name(self): return self.old_name_forms.normal_form()

    @property
    def place_name_changed(self):
        return self.old_name != self.place.name

    @property
    def user_form_initials(self):
        return {'place': self.place_id,
                'name': self.name_forms}

    @property
    def moderator_form_initials(self):
        return {'name': self.name_forms}

    def initialize_with_user_data(self, user_form):
        self.place_id = int(user_form.c.place)
        self.old_name_forms = self.place.utg_name
        self.name_forms = user_form.c.name

    def initialize_with_moderator_data(self, moderator_form):
        self.name_forms = moderator_form.c.name

    def has_meaning(self):
        return self.place.utg_name != self.name_forms

    def apply(self, bill=None):
        if self.has_meaning():
            self.place.set_utg_name(self.name_forms)
            places_logic.save_place(self.place)

    def serialize(self):
        return {'type': self.type.name.lower(),
                'old_name_forms': self.old_name_forms.serialize(),
                'name_forms': self.name_forms.serialize(),
                'place_id': self.place_id}

    @classmethod
    def deserialize(cls, data):
        obj = cls()

        if 'old_name_forms' in data:
            obj.old_name_forms = utg_words.Word.deserialize(data['old_name_forms'])
        else:
            obj.old_name_forms = names.generator.get_fast_name(u'название неизвестно')

        obj.name_forms = utg_words.Word.deserialize(data['name_forms'])
        obj.place_id = data['place_id']

        return obj
