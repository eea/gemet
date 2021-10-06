from xmlrpc.client import Fault
from xmlrpc.server import SimpleXMLRPCDispatcher
from inspect import getargspec
import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.shortcuts import redirect

from gemet.thesaurus.models import Concept, Group, Language, InspireTheme
from gemet.thesaurus.models import Namespace, Property, Relation, SuperGroup
from gemet.thesaurus.models import Term, Theme
from gemet.thesaurus import DEFAULT_LANGCODE, NS_VIEW_MAPPING
from gemet.thesaurus.utils import search_queryset, regex_search

ENDPOINT_URI = 'http://www.eionet.europa.eu/gemet/'
ENDPOINT_URI_2 = 'http://inspire.ec.europa.eu/theme/'
dispatcher = SimpleXMLRPCDispatcher(allow_none=False, encoding=None)


class ApiView(View):

    functions = {}

    @classmethod
    def register_function(cls, function, name):
        dispatcher.register_function(function, name)
        cls.functions.update({name: function})

    def dispatch(self, request, *args, **kwargs):
        self.method_name = kwargs.pop('method_name', None)
        if request.method == 'GET' and not self.method_name:
            return redirect(
                'themes',
                permanent=True,
                langcode=DEFAULT_LANGCODE,
            )
        return super(ApiView, self).dispatch(request, *args, **kwargs)

    @classmethod
    def as_view(cls, **initkwargs):
        return csrf_exempt(super(ApiView, cls).as_view(**initkwargs))

    def post(self, request):
        response = HttpResponse(content_type='text/xml')
        response.write(dispatcher._marshaled_dispatch(request.body))
        return response

    def get(self, request):

        def has_get_param(name):
            return name in request.GET

        def get_param(name):
            if has_get_param(name):
                return request.GET.get(name)
            else:
                raise Fault(-1, 'Missing parameter: %s' % name)

        try:
            function = self.functions[self.method_name]
        except KeyError:
            raise Fault(-1, 'Invalid method name: %s' % self.method_name)
        response = HttpResponse(content_type='application/json')
        defaults = getargspec(function).defaults
        arguments = getargspec(function).args

        if defaults:
            required_args = arguments[:-len(defaults)]
            optional_args = filter(has_get_param, arguments[-len(defaults):])
            arguments = required_args + list(optional_args)

        kwargs = {arg: get_param(arg) for arg in arguments}
        d = json.dumps(function(**kwargs))
        try:
            jsonp = get_param('jsonp')
            if jsonp:
                response.write(jsonp + '(' + d + ')')
            else:
                response.write(d)
        except Fault:
            response.write(d)
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
        ENDPOINT_URI_2,
    )
    return thesaurus_uri in all_thesaurus


def has_language(langcode):
    if langcode not in Language.objects.values_list('code', flat=True):
        raise Fault(-1, 'Language not found: %s' % langcode)
    return True


def get_language(langcode):
    if has_language(langcode):
        return Language.objects.get(pk=langcode)


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
        ENDPOINT_URI_2: InspireTheme,
    }
    return thesaurus_to_model.get(thesaurus_uri)


def get_reverse_name(heading):
    return NS_VIEW_MAPPING.get(heading)


def get_concept_id(concept_uri):
    thesaurus_uri, concept_code = split_concept_uri(concept_uri)

    if not has_thesaurus_uri(thesaurus_uri):
        raise Fault(-1, 'Thesaurus URI not found: %s' % thesaurus_uri)

    model = get_model(thesaurus_uri)
    try:
        concept = model.published.get(code=concept_code)
    except model.DoesNotExist:
        raise Fault(-1, 'Concept code not found: %s' % concept_code)

    return concept.id


def get_concept(thesaurus_uri, concept_id, langcode):
    names = {
        'prefLabel': 'preferredLabel',
        'definition': 'definition',
    }
    concept = Concept.published.get(pk=concept_id)
    concept_properties = concept.properties.filter(
        language__code=langcode,
        name__in=['prefLabel', 'definition'],
    ).values_list('name', 'value')

    json_concept = {}
    for name, value in concept_properties:
        key = names[name]
        json_concept[key] = {
            'string': value,
            'language': langcode,
        }
    json_concept.update({
        'uri': thesaurus_uri + concept.code,
        'thesaurus': thesaurus_uri,
    })

    return json_concept


