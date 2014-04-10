from django.shortcuts import render, get_object_or_404
from gemet.thesaurus.models import (
    Namespace,
    Property,
    Language,
    Concept,
)


def index(request):
    return render(request, 'index.html', {})


def themes_list(request):
    ns = Namespace.objects.get(heading='Themes')
    themes = Property.objects.filter(concept__namespace=ns, name='prefLabel')

    return render(request, 'themes_list.html', {'themes': themes})


def groups_list(request):
    languages = Language.objects.all()
    langcode = request.GET.get('langcode', 'en')
    ns = Namespace.objects.get(heading='Super Groups')
    supergroups = Property.objects.filter(
        concept__namespace=ns,
        language__code=langcode,
        name='prefLabel',
    )
    groups = {s.value: Property.objects.only('value').filter(
        concept__in=s.concept.target_relations.filter(
            property_type__name='broader',
        ),
        language__code=langcode,
        name='prefLabel',
    )
        for s in supergroups
    }

    return render(request, 'groups_list.html', {
        'languages': languages,
        'groups': groups,
    })


def concept(request, concept_id):
    languages = Language.objects.all()
    langcode = request.GET.get('langcode', 'en')

    concept = get_object_or_404(Concept, pk=concept_id)

    data_dict = {'id': concept_id}

    properties = dict(
        concept.properties
        .filter(
            language__code=langcode,
            name__in=['prefLabel', 'definition', 'scopeNote'],
        )
        .values_list('name', 'value')
    )
    data_dict.update(properties)

    broader_concept_names = ['theme', 'group']
    broader_concepts = {c + 's': Property.objects.filter(
        concept__in=concept.source_relations
        .filter(property_type__name=c)
        .values_list('target'),
        name='prefLabel',
        language__code=langcode,
    )
        for c in broader_concept_names
    }
    data_dict.update(broader_concepts)

    foreign_relations = concept.foreign_relations.filter(show_in_html=True)
    translations = concept.properties.filter(name='prefLabel')
    data_dict.update({
        'foreign_relations': foreign_relations,
        'translations': translations,
    })

    return render(request, 'concept.html', {
        'languages': languages,
        'concept': data_dict,
    })
