# coding: utf-8

from django.contrib import admin

from the_tale.game.roads.models import Road, Waymark

class RoadAdmin(admin.ModelAdmin):
    list_display = ('id', 'exists', 'point_1', 'point_2', 'length')

    list_filter = ('point_1', 'point_2')

class WaymarkAdmin(admin.ModelAdmin):
    list_display = ('id', 'point_from', 'point_to', 'road', 'length')

    list_filter = ('point_from', 'point_to')

admin.site.register(Road, RoadAdmin)
admin.site.register(Waymark, WaymarkAdmin)
