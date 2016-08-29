# coding: utf-8
import datetime

from django.db import IntegrityError, transaction

from dext.common.utils import s11n

from utg import words as utg_words
from utg import templates as utg_templates
from utg import exceptions as utg_exceptions
from utg import constructors as utg_constructors
from utg.data import VERBOSE_TO_PROPERTIES

from the_tale.amqp_environment import environment

from the_tale.common.utils.prototypes import BasePrototype
from the_tale.common.utils.decorators import lazy_property
from the_tale.common.utils.logic import get_or_create

from the_tale.linguistics import models
from the_tale.linguistics import relations
from the_tale.linguistics.lexicon import logic as lexicon_logic
from the_tale.linguistics.lexicon import dictionary as lexicon_dictionary
from the_tale.linguistics.lexicon import relations as lexicon_relations


class WordPrototype(BasePrototype):
    _model_class = models.Word
    _readonly = ('id', 'type', 'created_at', 'updated_at', 'author_id')
    _bidirectional = ('state', 'parent_id', 'used_in_ingame_templates', 'used_in_onreview_templates', 'used_in_status')
    _get_by = ('id', 'parent_id')

    @lazy_property
    def utg_word(self):
        return utg_words.Word.deserialize(s11n.from_json(self._model.forms))

    def get_parent(self):
        if self.parent_id is None:
            return None
        return WordPrototype.get_by_id(self.parent_id)

    def get_child(self):
        return self.get_by_parent_id(self.id)

    def has_parent(self): return bool(self.get_parent())
    def has_child(self): return bool(self.get_child())


    @classmethod
    def create(cls, utg_word, parent=None, author=None, state=relations.WORD_STATE.ON_REVIEW):
        model = cls._db_create(type=utg_word.type,
                               state=state,
                               normal_form=utg_word.normal_form(),
                               forms=s11n.to_json(utg_word.serialize()),
                               parent=parent._model if parent is not None else None,
                               author=author._model if author is not None else None)

        prototype = cls(model)

        environment.workers.linguistics_manager.cmd_game_dictionary_changed()

        return prototype

    def save(self):
        from the_tale.linguistics import storage

        self._model.forms = s11n.to_json(self.utg_word.serialize())
        self._model.normal_form = self.utg_word.normal_form()
        self._model.updated_at = datetime.datetime.now()

        super(WordPrototype, self).save()

        if self.state.is_IN_GAME:
            storage.game_dictionary.update_version()
            storage.game_dictionary.refresh()

        environment.workers.linguistics_manager.cmd_game_dictionary_changed()


    def remove(self):
        self._model.delete()

    def update_used_in_status(self, used_in_ingame_templates, used_in_onreview_templates, force_update=True):
        changed = (self.used_in_ingame_templates != used_in_ingame_templates or self.used_in_onreview_templates != used_in_onreview_templates)

        self.used_in_ingame_templates = used_in_ingame_templates
        self.used_in_onreview_templates = used_in_onreview_templates

        if self.used_in_ingame_templates > 0:
            self.used_in_status = relations.WORD_USED_IN_STATUS.IN_INGAME_TEMPLATES
        elif self.used_in_onreview_templates > 0:
            self.used_in_status = relations.WORD_USED_IN_STATUS.IN_ONREVIEW_TEMPLATES
        else:
            self.used_in_status = relations.WORD_USED_IN_STATUS.NOT_USED

        if force_update and changed:
            self._db_filter(id=self.id).update(used_in_status=self.used_in_status,
                                               used_in_ingame_templates=self.used_in_ingame_templates,
                                               used_in_onreview_templates=self.used_in_onreview_templates)



