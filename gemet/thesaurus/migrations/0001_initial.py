# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Concept',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=10)),
                ('date_entered', models.DateTimeField(null=True, blank=True)),
                ('date_changed', models.DateTimeField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DefinitionSource',
            fields=[
                ('abbr', models.CharField(max_length=10, serialize=False, primary_key=True)),
                ('author', models.CharField(max_length=255, null=True)),
                ('title', models.CharField(max_length=255, null=True)),
                ('url', models.CharField(max_length=255, null=True)),
                ('publication', models.CharField(max_length=255, null=True)),
                ('place', models.CharField(max_length=255, null=True)),
                ('year', models.CharField(max_length=10, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ForeignRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uri', models.CharField(max_length=512)),
                ('label', models.CharField(max_length=100)),
                ('show_in_html', models.BooleanField(default=True)),
                ('concept', models.ForeignKey(related_name=b'foreign_relations', to='thesaurus.Concept')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('code', models.CharField(max_length=10, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('charset', models.CharField(max_length=100)),
                ('code_alt', models.CharField(max_length=3)),
                ('direction', models.CharField(max_length=1, choices=[(b'0', b'ltr'), (b'1', b'rtl')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Namespace',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.CharField(max_length=255)),
                ('heading', models.CharField(max_length=255)),
                ('version', models.CharField(max_length=255)),
                ('type_url', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Property',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('value', models.CharField(max_length=16000)),
                ('is_resource', models.BooleanField(default=False)),
                ('concept', models.ForeignKey(related_name=b'properties', to='thesaurus.Concept')),
                ('language', models.ForeignKey(related_name=b'properties', to='thesaurus.Language')),
            ],
            options={
                'verbose_name_plural': 'properties',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PropertyType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=40)),
                ('label', models.CharField(max_length=100)),
                ('uri', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Relation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('property_type', models.ForeignKey(to='thesaurus.PropertyType')),
                ('source', models.ForeignKey(related_name=b'source_relations', to='thesaurus.Concept')),
                ('target', models.ForeignKey(related_name=b'target_relations', to='thesaurus.Concept')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='foreignrelation',
            name='property_type',
            field=models.ForeignKey(to='thesaurus.PropertyType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='concept',
            name='namespace',
            field=models.ForeignKey(to='thesaurus.Namespace'),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('thesaurus.concept',),
        ),
        migrations.CreateModel(
            name='InspireTheme',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('thesaurus.concept',),
        ),
        migrations.CreateModel(
            name='SuperGroup',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('thesaurus.concept',),
        ),
        migrations.CreateModel(
            name='Term',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('thesaurus.concept',),
        ),
        migrations.CreateModel(
            name='Theme',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('thesaurus.concept',),
        ),
    ]
