# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [(u'PVP_MISS_ABILITY', 340000, u'Журнал: Неудачное использование способности', LEXICON_GROUP.PVP,
         u'Хранитель пытается применить способность и терпит неудачу.',
         [V.DUELIST_1, V.DUELIST_2], None),

        (u'PVP_SAY', 340001, u'Журнал: Сообщение', LEXICON_GROUP.PVP,
         u'Один из участвующих Хранителей что-то сказал.',
         [V.TEXT], None),

        (u'PVP_USE_ABILITY_BLOOD', 340002, u'Журнал: Использование способности крови', LEXICON_GROUP.PVP,
         u'Хранитель применяет способность крови.',
         [V.EFFECTIVENESS, V.DUELIST_1, V.DUELIST_2], u'duelist_1#N +effectiveness#EF'),

        (u'PVP_USE_ABILITY_FLAME', 340003, u'Журнал: Использование способности пламени', LEXICON_GROUP.PVP,
         u'Хранитель применяет способность пламени.',
         [V.DUELIST_1, V.DUELIST_2], None),

        (u'PVP_USE_ABILITY_ICE', 340004, u'Журнал: Использование способности льда', LEXICON_GROUP.PVP,
         u'Хранитель применяет способность льда.',
         [V.DUELIST_1, V.DUELIST_2], None),

       ]
