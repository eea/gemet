# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-02 10:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('thesaurus', '0002_add_status_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='concept',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(0, b'pending'), (1, b'published'), (2, b'deleted'), (3, b'deleted pending')], default=0),
        ),
        migrations.AlterField(
            model_name='foreignrelation',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(0, b'pending'), (1, b'published'), (2, b'deleted'), (3, b'deleted pending')], default=0),
        ),
        migrations.AlterField(
            model_name='property',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(0, b'pending'), (1, b'published'), (2, b'deleted'), (3, b'deleted pending')], default=0),
        ),
        migrations.AlterField(
            model_name='relation',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(0, b'pending'), (1, b'published'), (2, b'deleted'), (3, b'deleted pending')], default=0),
        ),
    ]