def getTopmostConcepts(thesaurus_uri, language=DEFAULT_LANGCODE):
    has_language(language)
    ns = get_namespace(thesaurus_uri)
    all_concepts = (
        Property.published.filter(
            language__code=language,
            concept__namespace=ns,
        ).values_list(
            'concept__id', flat=True,
        ).distinct()
    )

    excluded_concepts = (
        Relation.published
        .filter(property_type__name='narrower', target__namespace_id=ns.id)
        .exclude(source__namespace__heading='Super groups')
        .values_list('target_id', flat=True)
    )
    concepts_id = list(set(all_concepts) - set(excluded_concepts))

    concepts = []
    for concept_id in concepts_id:
        concept = get_concept(thesaurus_uri, concept_id, language)
        concepts.append(concept)
    if not all(['preferredLabel' in con for con in concepts]):
        return concepts
    return sorted(concepts,
                  key=lambda x: x['preferredLabel']['string'].lower())


def getAllConceptRelatives(concept_uri, target_thesaurus_uri=None,
                           relation_uri=None):
    concept_id = get_concept_id(concept_uri)

    relations = Relation.published.filter(source_id=concept_id,)
    if relation_uri:
        relations = relations.filter(property_type__uri=relation_uri,)
    if target_thesaurus_uri:
        relations = relations.filter(
            target__namespace__url=target_thesaurus_uri,
        )
    relations = relations.values(
        'property_type__uri',
        'target__code',
        'target__namespace__url',
    )
    relatives = []
    for relation in relations:
        relatives.append({
            'source': concept_uri,
            'relation': relation['property_type__uri'],
            'target':
            relation['target__namespace__url'] + relation['target__code'],
        })
    return relatives


def getRelatedConcepts(concept_uri, relation_uri, language=DEFAULT_LANGCODE):
    has_language(language)
    concept_id = get_concept_id(concept_uri)

    related_concepts = Relation.published.filter(
        source_id=concept_id,
        property_type__uri=relation_uri,
    ).values_list('target_id', flat=True)

    related_concepts = [
        r for r in related_concepts
        if (
            Concept.published.get(pk=r)
            .properties.filter(language__code=language)
            .count()
        ) > 0
    ]

    relatives = []
    thesaurus_uri, concept_code = split_concept_uri(concept_uri)
    for related_id in related_concepts:
        relatives.append(get_concept(thesaurus_uri, related_id, language))
    return relatives


def getConcept(concept_uri, language=DEFAULT_LANGCODE):
    has_language(language)
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

    property_type_uri = Relation.published.filter(
        source_id=source_id,
        target_id=target_id,
    ).values_list('property_type__uri', flat=True).first()

    return relation_uri == property_type_uri


def getAllTranslationsForConcept(concept_uri, property_uri):
    concept_id = get_concept_id(concept_uri)

    name = property_uri.rsplit('#', 1)[-1]

    translations_qs = Property.published.filter(
        concept_id=concept_id,
        name=name,
    ).values_list('language', 'value')

    result = []
    for language, value in translations_qs:
        result.append({'language': language, 'string': value})
    return result


def getConceptsMatchingKeyword(keyword, search_mode, thesaurus_uri='',
                               language=DEFAULT_LANGCODE):
    try:
        search_mode = int(search_mode)
        if search_mode not in range(5):
            raise ValueError
    except ValueError:
        raise Fault(-1, 'Invalid search mode. Possible values are 0 .. 4.')

    language = get_language(language)

    if thesaurus_uri:
        ns = get_namespace(thesaurus_uri)
        headings = [ns.heading]
    else:
        headings = Namespace.objects.values_list('heading', flat=True)

    concepts = search_queryset(keyword, language, search_mode, headings, True)
    results = []

    if thesaurus_uri:
        for concept in concepts:
            results.append(
                get_concept(thesaurus_uri, concept['id'], language.code)
            )
    else:
        for concept in concepts:
            results.append(get_concept(
                Concept.published.get(pk=concept['id']).namespace.url,
                concept['id'],
                language.code
            ))

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
    thesaurus_uri, _ = split_concept_uri(concept_uri)
    ns = get_namespace(thesaurus_uri)
    concept_id = get_concept_id(concept_uri)
    languages = Property.published.filter(
        concept_id=concept_id,
        concept__namespace=ns,
    ).values_list('language', flat=True).distinct()

    return [] or sorted(languages)


def getSupportedLanguages(thesaurus_uri):
    ns = get_namespace(thesaurus_uri)
    languages = Property.published.filter(
        concept__namespace=ns,
    ).values_list('language', flat=True).distinct()

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
    return getTopmostConcepts(ENDPOINT_URI + 'group/', language)


def fetchSuperGroups(language=DEFAULT_LANGCODE):
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
ApiView.register_function(fetchSuperGroups, 'fetchSuperGroups')
dispatcher.register_multicall_functions()
