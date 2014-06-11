from SimpleXMLRPCServer import SimpleXMLRPCDispatcher
from xmlrpclib import Fault

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.core.urlresolvers import reverse

from gemet.thesaurus.models import (
    Namespace,
    Language,
    Term,
    Theme,
    Group,
    SuperGroup,
    Property,
    Relation,
    PropertyType,
)
from gemet.thesaurus import DEFAULT_LANGCODE
from gemet.thesaurus.utils import search_queryset, regex_search

ENDPOINT_URI = 'http://www.eionet.europa.eu/gemet/'
dispatcher = SimpleXMLRPCDispatcher(allow_none=False, encoding=None)


class ApiView(View):

    def get(self, request):
        response = HttpResponse()
        response.write("<b>This is an XML-RPC Service.</b><br>")
        response.write("You need to invoke it using an XML-RPC Client!<br>")
        return response

    def post(self, request):
        response = HttpResponse(content_type='text/xml')
        response.write(dispatcher._marshaled_dispatch(request.body))
        return response

    @classmethod
    def as_view(cls, **initkwargs):
        return csrf_exempt(super(ApiView, cls).as_view(**initkwargs))


def split_concept_uri(concept_uri):
    if '/' in concept_uri:
        thesaurus_uri, concept_code = concept_uri.rsplit('/', 1)
        thesaurus_uri += '/'
    else:
        thesaurus_uri = concept_uri
        concept_code = None
    return thesaurus_uri, concept_code


def has_thesaurus_uri(thesaurus_uri):
    all_thesaurus = (
        ENDPOINT_URI + 'concept/',
        ENDPOINT_URI + 'theme/',
        ENDPOINT_URI + 'group/',
        ENDPOINT_URI + 'supergroup/',
    )
    return thesaurus_uri in all_thesaurus


def get_language(langcode):
    try:
        return Language.objects.get(pk=langcode)
    except Language.DoesNotExist:
        raise Fault(-1, 'Language not found: %s' % langcode)


def get_namespace(thesaurus_uri):
    try:
        return Namespace.objects.get(url=thesaurus_uri)
    except Namespace.DoesNotExist:
        raise Fault(-1, 'Thesaurus URI not found: %s' % thesaurus_uri)


def get_model(thesaurus_uri):
    thesaurus_to_model = {
        ENDPOINT_URI + 'concept/': Term,
        ENDPOINT_URI + 'theme/': Theme,
        ENDPOINT_URI + 'group/': Group,
        ENDPOINT_URI + 'supergroup/': SuperGroup,
    }

    return thesaurus_to_model.get(thesaurus_uri)


def get_reverse_name(heading):
    heading_to_urlname = {
        'Concepts': 'concept',
        'Themes': 'theme',
        'Groups': 'group',
        'Super groups': 'supergroup',
    }

    return heading_to_urlname.get(heading)


def get_concept_uri(view_name, concept_id, langcode):
    host = ENDPOINT_URI.split('/gemet/')[0]
    return host + reverse(view_name, kwargs={
        'langcode': langcode,
        'concept_id': concept_id,
    })


def get_concept_id(concept_uri):
    thesaurus_uri, concept_code = split_concept_uri(concept_uri)

    if not has_thesaurus_uri(thesaurus_uri):
        raise Fault(-1, 'Thesaurus URI not found: %s' % thesaurus_uri)

    model = get_model(thesaurus_uri)
    try:
        concept = model.objects.get(code=concept_code)
    except model.DoesNotExist:
        raise Fault(-1, 'Concept code not found: %s' % concept_code)

    return concept.id


def get_concept(thesaurus_uri, concept_id, langcode):
    reverse_name = get_reverse_name(
        Namespace.objects.get(url=thesaurus_uri).heading
    )

    names = {
        'prefLabel': 'preferredLabel',
        'definition': 'definition',
    }

    concept_properties = Property.objects.filter(
        concept_id=concept_id,
        language__code=langcode,
        name__in=['prefLabel', 'definition'],
    ).values_list('name', 'value')

    concept = {}
    for name, value in concept_properties:
        key = names[name]
        concept[key] = {
            'string': value,
            'language': langcode,
        }
    concept.update({
        'uri': get_concept_uri(reverse_name, concept_id, langcode),
        'thesaurus': thesaurus_uri,
    })

    return concept


def getTopmostConcepts(thesaurus_uri, langcode=DEFAULT_LANGCODE):
    get_language(langcode)
    ns = get_namespace(thesaurus_uri)
    model = get_model(thesaurus_uri)
    all_concepts = model.objects.values_list('id', flat=True)
    excluded_concepts = (
        Relation.objects
        .filter(property_type__name='narrower', target__namespace_id=ns.id)
        .exclude(source__namespace__heading='Super groups')
        .values_list('target_id', flat=True)
    )
    concepts_id = list(set(all_concepts) - set(excluded_concepts))

    concepts = []
    for concept_id in concepts_id:
        concept = get_concept(thesaurus_uri, concept_id, langcode)
        concepts.append(concept)

    return sorted(concepts,
                  key=lambda x: x['preferredLabel']['string'].lower())


