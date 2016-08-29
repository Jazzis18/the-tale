# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-16 13:55
from __future__ import unicode_literals

from django.db import migrations


def remove_specialization_removed_message(apps, schema_editor):
    Template = apps.get_model("linguistics", "Template")
    Template.objects.filter(key=260031).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('linguistics', '0016_remove_person_leave_place_message'),
    ]

    operations = [
        migrations.RunPython(
            remove_specialization_removed_message,
        ),
    ]
