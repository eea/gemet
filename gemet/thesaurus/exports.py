import os

from django.conf import settings
from django.template.loader import render_to_string

from gemet.thesaurus import DEFAULT_LANGCODE, PUBLISHED
from gemet.thesaurus.models import Group, ForeignRelation, Language, Namespace
from gemet.thesaurus.models import Property, Relation, SuperGroup, Term, Theme


class ExportView(object):
    template_name = ''
    filename = ''

    @staticmethod
    def get_context():
        return {}


class BackboneView(ExportView):
    template_name = 'downloads/backbone.html'
    filename = 'gemet-backbone.html'

    @staticmethod
    def get_context():
        relations = (
            Relation.published.filter(
                property_type__label__in=['Theme', 'Group'],
            ).values(
                'source__code', 'property_type__label', 'target__code',
            )
        )
        return {"relations": relations}


class BackboneRDFView(ExportView):
    template_name = 'downloads/backbone.rdf'
    filename = 'gemet-backbone.rdf'

    @staticmethod
    def get_context():
        supergroup_uri = Namespace.objects.get(heading='Super groups').type_url
        supergroups = SuperGroup.published.values('code')

        group_uri = Namespace.objects.get(heading='Groups').type_url
        # TODO: find a way to alias foreign key attributes
        groups = (Group.published
                  .filter(source_relations__property_type__name='broader')
                  .values('source_relations__target__code', 'code'))

        theme_uri = Namespace.objects.get(heading='Themes').type_url
        themes = Theme.published.values('code')

        relations = {}
        concepts = Term.published.values('id', 'code')

        for concept in concepts:
            relations.update({
                concept['code']: (
                    Relation.published
                    .filter(source_id=concept['id'],
                            property_type__name__in=['theme', 'group'])
                    .values('target__code',
                            'property_type__name')
                )
            })
        return {
            'supergroup_uri': supergroup_uri,
            'supergroups': supergroups,
            'group_uri': group_uri,
            'groups': groups,
            'theme_uri': theme_uri,
            'themes': themes,
            'concept_relations': relations,
        }


class DefinitionsView(ExportView):
    template_name = 'downloads/definitions.html'
    filename = 'gemet-definitions.html'

    @staticmethod
    def get_context():
        concepts = []
        for term in Term.published.all():
            concept_properties = (
                term.properties
                .filter(
                    language__code=DEFAULT_LANGCODE,
                    name__in=['prefLabel', 'scopeNote', 'definition',
                              'notation'],
                )
                .values('name', 'value')
            )
            if concept_properties:
                concept = {'code': term.code}
                for c in concept_properties:
                    concept.update({c['name']: c['value']})
                concepts.append(concept)

        return {"concepts": concepts}


class GemetGroupsView(ExportView):
    template_name = 'downloads/gemet-groups.html'
    filename = 'gemet-groups.html'
    translate = {
        'Super groups': 'SuperGroup',
        'Groups': 'Group',
        'Themes': 'Theme',
    }

    @staticmethod
    def get_context():
        supergroups = (
            Property.published
            .filter(
                name='prefLabel',
                concept__namespace__heading='Super groups',
                language__code=DEFAULT_LANGCODE,
            )
            .values('concept__code', 'value')
        )

        relations = (
            Relation.published
            .filter(
                target_id__in=SuperGroup.published.values_list('id', flat=True),
                property_type__label='broader term',
            )
            .values('target__code', 'source_id')
        )

        groups = []
        for relation in relations:
            source = (
                Property.published
                .filter(
                    concept_id=relation['source_id'],
                    name='prefLabel',
                    language__code=DEFAULT_LANGCODE,
                )
                .values('concept__code', 'value')
                .first()
            )
            groups.append({
                'source_code': source['concept__code'],
                'source_label': source['value'],
                'target_code': relation['target__code'],
            })

        themes = (
            Property.published
            .filter(
                name='prefLabel',
                language__code=DEFAULT_LANGCODE,
                concept__namespace__heading='Themes',
            )
            .values('concept__code', 'value')
        )

        return {
            'supergroups': supergroups,
            'supergroup_type': GemetGroupsView.translate.get('Super groups'),
            'groups': groups,
            'group_type': GemetGroupsView.translate.get('Groups'),
            'themes': themes,
            'theme_type': GemetGroupsView.translate.get('Themes'),
        }


def get_relations():
    return Relation.published.filter(
        source__namespace__heading='Concepts',
        target__namespace__heading='Concepts',
        property_type__name__in=['broader', 'narrower', 'related']
    ).values(
        'source__code',
        'target__code',
        'property_type__name',
    )


