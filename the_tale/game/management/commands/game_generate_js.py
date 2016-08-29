# coding: utf-8

from django.core.management.base import BaseCommand

from dext.common.utils import s11n
from dext.common.utils import jinja2

from the_tale.game.conf import game_settings

from the_tale.game.quests.relations import ACTOR_TYPE
from the_tale.game.relations import GENDER, RACE
from the_tale.game.map.conf import map_settings
from the_tale.game.map.relations import SPRITES
from the_tale.game.persons.relations import PERSON_TYPE
from the_tale.game.abilities.relations import ABILITY_TYPE
from the_tale.game.relations import GAME_STATE
from the_tale.game.artifacts import relations as artifacts_relations
from the_tale.game.artifacts.effects import EFFECTS
from the_tale.game.cards import relations as cards_relations
from the_tale.game.cards import effects as cards_effects

from the_tale.linguistics import logic as linguistics_logic
from the_tale.linguistics.lexicon import keys as linguistics_keys


class Command(BaseCommand):

    help = 'generate javascript files'

    option_list = BaseCommand.option_list

    def handle(self, *args, **options):

        LINGUISTICS_FORMATTERS = {key.value: linguistics_logic.ui_format(key.ui_text)
                                  for key in linguistics_keys.LEXICON_KEY.records
                                  if key.ui_text is not None}

        with open(game_settings.JS_CONSTNATS_FILE_LOCATION, 'w') as f:
            f.write(jinja2.render('game/js_constants.js',
                                  context={'actor_type': s11n.to_json({a.name: a.value for a in ACTOR_TYPE.records}),
                                           'gender_to_text': s11n.to_json(dict(GENDER.select('value', 'text'))),
                                           'gender_to_str': s11n.to_json(dict(GENDER.select('value', 'name'))),
                                           'person_type_to_text': s11n.to_json(dict(PERSON_TYPE.select('value', 'text'))),
                                           'race_to_text': s11n.to_json(dict(RACE.select('value', 'text'))),
                                           'race_to_str': s11n.to_json(dict(RACE.select('value', 'name'))),
                                           'game_state': s11n.to_json(dict(GAME_STATE.select('name', 'value'))),
                                           'ARTIFACT_TYPE': artifacts_relations.ARTIFACT_TYPE,
                                           'NO_EFFECT': artifacts_relations.ARTIFACT_EFFECT.NO_EFFECT,
                                           'EFFECTS': EFFECTS,
                                           'ARTIFACT_RARITY': artifacts_relations.RARITY,
                                           'CARD_RARITY': cards_relations.RARITY,
                                           'CARDS_EFFECTS': cards_effects.EFFECTS,
                                           'ABILITY_TYPE': ABILITY_TYPE,
                                           'SPRITES': SPRITES,
                                           'CELL_SIZE': map_settings.CELL_SIZE,
                                           'LINGUISTICS_FORMATTERS': LINGUISTICS_FORMATTERS
                                          }).encode('utf-8'))
