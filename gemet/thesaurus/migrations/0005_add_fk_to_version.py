# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-03 14:53
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    Version = apps.get_model("thesaurus", "Version")
    Concept = apps.get_model("thesaurus", "Concept")
    Property = apps.get_model("thesaurus", "Property")
    Relation = apps.get_model("thesaurus", "Relation")
    ForeignRelation = apps.get_model("thesaurus", "ForeignRelation")
    db_alias = schema_editor.connection.alias
    version = Version.objects.using(db_alias).filter(is_current=True).first()
    Concept.objects.using(db_alias).all().update(version_added=version)
    Property.objects.using(db_alias).all().update(version_added=version)
    Relation.objects.using(db_alias).all().update(version_added=version)
    ForeignRelation.objects.using(db_alias).all().update(version_added=version)


def reverse_func(apps, schema_editor):
    # No need to change `version_added` back to NULL
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("thesaurus", "0004_version"),
    ]

    operations = [
        migrations.AddField(
            model_name="concept",
            name="version_added",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="thesaurus.Version"
            ),
        ),
        migrations.AddField(
            model_name="foreignrelation",
            name="version_added",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="thesaurus.Version"
            ),
        ),
        migrations.AddField(
            model_name="property",
            name="version_added",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="thesaurus.Version"
            ),
        ),
        migrations.AddField(
            model_name="relation",
            name="version_added",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="thesaurus.Version"
            ),
        ),
        migrations.RunPython(forwards_func, reverse_func),
    ]
