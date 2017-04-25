# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-25 14:32
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('thesaurus', '0009_rename_change_note_field'),
    ]

    operations = [
        migrations.CreateModel(
            name='AsyncTask',
            fields=[
                ('task', models.CharField(max_length=32)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('status', models.CharField(choices=[('queued', b'Queued'), ('finished', b'Finished'), ('failed', b'Failed'), ('started', b'Started')], default='queued', max_length=10)),
                ('version', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='thesaurus.Version')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
