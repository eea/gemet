# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-10 15:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("thesaurus", "0007_editable_concepts"),
    ]

    operations = [
        migrations.CreateModel(
            name="AuthorizedUser",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("username", models.CharField(max_length=100)),
            ],
        ),
    ]
