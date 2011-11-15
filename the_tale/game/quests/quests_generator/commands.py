# coding: utf-8

def deserialize_command(data):
    cmd = COMMAND_CLASSES[data['type']]()
    cmd.deserialize(data)
    return cmd

class Command(object):

    def __init__(self, event=None):
        self.event = event
        
    @classmethod
    def type(cls):
        return cls.__name__.lower()

    def get_description(self, env):
        return 'unknown command'

    def serialize(self):
        return { 'type': self.type(),
                 'event': self.event}

    def deserialize(self, data):
        self.event = data['event']


class Description(Command):

    def __init__(self, **kwargs):
        super(Description, self).__init__(**kwargs)

    def get_description(self, env):
        return '<description> msg: %s' % self.event

    def serialize(self):
        data = super(Description, self).serialize()
        data.update({'msg': self.context_msg})
        return data

    def deserialize(self, data):
        super(Description, self).deserialize(data)
        self.context_msg = data['msg']


class Move(Command):

    def __init__(self, place=None, **kwargs):
        super(Move, self).__init__(**kwargs)
        self.place = place

    def get_description(self, env):
        return '<move to> place: %s' % self.place

    def serialize(self):
        data = super(Move, self).serialize()
        data.update({'place': self.place})
        return data

    def deserialize(self, data):
        super(Move, self).deserialize(data)
        self.place = data['place']


class GetItem(Command):

    def __init__(self, item=None, **kwargs):
        super(GetItem, self).__init__(**kwargs)
        self.item = item

    def get_description(self, env):
        return '<get item> item: %s' % self.item

    def serialize(self):
        data = super(GetItem, self).serialize()
        data.update({'item': self.item})
        return data

    def deserialize(self, data):
        super(GetItem, self).deserialize(data)
        self.item = data['item']


class GiveItem(Command):

    def __init__(self, item=None, **kwargs):
        super(GiveItem, self).__init__(**kwargs)
        self.item = item

    def get_description(self, env):
        return '<give item> item: %s' % self.item

    def serialize(self):
        data = super(GiveItem, self).serialize()
        data.update({'item': self.item})
        return data

    def deserialize(self, data):
        super(GiveItem, self).deserialize(data)
        self.item = data['item']

class GetReward(Command):
    
    def __init__(self, person=None, **kwargs):
        super(GetReward, self).__init__(**kwargs)
        self.person = person

    def get_description(self, env):
        return '<get revard> person: %s' % self.person

    def serialize(self):
        data = super(GetReward, self).serialize()
        data.update({'person': self.person})
        return data

    def deserialize(self, data):
        super(GetReward, self).deserialize(data)
        self.person = data['person']

class GivePower(Command):

    def __init__(self, person=None, power=None, multiply=None, depends_on=None, **kwargs):
        super(GivePower, self).__init__(**kwargs)
        self.person = person
        self.power = power
        self.multiply = multiply
        self.depends_on = depends_on

    def get_description(self, env):
        return '<give power> person: %s (power: %s, multiply: %s, depends_on: %s)' % (self.person, self.power, self.multiply, self.depends_on)

    def serialize(self):
        data = super(GivePower, self).serialize()
        data.update({'power': self.power,
                     'person': self.person,
                     'depends_on': self.depends_on,
                     'multiply': self.multiply})
        return data

    def deserialize(self, data):
        super(GivePower, self).deserialize(data)
        self.person = data['person']
        self.depends_on = data['depends_on']
        self.power = data['power']
        self.multiply = data['multiply']

class Choose(Command):

    def __init__(self, id=None, choices=None, default=None, choice=None, **kwargs):
        super(Choose, self).__init__(**kwargs)
        self.choices = choices
        self.default = default
        self.id = id
        self.choice = choice

    def get_description(self, env):
        return { 'cmd': 'choose',
                 'default': self.default,
                 'choices': self.choices,
                 'choice': self.choice}

    def serialize(self):
        data = super(Choose, self).serialize()
        data.update({'choices': self.choices,
                     'id': self.id,
                     'default': self.default,
                     'choice': self.choice})
        return data

    def deserialize(self, data):
        super(Choose, self).deserialize(data)
        self.id = data['id']
        self.choices = data['choices']
        self.default = data['default']
        self.choice = data['choice']


class Quest(Command):

    def __init__(self, quest=None, **kwargs):
        super(Quest, self).__init__(**kwargs)
        self.quest = quest

    def get_description(self, env):
        return env.quests[self.quest].get_description(env)

    def serialize(self):
        data = super(Quest, self).serialize()
        data.update({'quest': self.quest})
        return data

    def deserialize(self, data):
        super(Quest, self).deserialize(data)
        self.quest = data['quest']


COMMAND_CLASSES = dict( (cmd_class.type(), cmd_class) 
                        for cmd_name, cmd_class in globals().items() 
                        if isinstance(cmd_class, type) and issubclass(cmd_class, Command) and cmd_class is not Command)
