# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-19 09:04
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("thesaurus", "0008_add_authorized_user_model"),
    ]

    operations = [
        migrations.RenameField(
            model_name="version",
            old_name="changed_note",
            new_name="change_note",
        ),
    ]
