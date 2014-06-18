from SimpleXMLRPCServer import SimpleXMLRPCDispatcher
from xmlrpclib import Fault
from inspect import getargspec
from exceptions import ValueError
from json import JSONEncoder

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

    functions = {}

    @classmethod
    def register_function(cls, function, name):
        dispatcher.register_function(function, name)
        cls.functions.update({name: function})

    def dispatch(self, request, *args, **kwargs):
        self.method_name = kwargs.pop('method_name')
        return super(ApiView, self).dispatch(request, *args, **kwargs)

    @classmethod
    def as_view(cls, **initkwargs):
        return csrf_exempt(super(ApiView, cls).as_view(**initkwargs))


class ApiViewPOST(ApiView):

    def post(self, request):
        response = HttpResponse(content_type='text/xml')
        response.write(dispatcher._marshaled_dispatch(request.body))
        return response


class ApiViewGET(ApiView):

    def get(self, request):

        def has_get_param(name):
            return name in request.GET

        def get_param(name):
            if has_get_param(name):
                return request.GET.get(name)
            else:
                Fault(-1, 'Missing parameter: %s' % name)

        function = self.functions.get(self.method_name)
        response = HttpResponse(
            content_type='text/javascript' if (
                has_get_param('jsonp') and get_param('jsonp') == 'callback'
            )
            else 'application/json'
        )
        defaults = getargspec(function).defaults
        arguments = getargspec(function).args
        kwargs = {}

        if defaults:
            required_args = arguments[:-len(defaults)]
            args = map(get_param, required_args)
            optional_args = arguments[-len(defaults):]
            optional_args = filter(has_get_param, optional_args)
            for arg in optional_args:
                kwargs.update({arg: get_param(arg)})
        else:
            args = map(get_param, arguments)
        response.write(JSONEncoder().encode(function(*args, **kwargs)))
        return response


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


def getTopmostConcepts(thesaurus_uri, language=DEFAULT_LANGCODE):
    get_language(language)
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
        concept = get_concept(thesaurus_uri, concept_id, language)
        concepts.append(concept)

    return sorted(concepts,
                  key=lambda x: x['preferredLabel']['string'].lower())


def getAllConceptRelatives(concept_uri, target_thesaurus_uri=None,
                           relation_uri=None):
    concept_id = get_concept_id(concept_uri)

    relations = Relation.objects.filter(source_id=concept_id)
    if relation_uri:
        relations = relations.filter(property_type__uri=relation_uri)
    if target_thesaurus_uri:
        relations = relations.filter(
            target__namespace__url=target_thesaurus_uri
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


def getRelatedConcepts(concept_uri, relation_uri, language=DEFAULT_LANGCODE):
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
        relatives.append(get_concept(thesaurus_uri, related_id, language))
    return relatives


def getConcept(concept_uri, language=DEFAULT_LANGCODE):
    get_language(language)
    concept_id = get_concept_id(concept_uri)

    thesaurus_uri, concept_code = split_concept_uri(concept_uri)
    return get_concept(thesaurus_uri, concept_id, language)


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


def getConceptsMatchingKeyword(keyword, search_mode, thesaurus_uri,
                               language=DEFAULT_LANGCODE):

    language = get_language(language)
    ns = get_namespace(thesaurus_uri)
    try:
        search_mode = int(search_mode)
        if not search_mode in range(5):
            raise ValueError
    except ValueError:
        raise Fault(-1, 'Invalid search mode. Possible values are 0 .. 4.')

    concepts = search_queryset(keyword, language, search_mode, ns.heading,
                               True)
    results = []
    for concept in concepts:
        results.append(get_concept(thesaurus_uri, concept['id'], language.code))

    return results


def getConceptsMatchingRegexByThesaurus(regex, thesaurus_uri,
                                        language=DEFAULT_LANGCODE):
    language = get_language(language)
    ns = get_namespace(thesaurus_uri)

    concepts = regex_search(regex, language, ns.heading)
    results = []
    for concept in concepts:
        results.append(get_concept(thesaurus_uri, concept['id'], language.code))

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


def fetchThemes(language=DEFAULT_LANGCODE):
    return getTopmostConcepts(ENDPOINT_URI + 'theme/', language)


def fetchGroups(language=DEFAULT_LANGCODE):
    return getTopmostConcepts(ENDPOINT_URI + 'supergroup/', language)


dispatcher.register_introspection_functions()
ApiView.register_function(getTopmostConcepts, 'getTopmostConcepts')
ApiView.register_function(getAllConceptRelatives, 'getAllConceptRelatives')
ApiView.register_function(getRelatedConcepts, 'getRelatedConcepts')
ApiView.register_function(getConcept, 'getConcept')
ApiView.register_function(hasConcept, 'hasConcept')
ApiView.register_function(hasRelation, 'hasRelation')
ApiView.register_function(getAllTranslationsForConcept,
                          'getAllTranslationsForConcept')
ApiView.register_function(getConceptsMatchingKeyword,
                          'getConceptsMatchingKeyword')
ApiView.register_function(getConceptsMatchingRegexByThesaurus,
                          'getConceptsMatchingRegexByThesaurus')
ApiView.register_function(getAvailableLanguages, 'getAvailableLanguages')
ApiView.register_function(getSupportedLanguages, 'getSupportedLanguages')
ApiView.register_function(getAvailableThesauri, 'getAvailableThesauri')
ApiView.register_function(fetchThemes, 'fetchThemes')
ApiView.register_function(fetchGroups, 'fetchGroups')
dispatcher.register_multicall_functions()