class TemplatePrototype(BasePrototype):
    _model_class = models.Template
    _readonly = ('id', 'created_at', 'updated_at', 'raw_template', 'author_id')
    _bidirectional = ('state', 'parent_id', 'errors_status', 'key')
    _get_by = ('id', 'parent_id')

    def get_parent(self):
        if self.parent_id is None:
            return None
        return TemplatePrototype.get_by_id(self.parent_id)

    def get_child(self):
        return self.get_by_parent_id(self.id)


    @lazy_property
    def _data(self):
        return s11n.from_json(self._model.data)

    @lazy_property
    def lexicon_groups(self):
        return {key: tuple(value) for key, value in self._data['groups'].iteritems()}

    @lazy_property
    def verificators(self):
        return [Verificator.deserialize(v) for v in self._data['verificators']]

    @lazy_property
    def raw_restrictions(self):
        return frozenset(tuple(key) for key in self._data.get('restrictions', ()))

    @lazy_property
    def restrictions(self):
        from the_tale.linguistics import storage

        data = {}

        for variable_value, restriction_id in self.raw_restrictions:
            variable = lexicon_relations.VARIABLE(variable_value)

            if variable not in data:
                data[variable] = []

            data[variable].append(storage.restrictions_storage[restriction_id])

        return data

    @lazy_property
    def utg_template(self):
        return utg_templates.Template.deserialize(self._data['template'])

    @classmethod
    def get_start_verificatos(self, key):
        groups = lexicon_logic.get_verificators_groups(key=key, old_groups=())
        verificators = Verificator.get_verificators(key=key, groups=groups, old_verificators=())
        return verificators

    def get_all_verificatos(self):
        groups = lexicon_logic.get_verificators_groups(key=self.key, old_groups=self.lexicon_groups)
        verificators = Verificator.get_verificators(key=self.key, groups=groups, old_verificators=self.verificators)
        return verificators

    def get_errors(self):
        from the_tale.linguistics import storage
        from the_tale.linguistics import logic


        utg_dictionary = storage.game_dictionary.item

        errors = []

        verificators = self.get_all_verificatos()

        unexisted_words = self.utg_template.get_undictionaried_words(externals=[v.value for v in self.key.variables],
                                                                     dictionary=utg_dictionary)

        for word in unexisted_words:
            errors.append(u'Неизвестное слово: «%s»' % word)

        if errors:
            return errors

        for verificator in verificators:
            externals = verificator.preprocessed_externals()

            try:
                template_render = self.utg_template.substitute(externals=externals, dictionary=utg_dictionary)
            except utg_exceptions.MoreThenOneWordFoundError as e:
                errors.append(u'Невозможно однозначно определить слово с формой «%s» — существует несколько слов с такими формами. Укажите более точные свойства.' %
                              e.arguments['text'])
                return errors

            import jinja2
            if logic.efication(verificator.text) != logic.efication(template_render):
                errors.append(u'Проверочный текст не совпадает с интерпретацией шаблона<br/>%s<br/>%s' % (jinja2.escape(template_render), jinja2.escape(verificator.text)) )

        return errors

    def has_errors(self):
        return bool(self.get_errors())

    def sync_restrictions(self):
        with transaction.atomic():
            models.TemplateRestriction.objects.filter(template_id=self.id).delete()
            for variable, restrictions in self.restrictions.iteritems():
                for restriction in restrictions:
                    models.TemplateRestriction.objects.create(template_id=self.id, variable=variable.value, restriction_id=restriction.id)


    @classmethod
    def create(cls, key, raw_template, utg_template, verificators, author, parent=None, restrictions=frozenset(), state=relations.TEMPLATE_STATE.ON_REVIEW):
        model = cls._db_create(key=key,
                               state=state,
                               raw_template=raw_template,
                               author=None if author is None else author._model,
                               parent=None if parent is None else parent._model,
                               data=s11n.to_json({'verificators': [v.serialize() for v in verificators],
                                                  'template': utg_template.serialize(),
                                                  'restrictions': list(restrictions),
                                                  'groups': lexicon_logic.get_verificators_groups(key=key)}))
        prototype = cls(model)

        prototype.update_errors_status(force_update=True)
        prototype.sync_restrictions()

        environment.workers.linguistics_manager.cmd_game_lexicon_changed()

        return prototype


    def update(self, raw_template=None, utg_template=None, verificators=None, restrictions=None):
        if raw_template is not None:
            self._model.raw_template = raw_template

        self.del_lazy_properties()

        if verificators is not None:
            self._data['verificators'] = [v.serialize() for v in verificators]

        if utg_template is not None:
            self._data['template'] = utg_template.serialize()

        if restrictions is not None:
            self._data['restrictions'] = list(restrictions)

        self._data['groups'] = self.lexicon_groups

        self.save()


    def save(self):
        from the_tale.linguistics import storage

        self._data['verificators'] = [v.serialize() for v in self.verificators]
        self._data['restrictions'] = list(self.raw_restrictions)
        self._data['template'] = self.utg_template.serialize()
        self._data['groups'] = self.lexicon_groups

        self._model.data = s11n.to_json(self._data)

        self._model.updated_at = datetime.datetime.now()

        self.update_errors_status(force_update=False)
        self.sync_restrictions()

        super(TemplatePrototype, self).save()

        if self.state.is_IN_GAME:
            storage.game_lexicon.update_version()
            storage.game_lexicon.refresh()

        environment.workers.linguistics_manager.cmd_game_lexicon_changed()

    def remove(self):
        self._model.delete()

    def update_errors_status(self, force_update=False):
        old_errors_status = self.errors_status

        if self.has_errors():
            self.errors_status = relations.TEMPLATE_ERRORS_STATUS.HAS_ERRORS
        else:
            self.errors_status = relations.TEMPLATE_ERRORS_STATUS.NO_ERRORS

        if force_update and old_errors_status != self.errors_status:
            self._db_filter(id=self.id).update(errors_status=self.errors_status)

        return old_errors_status != self.errors_status


