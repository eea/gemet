# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2021-01-15 15:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


def forwards_func(apps, schema_editor):
    Concept = apps.get_model("thesaurus", "Concept")
    db_alias = schema_editor.connection.alias
    for concept in Concept.objects.using(db_alias).all():
        if concept.date_entered:
            Concept.objects.filter(pk=concept.pk).update(
                created_at=concept.date_entered
            )
        if concept.date_changed:
            Concept.objects.filter(pk=concept.pk).update(
                created_at=concept.date_changed
            )


def reverse_func(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("thesaurus", "0012_import"),
    ]

    operations = [
        migrations.AddField(
            model_name="concept",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="concept",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.RunPython(forwards_func, reverse_func),
        migrations.RemoveField(
            model_name="concept",
            name="date_changed",
        ),
        migrations.RemoveField(
            model_name="concept",
            name="date_entered",
        ),
    ]
