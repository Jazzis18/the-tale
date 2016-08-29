# coding: utf-8

from rels import Column
from rels.django import DjangoEnum

from the_tale.game.cards import forms


class RARITY(DjangoEnum):
    priority = Column()

    records = ( ('COMMON', 0, u'обычная карта', 3**4),
                ('UNCOMMON', 1, u'необычная карта', 3**3),
                ('RARE', 2, u'редкая карта', 3**2),
                ('EPIC', 3, u'эпическая карта', 3**1),
                ('LEGENDARY', 4, u'легендарная карта', 3**0) )

class AVAILABILITY(DjangoEnum):
    records = ( ('FOR_ALL', 0, u'для всех'),
                ('FOR_PREMIUMS', 1, u'только для подписчиков') )


class CARDS_COMBINING_STATUS(DjangoEnum):
    records = ( ('ALLOWED', 0, u'Объединение разрешено'),
                ('NOT_ENOUGH_CARDS', 1, u'Не хватает карт'),
                ('TO_MANY_CARDS', 2, u'Слишком много карт'),
                ('EQUAL_RARITY_REQUIRED', 3, u'Карты должны быть одной редкости'),
                ('LEGENDARY_X3_DISALLOWED', 4, u'Нельзя объединять 3 легендарных карты'),
                ('HAS_NO_CARDS', 5, u'У героя нет таких карт') )



