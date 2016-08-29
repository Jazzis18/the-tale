# coding: utf-8

from django.forms import ValidationError

from dext.forms import fields

from the_tale.common.utils.decorators import lazy_property


from the_tale.game.bills import relations
from the_tale.game.bills.forms import BaseUserForm, BaseModeratorForm
from the_tale.game.bills.bills.base_bill import BaseBill

from the_tale.game.places import storage as places_storage


class UserForm(BaseUserForm):

    declined_bill = fields.TypedChoiceField(label=u'Отменяемый закон', coerce=int)

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        bills = [exchange.bill for exchange in places_storage.resource_exchanges.all() if exchange.bill]
        self.fields['declined_bill'].choices = [(bill.id, bill.caption) for bill in bills]

    def clean(self):
        cleaned_data = super(UserForm, self).clean()

        if 'declined_bill' not in cleaned_data or not places_storage.resource_exchanges.get_exchange_for_bill_id(cleaned_data['declined_bill']):
            raise ValidationError(u'Закон уже не действует или не может быть отменён')

        return cleaned_data


class ModeratorForm(BaseModeratorForm):
    pass


class BillDecline(BaseBill):
    type = relations.BILL_TYPE.BILL_DECLINE

    UserForm = UserForm
    ModeratorForm = ModeratorForm

    CAPTION = u'Отмена действующего закона'
    DESCRIPTION = u'Отменяет действующий в текущий момент закон'

    def __init__(self, declined_bill_id=None):
        super(BillDecline, self).__init__()
        self.declined_bill_id = declined_bill_id

    @lazy_property
    def declined_bill(self):
        from the_tale.game.bills.prototypes import BillPrototype
        return BillPrototype.get_by_id(self.declined_bill_id)

    @property
    def actors(self): return self.declined_bill.data.actors

    @property
    def user_form_initials(self):
        return {'declined_bill': self.declined_bill_id}

    def initialize_with_user_data(self, user_form):
        self.declined_bill_id = int(user_form.c.declined_bill)

    def has_meaning(self):
        self.declined_bill.reload() # enshure that we loaded latest bill version
        return not self.declined_bill.is_declined

    def apply(self, bill=None):
        if self.has_meaning():
            self.declined_bill.decline(bill)

    def serialize(self):
        return {'type': self.type.name.lower(),
                'declined_bill_id': self.declined_bill_id}

    @classmethod
    def deserialize(cls, data):
        obj = cls()
        obj.declined_bill_id = data['declined_bill_id']

        return obj
