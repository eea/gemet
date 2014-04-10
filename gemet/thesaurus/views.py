from django.shortcuts import render
from gemet.thesaurus.models import (
    Namespace,
    Property,
    Language,
    Relation,
    ForeignRelation,
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
    concept_query = Property.objects.only('value').filter(
        concept__id=concept_id,
        language__code=langcode,
    )
    data_dict = {'id': concept_id}
    property_names = ['prefLabel', 'definition', 'scopeNote']
    data_dict.update(
        {p: concept_query.filter(name=p).first() for p in property_names})

    broader_concept_names = ['theme', 'group']
    broader_concepts = {c + 's': Property.objects.filter(
        concept__in=[r.target for r in Relation.objects.filter(
            source__id=concept_id,
            property_type__name=c)],
        name='prefLabel',
        language__code=langcode,
    )
        for c in broader_concept_names
    }
    data_dict.update(broader_concepts)

    foreign_relations = ForeignRelation.objects.filter(
        concept__id=concept_id,
        show_in_html=True,
    )
    translations = Property.objects.filter(
        concept__id=concept_id,
        name='prefLabel',
    )
    data_dict.update({
        'foreign_relations': foreign_relations,
        'translations': translations,
    })

    return render(request, 'concept.html', {
        'languages': languages,
        'concept': data_dict,
    })
