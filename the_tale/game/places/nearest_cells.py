# coding: utf-8
import math

from the_tale.game.map import conf as map_conf

from the_tale.game.balance import constants as c

from . import storage

E = 0.01
GUARANTIED_RADIUS = math.sqrt(1+1)+E # guarantied raidius of places cells
SKIPPED_ANGLE = math.pi / 6

def dst(x, y, x2, y2):
    return math.sqrt((x-x2)**2 + (y-y2)**2)


def skip_one(x, y, current_place, checked_place):
    current_angle = math.atan2(y-current_place.y, x-current_place.x)
    checked_angle = math.atan2(y-checked_place.y, x-checked_place.x)
    return abs(current_angle - checked_angle) < SKIPPED_ANGLE


def get_availabled_places(x, y):

    places = []

    for checked_place in storage.places.all():
        can_be_taken = True
        checked_dst = dst(x, y, checked_place.x, checked_place.y)

        for other_place in storage.places.all():
            if checked_place.id == other_place.id:
                continue

            other_dst = dst(x, y, other_place.x, other_place.y)

            if skip_one(x, y, checked_place, other_place):
                if checked_dst > other_dst:
                    can_be_taken = False
                    break

        if can_be_taken:
            places.append((checked_dst, checked_place))

    return places


def update_nearest_cells():

    for place in storage.places.all():
        place.nearest_cells = []

    for x in xrange(0, map_conf.map_settings.WIDTH):
        for y in xrange(0, map_conf.map_settings.HEIGHT):
            nearest_place = None
            nearest_power = 0

            for cur_dst, place in get_availabled_places(x, y):

                if cur_dst > place.attrs.politic_radius:
                    continue

                if cur_dst < GUARANTIED_RADIUS:
                    place_power = c.PLACE_MAX_SIZE**2 + place.attrs.size
                else:
                    place_power = float(place.attrs.size) / (cur_dst**2)

                if nearest_power < place_power:
                    nearest_place = place
                    nearest_power = place_power

            if nearest_place:
                nearest_place.nearest_cells.append((x, y))

    storage.places.save_all()