class CARD_TYPE(DjangoEnum):
    availability = Column(unique=False)
    rarity = Column(unique=False)
    form = Column(unique=False, primary=False, single_type=False)
    in_game = Column(unique=False, primary=False)

    records = ( ('LEVEL_UP', 1, u'озарение', AVAILABILITY.FOR_ALL, RARITY.LEGENDARY, forms.EmptyForm, True),

                ('ADD_BONUS_ENERGY_COMMON', 5, u'капля энергии', AVAILABILITY.FOR_ALL, RARITY.COMMON, forms.EmptyForm, True,),
                ('ADD_BONUS_ENERGY_UNCOMMON', 6, u'чаша Силы', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),
                ('ADD_BONUS_ENERGY_RARE', 7, u'магический вихрь', AVAILABILITY.FOR_ALL, RARITY.RARE, forms.EmptyForm, True,),
                ('ADD_BONUS_ENERGY_EPIC', 8, u'энергетический шторм', AVAILABILITY.FOR_ALL, RARITY.EPIC, forms.EmptyForm, True,),
                ('ADD_BONUS_ENERGY_LEGENDARY', 9, u'шквал Силы', AVAILABILITY.FOR_ALL, RARITY.LEGENDARY, forms.EmptyForm, True,),

                ('ADD_GOLD_COMMON', 10, u'горсть монет', AVAILABILITY.FOR_ALL, RARITY.COMMON, forms.EmptyForm, True,),
                ('ADD_GOLD_UNCOMMON', 11, u'увесистый кошель', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),
                ('ADD_GOLD_RARE', 12, u'сундучок на счастье', AVAILABILITY.FOR_ALL, RARITY.RARE, forms.EmptyForm, True,),

                ('CHANGE_HABIT_HONOR_PLUS_UNCOMMON', 13, u'умеренность', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),
                ('CHANGE_HABIT_HONOR_MINUS_UNCOMMON', 14, u'чревоугодие', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),
                ('CHANGE_HABIT_PEACEFULNESS_PLUS_UNCOMMON', 15, u'спокойствие', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),
                ('CHANGE_HABIT_PEACEFULNESS_MINUS_UNCOMMON', 16, u'вспыльчивость', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),

                ('CHANGE_HABIT_HONOR_PLUS_RARE', 17, u'верность', AVAILABILITY.FOR_ALL, RARITY.RARE, forms.EmptyForm, True,),
                ('CHANGE_HABIT_HONOR_MINUS_RARE', 18, u'блуд', AVAILABILITY.FOR_ALL, RARITY.RARE, forms.EmptyForm, True,),
                ('CHANGE_HABIT_PEACEFULNESS_PLUS_RARE', 19, u'дружелюбие', AVAILABILITY.FOR_ALL, RARITY.RARE, forms.EmptyForm, True,),
                ('CHANGE_HABIT_PEACEFULNESS_MINUS_RARE', 20, u'алчность', AVAILABILITY.FOR_ALL, RARITY.RARE, forms.EmptyForm, True,),

                ('CHANGE_HABIT_HONOR_PLUS_EPIC', 21, u'скромность', AVAILABILITY.FOR_ALL, RARITY.EPIC, forms.EmptyForm, True,),
                ('CHANGE_HABIT_HONOR_MINUS_EPIC', 22, u'тщеславие', AVAILABILITY.FOR_ALL, RARITY.EPIC, forms.EmptyForm, True,),
                ('CHANGE_HABIT_PEACEFULNESS_PLUS_EPIC', 23, u'сдержанность', AVAILABILITY.FOR_ALL, RARITY.EPIC, forms.EmptyForm, True,),
                ('CHANGE_HABIT_PEACEFULNESS_MINUS_EPIC', 24, u'гнев', AVAILABILITY.FOR_ALL, RARITY.EPIC, forms.EmptyForm, True,),

                ('CHANGE_HABIT_HONOR_PLUS_LEGENDARY', 25, u'смирение', AVAILABILITY.FOR_ALL, RARITY.LEGENDARY, forms.EmptyForm, True,),
                ('CHANGE_HABIT_HONOR_MINUS_LEGENDARY', 26, u'гордыня', AVAILABILITY.FOR_ALL, RARITY.LEGENDARY, forms.EmptyForm, True,),
                ('CHANGE_HABIT_PEACEFULNESS_PLUS_LEGENDARY', 27, u'миролюбие', AVAILABILITY.FOR_ALL, RARITY.LEGENDARY, forms.EmptyForm, True,),
                ('CHANGE_HABIT_PEACEFULNESS_MINUS_LEGENDARY', 28, u'ярость', AVAILABILITY.FOR_ALL, RARITY.LEGENDARY, forms.EmptyForm, True,),

                ('PREFERENCES_COOLDOWNS_RESET_MOB', 29, u'знание врага', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),
                ('PREFERENCES_COOLDOWNS_RESET_PLACE', 30, u'новая родина', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),
                ('PREFERENCES_COOLDOWNS_RESET_FRIEND', 31, u'новый соратник', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),
                ('PREFERENCES_COOLDOWNS_RESET_ENEMY', 32, u'новый противник', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),
                ('PREFERENCES_COOLDOWNS_RESET_ENERGY_REGENERATION', 33, u'прозрение', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),
                ('PREFERENCES_COOLDOWNS_RESET_EQUIPMEN_SLOT', 34, u'вкусы в экипировке', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),
                ('PREFERENCES_COOLDOWNS_RESET_RISK_LEVEL', 35, u'определение лихости', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),
                ('PREFERENCES_COOLDOWNS_RESET_FAVORITE_ITEM', 36, u'наскучившая вещь', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),
                ('PREFERENCES_COOLDOWNS_RESET_ARCHETYPE', 37, u'пересмотр стиля боя', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),

                ('PREFERENCES_COOLDOWNS_RESET_ALL', 38, u'пересмотр ценностей', AVAILABILITY.FOR_ALL, RARITY.RARE, forms.EmptyForm, True,),

                ('CHANGE_ABILITIES_CHOICES', 39, u'альтернатива', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),

                ('CHANGE_HERO_SPENDINGS_TO_INSTANT_HEAL', 40, u'странный зуд', AVAILABILITY.FOR_ALL, RARITY.COMMON, forms.EmptyForm, True,),
                ('CHANGE_HERO_SPENDINGS_TO_BUYING_ARTIFACT', 41, u'магазинный импульс', AVAILABILITY.FOR_ALL, RARITY.COMMON, forms.EmptyForm, True,),
                ('CHANGE_HERO_SPENDINGS_TO_SHARPENING_ARTIFACT', 42, u'стремление к совершенству', AVAILABILITY.FOR_ALL, RARITY.COMMON, forms.EmptyForm, True,),
                ('CHANGE_HERO_SPENDINGS_TO_EXPERIENCE', 43, u'тяга к знаниям', AVAILABILITY.FOR_ALL, RARITY.COMMON, forms.EmptyForm, True,),
                ('CHANGE_HERO_SPENDINGS_TO_REPAIRING_ARTIFACT', 44, u'забота об имуществе', AVAILABILITY.FOR_ALL, RARITY.COMMON, forms.EmptyForm, True,),

                ('REPAIR_RANDOM_ARTIFACT', 45, u'фея-мастерица', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),
                ('REPAIR_ALL_ARTIFACTS', 46, u'благословение Великого Творца', AVAILABILITY.FOR_ALL, RARITY.EPIC, forms.EmptyForm, True,),

                ('CANCEL_QUEST', 47, u'другие заботы', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),

                ('GET_ARTIFACT_COMMON', 48, u'внезапная находка', AVAILABILITY.FOR_ALL, RARITY.COMMON, forms.EmptyForm, True,),
                ('GET_ARTIFACT_UNCOMMON', 49, u'полезный подарок', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),
                ('GET_ARTIFACT_RARE', 50, u'редкое приобретение', AVAILABILITY.FOR_ALL, RARITY.RARE, forms.EmptyForm, True,),
                ('GET_ARTIFACT_EPIC', 51, u'дар Хранителя', AVAILABILITY.FOR_ALL, RARITY.EPIC, forms.EmptyForm, True,),

                ('INSTANT_MONSTER_KILL', 52, u'длань Смерти', AVAILABILITY.FOR_ALL, RARITY.COMMON, forms.EmptyForm, True,),

                ('KEEPERS_GOODS_COMMON', 53, u'неразменная монета', AVAILABILITY.FOR_PREMIUMS, RARITY.COMMON, forms.PlaceForm, True),
                ('KEEPERS_GOODS_UNCOMMON', 54, u'волшебный горшочек', AVAILABILITY.FOR_PREMIUMS, RARITY.UNCOMMON, forms.PlaceForm, True),
                ('KEEPERS_GOODS_RARE', 55, u'скатерть самобранка', AVAILABILITY.FOR_PREMIUMS, RARITY.RARE, forms.PlaceForm, True),
                ('KEEPERS_GOODS_EPIC', 56, u'несметные богатства', AVAILABILITY.FOR_PREMIUMS, RARITY.EPIC, forms.PlaceForm, True),
                ('KEEPERS_GOODS_LEGENDARY', 0, u'рог изобилия', AVAILABILITY.FOR_PREMIUMS, RARITY.LEGENDARY, forms.PlaceForm, True),

                ('REPAIR_BUILDING', 57, u'волшебный инструмент', AVAILABILITY.FOR_PREMIUMS, RARITY.EPIC, forms.BuildingForm, True),

                ('ADD_PERSON_POWER_POSITIVE_UNCOMMON', 58, u'удачный день', AVAILABILITY.FOR_PREMIUMS, RARITY.UNCOMMON, forms.PersonForm, True),
                ('ADD_PERSON_POWER_POSITIVE_RARE', 59, u'нежданная выгода', AVAILABILITY.FOR_PREMIUMS, RARITY.RARE, forms.PersonForm, True),
                ('ADD_PERSON_POWER_POSITIVE_EPIC', 60, u'удачная афера', AVAILABILITY.FOR_PREMIUMS, RARITY.EPIC, forms.PersonForm, True),
                ('ADD_PERSON_POWER_POSITIVE_LEGENDARY', 61, u'преступление века', AVAILABILITY.FOR_PREMIUMS, RARITY.LEGENDARY, forms.PersonForm, True),

                ('ADD_PLACE_POWER_POSITIVE_UNCOMMON', 62, u'погожие деньки', AVAILABILITY.FOR_PREMIUMS, RARITY.UNCOMMON, forms.PlaceForm, True),
                ('ADD_PLACE_POWER_POSITIVE_RARE', 63, u'торговый день', AVAILABILITY.FOR_PREMIUMS, RARITY.RARE, forms.PlaceForm, True),
                ('ADD_PLACE_POWER_POSITIVE_EPIC', 64, u'городской праздник', AVAILABILITY.FOR_PREMIUMS, RARITY.EPIC, forms.PlaceForm, True),
                ('ADD_PLACE_POWER_POSITIVE_LEGENDARY', 65, u'экономический рост', AVAILABILITY.FOR_PREMIUMS, RARITY.LEGENDARY, forms.PlaceForm, True),

                ('ADD_PLACE_POWER_NEGATIVE_UNCOMMON', 66, u'ужасная погода', AVAILABILITY.FOR_PREMIUMS, RARITY.UNCOMMON, forms.PlaceForm, True),
                ('ADD_PLACE_POWER_NEGATIVE_RARE', 67, u'запустение', AVAILABILITY.FOR_PREMIUMS, RARITY.RARE, forms.PlaceForm, True),
                ('ADD_PLACE_POWER_NEGATIVE_EPIC', 68, u'нашествие крыс', AVAILABILITY.FOR_PREMIUMS, RARITY.EPIC, forms.PlaceForm, True),
                ('ADD_PLACE_POWER_NEGATIVE_LEGENDARY', 69, u'экономический спад', AVAILABILITY.FOR_PREMIUMS, RARITY.LEGENDARY, forms.PlaceForm, True),

                ('MOST_COMMON_PLACES_UNCOMMON', 70, u'ошибка в архивах', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.PlaceForm, True),
                ('MOST_COMMON_PLACES_RARE', 71, u'фальшивые рекомендации', AVAILABILITY.FOR_ALL, RARITY.RARE, forms.PlaceForm, True),
                ('MOST_COMMON_PLACES_EPIC', 72, u'застолье в Совете', AVAILABILITY.FOR_ALL, RARITY.EPIC, forms.PlaceForm, True),
                ('MOST_COMMON_PLACES_LEGENDARY', 73, u'интриги', AVAILABILITY.FOR_ALL, RARITY.LEGENDARY, forms.PlaceForm, True),

                ('ADD_EXPERIENCE_COMMON', 74, u'удачная мысль', AVAILABILITY.FOR_ALL, RARITY.COMMON, forms.EmptyForm, True,),
                ('ADD_EXPERIENCE_UNCOMMON', 75, u'чистый разум', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),
                ('ADD_EXPERIENCE_RARE', 76, u'неожиданные осложнения', AVAILABILITY.FOR_ALL, RARITY.RARE, forms.EmptyForm, True,),
                ('ADD_EXPERIENCE_EPIC', 77, u'слово Гзанзара', AVAILABILITY.FOR_ALL, RARITY.EPIC, forms.EmptyForm, True,),

                ('ADD_POWER_COMMON', 78, u'новые обстоятельства', AVAILABILITY.FOR_PREMIUMS, RARITY.COMMON, forms.EmptyForm, True,),
                ('ADD_POWER_UNCOMMON', 79, u'специальная операция', AVAILABILITY.FOR_PREMIUMS, RARITY.UNCOMMON, forms.EmptyForm, True,),
                ('ADD_POWER_RARE', 80, u'слово Дабнглана', AVAILABILITY.FOR_PREMIUMS, RARITY.RARE, forms.EmptyForm, True,),
                ('ADD_POWER_EPIC', 81, u'благословение Дабнглана', AVAILABILITY.FOR_PREMIUMS, RARITY.EPIC, forms.EmptyForm, True,),

                ('SHORT_TELEPORT', 82, u'телепорт', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),
                ('LONG_TELEPORT', 83, u'ТАРДИС', AVAILABILITY.FOR_ALL, RARITY.RARE, forms.EmptyForm, True,),

                ('EXPERIENCE_TO_ENERGY_UNCOMMON', 84, u'амнезия', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, False,),
                ('EXPERIENCE_TO_ENERGY_RARE', 85, u'донор Силы', AVAILABILITY.FOR_ALL, RARITY.RARE, forms.EmptyForm, False,),
                ('EXPERIENCE_TO_ENERGY_EPIC', 86, u'взыскание долга', AVAILABILITY.FOR_ALL, RARITY.EPIC, forms.EmptyForm, False,),
                ('EXPERIENCE_TO_ENERGY_LEGENDARY', 87, u'ритуал Силы', AVAILABILITY.FOR_ALL, RARITY.LEGENDARY, forms.EmptyForm, False,),

                ('SHARP_RANDOM_ARTIFACT', 88, u'волшебное точило', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),
                ('SHARP_ALL_ARTIFACTS', 89, u'суть вещей', AVAILABILITY.FOR_ALL, RARITY.EPIC, forms.EmptyForm, True,),

                ('GET_COMPANION_COMMON', 90, u'обычный спутник', AVAILABILITY.FOR_ALL, RARITY.COMMON, forms.EmptyForm, True),
                ('GET_COMPANION_UNCOMMON', 91, u'необычный спутник', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True),
                ('GET_COMPANION_RARE', 92, u'редкий спутник', AVAILABILITY.FOR_ALL, RARITY.RARE, forms.EmptyForm, True),
                ('GET_COMPANION_EPIC', 93, u'эпический спутник', AVAILABILITY.FOR_ALL, RARITY.EPIC, forms.EmptyForm, True),
                ('GET_COMPANION_LEGENDARY', 94, u'легендарный спутник', AVAILABILITY.FOR_ALL, RARITY.LEGENDARY, forms.EmptyForm, True),

                ('PREFERENCES_COOLDOWNS_RESET_COMPANION_DEDICATION', 95, u'новый взгляд', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),
                ('PREFERENCES_COOLDOWNS_RESET_COMPANION_EMPATHY', 96, u'чуткость', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),

                ('ADD_EXPERIENCE_LEGENDARY', 97, u'благословение Гзанзара', AVAILABILITY.FOR_ALL, RARITY.LEGENDARY, forms.EmptyForm, True,),

                ('RESET_ABILITIES', 98, u'новый путь', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),

                ('RELEASE_COMPANION', 99, u'четыре стороны', AVAILABILITY.FOR_ALL, RARITY.COMMON, forms.EmptyForm, True,),

                ('HEAL_COMPANION_COMMON', 100, u'передышка', AVAILABILITY.FOR_ALL, RARITY.COMMON, forms.EmptyForm, True,),
                ('HEAL_COMPANION_UNCOMMON', 101, u'подорожник', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),
                ('HEAL_COMPANION_RARE', 102, u'священный мёд', AVAILABILITY.FOR_ALL, RARITY.RARE, forms.EmptyForm, True,),
                ('HEAL_COMPANION_EPIC', 103, u'молодильное яблоко', AVAILABILITY.FOR_ALL, RARITY.EPIC, forms.EmptyForm, True,),
                ('HEAL_COMPANION_LEGENDARY', 104, u'живая вода', AVAILABILITY.FOR_ALL, RARITY.LEGENDARY, forms.EmptyForm, True,),

                ('CHANGE_HERO_SPENDINGS_TO_HEAL_COMPANION', 105, u'забота о ближнем', AVAILABILITY.FOR_ALL, RARITY.COMMON, forms.EmptyForm, True,),

                ('INCREMENT_ARTIFACT_RARITY', 106, u'скрытый потенциал', AVAILABILITY.FOR_ALL, RARITY.LEGENDARY, forms.EmptyForm, True,),

                ('ADD_POWER_LEGENDARY', 107, u'туз в рукаве', AVAILABILITY.FOR_PREMIUMS, RARITY.LEGENDARY, forms.EmptyForm, True,),
                ('ADD_PERSON_POWER_POSITIVE_COMMON', 108, u'улыбка фортуны', AVAILABILITY.FOR_PREMIUMS, RARITY.COMMON, forms.PersonForm, True),

                ('ADD_PLACE_POWER_POSITIVE_COMMON', 109, u'выгодный контракт', AVAILABILITY.FOR_PREMIUMS, RARITY.COMMON, forms.PlaceForm, True),
                ('ADD_PLACE_POWER_NEGATIVE_COMMON', 110, u'сорванный контракт', AVAILABILITY.FOR_PREMIUMS, RARITY.COMMON, forms.PlaceForm, True),

                ('ADD_PERSON_POWER_NEGATIVE_COMMON', 111, u'гримаса фортуны', AVAILABILITY.FOR_PREMIUMS, RARITY.COMMON, forms.PersonForm, True),
                ('ADD_PERSON_POWER_NEGATIVE_UNCOMMON', 112, u'гадкий день', AVAILABILITY.FOR_PREMIUMS, RARITY.UNCOMMON, forms.PersonForm, True),
                ('ADD_PERSON_POWER_NEGATIVE_RARE', 113, u'нежданная беда', AVAILABILITY.FOR_PREMIUMS, RARITY.RARE, forms.PersonForm, True),
                ('ADD_PERSON_POWER_NEGATIVE_EPIC', 114, u'провальное мероприятие', AVAILABILITY.FOR_PREMIUMS, RARITY.EPIC, forms.PersonForm, True),
                ('ADD_PERSON_POWER_NEGATIVE_LEGENDARY', 115, u'чёрная полоса', AVAILABILITY.FOR_PREMIUMS, RARITY.LEGENDARY, forms.PersonForm, True),
                )
