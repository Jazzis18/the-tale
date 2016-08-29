# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [(u'QUEST_HELP_ACTION_AFTER_SUCCESSED_HELP', 420000, u'Активность: после успешного задания', LEXICON_GROUP.QUEST_HELP,
         u'Краткое суммарное описание действий героя, когда он возвращается доложить об успешном выполнении задания.',
         [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        (u'QUEST_HELP_ACTION_INTRO', 420001, u'Активность: интро', LEXICON_GROUP.QUEST_HELP,
         u'Краткое суммарное описание действий героя в момент получения задания.',
         [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        (u'QUEST_HELP_ACTOR_INITIATOR', 420002, u'Актёр: инициатор задания', LEXICON_GROUP.QUEST_HELP,
         u'Название роли, инициирующей задание.',
         [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        (u'QUEST_HELP_ACTOR_RECEIVER', 420003, u'Актёр: цель задания', LEXICON_GROUP.QUEST_HELP,
         u'Название роли, цели задания.',
         [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        (u'QUEST_HELP_DIARY_FINISH_FAILED_ARTIFACT', 420004, u'Дневник: получение награды — провал (артефакт)', LEXICON_GROUP.QUEST_HELP,
         u'Герой получает награду за помощь, хотя выполнить задание не удалось (артефакт).',
         [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ARTIFACT], None),

        (u'QUEST_HELP_DIARY_FINISH_FAILED_MONEY', 420005, u'Дневник: получение награды — провал (деньги)', LEXICON_GROUP.QUEST_HELP,
         u'Герой получает награду за помощь хотя выполнить задание не удалось (деньги).',
         [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.COINS], u'hero#N +coins#G'),

        (u'QUEST_HELP_DIARY_FINISH_SUCCESSED_ARTIFACT', 420006, u'Дневник: получение награды (артефакт)', LEXICON_GROUP.QUEST_HELP,
         u'Герой получает награду за помощь (артефакт).',
         [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.ARTIFACT], None),

        (u'QUEST_HELP_DIARY_FINISH_SUCCESSED_MONEY', 420007, u'Дневник: получение награды (деньги)', LEXICON_GROUP.QUEST_HELP,
         u'Герой получает награду за помощь (деньги).',
         [V.INITIATOR, V.HERO, V.INITIATOR_POSITION, V.RECEIVER, V.RECEIVER_POSITION, V.COINS], u'hero#N +coins#G'),

        (u'QUEST_HELP_DIARY_INTRO', 420008, u'Дневник: Начало задания', LEXICON_GROUP.QUEST_HELP,
         u'Герой получил задание.',
         [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        (u'QUEST_HELP_JOURNAL_BEFORE_HELP', 420009, u'Журнал: Начало пути', LEXICON_GROUP.QUEST_HELP,
         u'Герой отправляется к целевому жителю.',
         [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),

        (u'QUEST_HELP_NAME', 420010, u'Название', LEXICON_GROUP.QUEST_HELP,
         u'Краткое название задания.',
         [V.RECEIVER_POSITION, V.RECEIVER, V.HERO, V.INITIATOR, V.INITIATOR_POSITION], None),
       ]
