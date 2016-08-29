# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [(u'ACTION_REST_DESCRIPTION', 180000, u'Описание', LEXICON_GROUP.ACTION_REST,
        u'Краткая декларация того, что делает герой.',
        [V.HERO], None),

        (u'ACTION_REST_RESRING', 180001, u'Журнал: Отдых', LEXICON_GROUP.ACTION_REST,
        u'Герой лечится и восстанавливает немного здоровья.',
        [V.HERO, V.HEALTH], u'hero#N +health#HP'),

        (u'ACTION_REST_START', 180002, u'Журнал: Начало', LEXICON_GROUP.ACTION_REST,
        u'Герой начинает лечиться.',
        [V.HERO], None),

        ]
