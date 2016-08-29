
if (!window.pgf) {
    pgf = {};
}

if (!pgf.game) {
    pgf.game = {};
}

pgf.game.constants = {

    ACTOR_TYPE: {{actor_type|safe}},

    GENDER_TO_TEXT: {{gender_to_text|safe}},
    GENDER_TO_STR: {{gender_to_str|safe}},

    PERSON_TYPE_TO_TEXT: {{person_type_to_text|safe}},

    RACE_TO_TEXT: {{race_to_text|safe}},
    RACE_TO_STR: {{race_to_str|safe}},

    GAME_STATE: {{game_state|safe}},
};

pgf.game.constants.ARTIFACT_TYPE = {
    {% for type in ARTIFACT_TYPE.records %}
    "{{ type.name }}": {
        "id": {{type.value}},
        "name": "{{type.text}}"
    }{%- if not loop.last -%},{%- endif -%}
    {% endfor %}
};

pgf.game.constants.ARTIFACT_RARITY = {
    {% for record in ARTIFACT_RARITY.records %}
    "{{record.name}}": {
        "id": {{record.value}},
        "name": "{{record.text}}"
    }{%- if not loop.last -%},{%- endif -%}
    {% endfor %}
};

pgf.game.constants.CARD_RARITY = {
    {% for record in CARD_RARITY.records %}
    "{{record.value}}": {
        "name": "{{record.name}}",
        "text": "{{record.text}}"
    }{%- if not loop.last -%},{%- endif -%}
    {% endfor %}
};

pgf.game.constants.CARD_TYPE = {
    {% for card_type, effect in CARDS_EFFECTS.iteritems() %}
    "{{card_type.value}}": {
        "text": "{{card_type.text}}",
        "description": "{{effect.DESCRIPTION}}"
    }{%- if not loop.last -%},{%- endif -%}
    {% endfor %}
};

pgf.game.constants.NO_EFFECT_ID = {{NO_EFFECT.value}};

pgf.game.constants.EFFECTS = {
    {% for effect in EFFECTS.values() %}
    "{{effect.TYPE.value}}": {
        "name": "{{effect.TYPE.text}}",
        "description": "{{effect.DESCRIPTION}}"
    }{%- if not loop.last -%},{%- endif -%}
    {% endfor %}
};

pgf.game.constants.abilities = {

    {% for ability_type in ABILITY_TYPE.records %}

    "{{ ability_type.value }}": {
        "type": "{{ ability_type.value }}",
        "name": "{{ ability_type.text }}",
        "description": "{{ ability_type.description }}",
        "cost": {{ ability_type.cost }}
    }{%- if not loop.last -%},{%- endif -%}

    {% endfor %}

};

pgf.game.constants.linguistics_formatters = {

    {% for key, text in LINGUISTICS_FORMATTERS.iteritems() %}

    "{{key}}": "{{text|replace("\"", "'")|safe}}"{% if not loop.last %},{% endif %}

    {% endfor %}

};


pgf.game.constants.sprites = {

    {% for sprite in SPRITES.records %}

    "{{ sprite.value }}": {
        "x": "{{ sprite.x }}",
        "y": "{{ sprite.y }}"
    },

    {% endfor %}

    "{{SPRITES.CELL_HIGHLIGHTING.name}}": "{{SPRITES.CELL_HIGHLIGHTING.value}}",
    "{{SPRITES.SELECT_LAND.name}}": "{{SPRITES.SELECT_LAND.value}}"

}

pgf.game.constants.tilesets = {

    main: {
        TILE_SIZE: {{CELL_SIZE}},
        W: {{CELL_SIZE}},
        H: {{CELL_SIZE}},
        SRC: "/game/images/map.png",
        sprites: jQuery.extend(true, {}, pgf.game.constants.sprites)
    },

    alternative: {
        TILE_SIZE: {{CELL_SIZE}},
        W: {{CELL_SIZE}},
        H: {{CELL_SIZE}},
        SRC: "/game/images/map_alternative.png",
        sprites: jQuery.extend(true, {}, pgf.game.constants.sprites)
    },

    winter: {
        TILE_SIZE: {{CELL_SIZE}},
        W: {{CELL_SIZE}},
        H: {{CELL_SIZE}},
        SRC: "/game/images/map_winter.png",
        sprites: jQuery.extend(true, {}, pgf.game.constants.sprites)
    },

    large_pixel: {
        TILE_SIZE: {{CELL_SIZE}},
        W: {{CELL_SIZE}},
        H: {{CELL_SIZE}},
        SRC: "/game/images/map_large_pixel.png",
        sprites: jQuery.extend(true, {}, pgf.game.constants.sprites)
    }
};


for (var tilesetName in pgf.game.constants.tilesets) {
    var tileset = pgf.game.constants.tilesets[tilesetName];

    for (var spriteName in tileset.sprites) {
        var sprite = tileset.sprites[spriteName];

        if (typeof(sprite)=='string') continue;

        if (sprite.w == undefined) sprite.w = tileset.W;
        if (sprite.h == undefined) sprite.h = tileset.H;
        if (sprite.src == undefined) sprite.src = tileset.SRC;
    }
}