def getAllConceptRelatives(concept_uri, target_namespace=None,
                           relation_uri=None):
    concept_id = get_concept_id(concept_uri)

    relations = Relation.objects.filter(source_id=concept_id)
    if relation_uri:
        relations = relations.filter(property_type__uri=relation_uri)
    if target_namespace:
        relations = relations.filter(
            target__namespace__url=target_namespace
        )
    relations = relations.values(
        'property_type__uri',
        'target_id',
        'target__namespace__heading',
    )
    relatives = []
    for relation in relations:
        target_id = relation['target_id']
        reverse_name = get_reverse_name(
            relation['target__namespace__heading']
        )
        relatives.append({
            'relation': relation['property_type__uri'],
            'target': get_concept_uri(reverse_name, target_id,
                                      DEFAULT_LANGCODE),
        })
    return relatives


def getRelatedConcepts(concept_uri, relation_uri, langcode=DEFAULT_LANGCODE):
    try:
        concept_id = get_concept_id(concept_uri)
    except Fault:
        return []

    related_concepts = Relation.objects.filter(
        source_id=concept_id,
        property_type__uri=relation_uri,
    ).values_list('target_id', flat=True)

    relatives = []
    thesaurus_uri, concept_code = split_concept_uri(concept_uri)
    for related_id in related_concepts:
        relatives.append(get_concept(thesaurus_uri, related_id, langcode))
    return relatives


def getConcept(concept_uri, langcode=DEFAULT_LANGCODE):
    get_language(langcode)
    concept_id = get_concept_id(concept_uri)

    thesaurus_uri, concept_code = split_concept_uri(concept_uri)
    return get_concept(thesaurus_uri, concept_id, langcode)


def hasConcept(concept_uri):
    try:
        get_concept_id(concept_uri)
    except Fault:
        return False
    return True


def hasRelation(concept_uri, relation_uri, object_uri):
    try:
        source_id = get_concept_id(concept_uri)
        target_id = get_concept_id(object_uri)
    except Fault:
        return False

    property_type_id = Relation.objects.filter(
        source_id=source_id,
        target_id=target_id,
    ).values_list('property_type_id', flat=True).first()

    return relation_uri == PropertyType.objects.get(pk=property_type_id).uri


def getAllTranslationsForConcept(concept_uri, property_uri):
    concept_id = get_concept_id(concept_uri)

    name = property_uri.rsplit('#', 1)[-1]

    translations_qs = Property.objects.filter(
        concept_id=concept_id,
        name=name,
    ).values_list('language', 'value')

    result = []
    for language, value in translations_qs:
        result.append({'language': language, 'string': value})
    return result


def getConceptsMatchingKeyword(keyword, searchmode, thesaurus_uri,
                               langcode=DEFAULT_LANGCODE):

    language = get_language(langcode)
    ns = get_namespace(thesaurus_uri)
    if not searchmode in range(5):
        raise Fault(-1, 'Invalid search mode. Possible values are 0 .. 4.')

    concepts = search_queryset(keyword, language, searchmode, ns.heading,
                               True)
    results = []
    for concept in concepts:
        results.append(get_concept(thesaurus_uri, concept['id'], langcode))

    return results


def getConceptsMatchingRegexByThesaurus(regex, thesaurus_uri,
                                        langcode=DEFAULT_LANGCODE):
    language = get_language(langcode)
    ns = get_namespace(thesaurus_uri)

    concepts = regex_search(regex, language, ns.heading)
    results = []
    for concept in concepts:
        results.append(get_concept(thesaurus_uri, concept['id'], langcode))

    return results


def getAvailableLanguages(concept_uri):
    concept_id = get_concept_id(concept_uri)

    languages = Property.objects.filter(
        concept_id=concept_id,
        name='prefLabel',
    ).values_list('language', flat=True)
    return [] or sorted(languages)


def getSupportedLanguages(thesaurus_uri):
    ns = get_namespace(thesaurus_uri)
    languages = Property.objects.filter(
        concept__namespace=ns,
    ).values_list('language', flat=True)

    return [] or sorted(set(languages))


def getAvailableThesauri():
    result = []
    for ns in Namespace.objects.all().values('url', 'heading', 'version'):
        result.append({
            'name': ns['heading'],
            'uri': ns['url'],
            'version': ns['version'],
        })
    return result


def fetchThemes(langcode=DEFAULT_LANGCODE):
    return getTopmostConcepts(ENDPOINT_URI + 'theme/', langcode)


def fetchGroups(langcode=DEFAULT_LANGCODE):
    return getTopmostConcepts(ENDPOINT_URI + 'group/', langcode)


dispatcher.register_introspection_functions()
dispatcher.register_function(getTopmostConcepts, 'getTopmostConcepts')
dispatcher.register_function(getAllConceptRelatives, 'getAllConceptRelatives')
dispatcher.register_function(getRelatedConcepts, 'getRelatedConcepts')
dispatcher.register_function(getConcept, 'getConcept')
dispatcher.register_function(hasConcept, 'hasConcept')
dispatcher.register_function(hasRelation, 'hasRelation')
dispatcher.register_function(getAllTranslationsForConcept,
                             'getAllTranslationsForConcept')
dispatcher.register_function(getConceptsMatchingKeyword,
                             'getConceptsMatchingKeyword')
dispatcher.register_function(getConceptsMatchingRegexByThesaurus,
                             'getConceptsMatchingRegexByThesaurus')
dispatcher.register_function(getAvailableLanguages, 'getAvailableLanguages')
dispatcher.register_function(getSupportedLanguages, 'getSupportedLanguages')
dispatcher.register_function(getAvailableThesauri, 'getAvailableThesauri')
dispatcher.register_function(fetchThemes, 'fetchThemes')
dispatcher.register_function(fetchGroups, 'fetchGroups')
dispatcher.register_multicall_functions()