class Verificator(object):
    __slots__ = ('text', 'externals')

    def __init__(self, text, externals):
        self.text = text
        self.externals = externals

    def serialize(self):
        return {'text': self.text,
                'externals': self.externals}

    @classmethod
    def deserialize(cls, data):
        return cls(text=data['text'],
                   externals={k: tuple(v) for k,v in data['externals'].iteritems()})

    def __eq__(self, other):
        return (self.text == other.text and
                self.externals == other.externals)

    def get_label(self):
        externals = self.preprocessed_externals()
        return u'Проверка для %s' % u', '.join(u'%s=%s' % (variable, value.form) for variable, value in externals.iteritems())

    def preprocessed_externals(self):
        externals = {}
        for k, (word_form, additional_properties) in self.externals.iteritems():

            if isinstance(word_form, (int, long)):
                word_form = utg_constructors.construct_integer(word_form)
            else:
                word_form = lexicon_dictionary.DICTIONARY.get_word(word_form)

            if additional_properties:
                properties = utg_words.Properties(word_form.properties,
                                                *[VERBOSE_TO_PROPERTIES[prop.strip()] for prop in additional_properties.split(',') if prop])
                word_form = utg_words.WordForm(word=word_form.word,
                                               properties=properties)

            externals[k] = word_form

        return externals


    @classmethod
    def _fill_externals(cls, externals, start_substitutions, work_substitutions, used_substitutions):
        for variable_value, substitutions in work_substitutions.iteritems():

            if variable_value in externals:
                continue

            # we can just get first candidate element since all substitutions has already shifted in VARIABLE_VERIFICATOR
            substitution = substitutions.pop(0)

            used_substitutions[variable_value].add(substitution)

            externals[variable_value] = substitution

            # substitutions.remove(substitution)

            if not substitutions:
                substitutions.extend(start_substitutions[variable_value])


    @classmethod
    def get_verificators(cls, key, groups, old_verificators=()):
        from the_tale.linguistics.lexicon.relations import VARIABLE_VERIFICATOR

        start_substitutions = {}
        used_substitutions = {}
        work_substitutions = {}

        for variable_value, (verificator_value, substitution_index) in groups.iteritems():
            verificator = VARIABLE_VERIFICATOR(verificator_value)
            start_substitutions[variable_value] = list(verificator.substitutions[substitution_index])
            work_substitutions[variable_value] = list(start_substitutions[variable_value])
            used_substitutions[variable_value] = set()

        verificators = []

        # filter old verificators which is correct now
        for old_verificator in old_verificators:
            correct_verificator = True

            for variable_value, substitution in old_verificator.externals.iteritems():
                if variable_value not in work_substitutions: # if variable removed from key
                    continue
                if substitution not in work_substitutions[variable_value]:
                    correct_verificator = False
                    break

            if not correct_verificator:
                continue

            verificators.append(old_verificator)

            for variable_value, substitution in old_verificator.externals.iteritems():
                if variable_value not in work_substitutions: # if variable removed from key
                    continue
                used_substitutions[variable_value].add(substitution)

                work_substitution = work_substitutions[variable_value]
                work_substitution.remove(substitution)
                if not work_substitution:
                    work_substitution.extend(start_substitutions[variable_value])

        # fill verificator groups with new substitutions, if they are added to groups after template was created
        for old_verificator in old_verificators:
            cls._fill_externals(old_verificator.externals, start_substitutions, work_substitutions, used_substitutions)

        # add lost verificators
        while not all(used_substitutions[external] == set(start_substitutions[external]) for external in used_substitutions.iterkeys()):
            externals = {}

            cls._fill_externals(externals, start_substitutions, work_substitutions, used_substitutions)

            verificators.append(cls(text=u'', externals=externals))

        return verificators



class ContributionPrototype(BasePrototype):
    _model_class = models.Contribution
    _readonly = ('id', 'created_at', 'account_id', 'type', 'entity_id', 'source', 'state')
    _bidirectional = ()
    _get_by = ('id', 'account_id', 'entity_id')


    @classmethod
    def create(cls, type, account_id, entity_id, source, state):
        return cls(cls._db_create(type=type,
                                  account_id=account_id,
                                  entity_id=entity_id,
                                  source=source,
                                  state=state))

    @classmethod
    def get_for(cls, type, account_id, entity_id, source, state):
        try:
            return cls(cls._db_get(type=type, account_id=account_id, entity_id=entity_id, state=state))
        except cls._model_class.DoesNotExist:
            return None

    @classmethod
    def get_for_or_create(cls, type, account_id, entity_id, source, state):
        return get_or_create(get_method=cls.get_for,
                             create_method=cls.create,
                             exception=IntegrityError,
                             kwargs={'type': type,
                                     'account_id': account_id,
                                     'entity_id': entity_id,
                                     'source': source,
                                     'state': state})