def get_foreign_relations():
    return (
        ForeignRelation.published
        .filter(
            concept__in=Term.published.all(),
            property_type__name__in=[
                'broadMatch', 'closeMatch', 'exactMatch', 'narrowMatch',
                'relatedMatch',
            ]
        )
    )


class GemetRelationsView(ExportView):
    template_name = 'downloads/gemet-relations.html'
    filename = 'gemet-relations.html'

    @staticmethod
    def get_context():
        relations = list(get_relations())
        foreign_relations = get_foreign_relations()

        foreign_relations = (
            foreign_relations
            .filter(
                show_in_html=True,
            ).order_by(
                'label',
            ).values(
                'concept__code', 'property_type__name', 'uri',
            )
        )
        for relation in foreign_relations:
            d = {'source__code': relation['concept__code'],
                 'property_type__name': relation['property_type__name'],
                 'target__code': relation['uri']}
            relations.append(d)

        return {
            'foreign_relations': foreign_relations,
            'relations': sorted(relations, key=lambda x: x['source__code']),
        }


class Skoscore(ExportView):
    template_name = 'downloads/skoscore.rdf'
    filename = 'gemet-skoscore.rdf'

    @staticmethod
    def get_context():
        relations = get_relations()
        foreign_relations = get_foreign_relations()
        concept_relations = {}

        foreign_relations = (
            foreign_relations
            .order_by('label',)
            .values('concept__code', 'property_type__name', 'uri',)
        )
        for r in relations:
            source_code = r['source__code']
            name = r['property_type__name']
            target_code = (
                ('' if 'Match' in name else 'concept/') +
                r['target__code']
            )
            concept_relations.setdefault(source_code, []).append(
                {'target__code': target_code, 'property_type__name': name}
            )

        for r in foreign_relations:
            source_code = r['concept__code']
            name = r['property_type__name']
            target_code = r['uri']
            concept_relations.setdefault(source_code, []).append({
                'target__code': target_code,
                'property_type__name': name,
            })

        return {'concept_relations': concept_relations}


class GemetThesaurus(ExportView):
    template_name = 'downloads/gemetThesaurus.xml'
    filename = 'gemetThesaurus.rdf'


class DefinitionsByLanguage(ExportView):
    template_name = 'downloads/language_definitions.rdf'
    filename = 'gemet-definitions.rdf'

    @staticmethod
    def get_context(language):
        definitions = (
            Property.published
            .filter(
                concept__status=PUBLISHED,
                concept__namespace__heading=Term.NAMESPACE,
                language_id=language,
                name__in=['definition', 'prefLabel'],
            )
            .values('concept__code', 'name', 'value')
            .order_by('concept__code', '-name')
        )

        return {'definitions': definitions}


class GroupsByLanguage(ExportView):
    template_name = 'downloads/language_groups.rdf'
    filename = 'gemet-groups.rdf'

    @staticmethod
    def get_context(language):
        context = {}
        for heading in ['Super groups', 'Groups', 'Themes']:
            context.update({
                heading.replace(' ', '_'): (
                    Property.objects
                    .filter(
                        concept__namespace__heading=heading,
                        language_id=language,
                        name='prefLabel',
                    )
                    .values(
                        'concept__code',
                        'value',
                    )
                )
            })
        return context


EXPORT_VIEWS = [
    BackboneView,
    BackboneRDFView,
    DefinitionsView,
    GemetGroupsView,
    GemetRelationsView,
    Skoscore,
    GemetThesaurus,
]

TRANSLATABLE_EXPORT_VIEWS = [
    DefinitionsByLanguage,
    GroupsByLanguage,
]


def create_export_files(version):
    version_root = os.path.join(settings.EXPORTS_ROOT, version.identifier)
    os.makedirs(version_root)

    for view in EXPORT_VIEWS:
        location = os.path.join(version_root, view.filename)
        with open(location, 'w') as f:
            content = render_to_string(view.template_name, view.get_context())
            f.write(content.encode('utf-8'))

    languages = Language.objects.order_by('name').values_list('code', flat=True)
    for language in languages:
        language_root = os.path.join(version_root, language)
        os.makedirs(language_root)

    for view in TRANSLATABLE_EXPORT_VIEWS:
        for language in languages:
            location = os.path.join(version_root, language, view.filename)

            with open(location, 'w') as f:
                content = render_to_string(view.template_name,
                                           view.get_context(language))
                f.write(content.encode('utf-8'))
