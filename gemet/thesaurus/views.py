from django.shortcuts import render
from gemet.thesaurus.models import Namespace, Property, Language


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
        concept__in=s.concept.relation_targets.filter(
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
