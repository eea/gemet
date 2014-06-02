from SimpleXMLRPCServer import SimpleXMLRPCDispatcher
from xmlrpclib import Fault

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.http import Http404

from models import (
    Namespace,
    Language,
    Concept,
    Term,
    Theme,
    Group,
    SuperGroup,
    Property,
    Relation,
    PropertyType,
)
from gemet.thesaurus import DEFAULT_LANGCODE
from gemet.thesaurus.utils import search_queryset

HOST = 'http://www.eionet.europa.eu/gemet/'
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

#=========helper functions ===========#


def split_concept_uri(concept_uri, get_only_thesaurus=True):
    if '/' in concept_uri:
        thesaurus_uri, concept_code = concept_uri.rsplit('/', 1)
        thesaurus_uri += '/'
    else:
        thesaurus_uri = concept_uri
        concept_code = None
    if get_only_thesaurus:
        return thesaurus_uri
    else:
        return thesaurus_uri, concept_code


def test_has_language(langcode):
    try:
        language = Language.objects.get(pk=langcode)
        return language
    except Language.DoesNotExist:
        raise Fault(-1, 'Language not found: %s' % langcode)


def has_thesaurus_uri(thesaurus_uri):
    all_thesaurus = (
        HOST + 'concept/',
        HOST + 'theme/',
        HOST + 'group/',
        HOST + 'supergroup/',
    )

    if thesaurus_uri in all_thesaurus:
        return True
    return False


def get_namespace(thesaurus_uri):
    try:
        ns = Namespace.objects.get(url=thesaurus_uri)
        return ns
    except Namespace.DoesNotExist:
        raise Fault(-1, 'Thesaurus URI not found: %s' % thesaurus_uri)


def get_model(thesaurus_uri):
    thesaurus_to_model = {
        HOST + 'concept/': Term,
        HOST + 'theme/': Theme,
        HOST + 'group/': Group,
        HOST + 'supergroup/': SuperGroup,
    }

    return(thesaurus_to_model.get(thesaurus_uri))


def get_reverse_name(heading):
    heading_to_urlname = {
        'Concepts': 'concept',
        'Themes': 'theme',
        'Groups': 'group',
        'Super groups': 'supergroup',
    }

    return heading_to_urlname[heading]


def get_concept_id(concept_uri):
    thesaurus_uri, concept_code = split_concept_uri(concept_uri, False)

    if has_thesaurus_uri(thesaurus_uri):
        model = get_model(thesaurus_uri)
        try:
            concept = model.objects.get(code=concept_code)
            return (True, concept.id)
        except model.DoesNotExist:
            return (False, 'Concept code not found: %s' % concept_code)
    else:
        return (False, 'Thesaurus URI not found: %s' % thesaurus_uri)


def get_concept(thesaurus_uri, concept_id, langcode):
    reverse_name = get_reverse_name(
        Namespace.objects.get(url=thesaurus_uri).heading
        )

    names = {
        'prefLabel': 'preferredLabel',
        'definition': 'definition'
    }

    concept_properties = Property.objects.filter(
        concept_id=concept_id,
        language__code=langcode,
        name__in=['prefLabel', 'definition']
        ).values('name', 'value')

    concept = {}
    for concept_property in concept_properties:
        concept.update(
            {names[concept_property['name']]: {
                'string': concept_property['value'],
                'language': langcode
                }
             })
    concept.update({
        'uri': HOST.split('/gemet/')[0] + reverse(reverse_name, kwargs={
            'langcode': langcode,
            'concept_id': concept_id
            }),
        'thesaurus': thesaurus_uri
        })

    return concept

#==============end of helper functions =================#


def getTopmostConcepts(thesaurus_uri, langcode=DEFAULT_LANGCODE):
    test_has_language(langcode)
    ns = get_namespace(thesaurus_uri)
    model = get_model(thesaurus_uri)
    concepts_id = model.objects.values_list('id', flat=True)

    concepts = []
    for concept_id in concepts_id:
        concept = get_concept(thesaurus_uri, concept_id, langcode)
        concepts.append(concept)

    return sorted(concepts,
                  key=lambda x: x['preferredLabel']['string'].lower())


def getAllConceptRelatives(concept_uri, target_namespace=None,
                           relation_uri=None):
    concept_id = get_concept_id(concept_uri)
    if concept_id[0]:

        relations = Relation.objects.filter(source_id=concept_id[1])
        if relation_uri:
            relations = relations.filter(property_type__uri=relation_uri)
        if target_namespace:
            relations = relations.filter(
                target__namespace__url=target_namespace
            )
        relations = relations.values(
            'property_type__uri',
            'target_id',
            'target__namespace__heading'
            )
        relatives = []
        for relation in relations:
            target_id = relation['target_id']
            reverse_name = get_reverse_name(
                relation['target__namespace__heading']
                )

            relatives.append({
                'relation': relation['property_type__uri'],
                'target': HOST.split('/gemet/')[0] + reverse(
                    reverse_name,
                    kwargs={
                        'langcode': DEFAULT_LANGCODE,
                        'concept_id': target_id
                    })
            })
        return relatives

    raise Fault(-1, concept_id[1])


def getRelatedConcepts(concept_uri, relation_uri, langcode=DEFAULT_LANGCODE):
    concept_id = get_concept_id(concept_uri)
    if concept_id[0]:
        related_concepts = Relation.objects.filter(
            source_id=concept_id[1],
            property_type__uri=relation_uri,
        ).values_list('target_id', flat=True)

        relatives = []
        thesaurus_uri = split_concept_uri(concept_uri)
        for related_id in related_concepts:
            relatives.append(get_concept(thesaurus_uri, related_id, langcode))
        return relatives

    return []


def getConcept(concept_uri, langcode=DEFAULT_LANGCODE):
    test_has_language(langcode)
    concept_id = get_concept_id(concept_uri)
    if concept_id[0]:
        thesaurus_uri = split_concept_uri(concept_uri)
        return get_concept(thesaurus_uri, concept_id[1], langcode)

    raise Fault(-1, concept_id[1])


def hasConcept(concept_uri):
    concept_id = get_concept_id(concept_uri)
    if not concept_id or not concept_id[0]:
        return False
    return True


def hasRelation(concept_uri, relation_uri, object_uri):

    concept_id = get_concept_id(concept_uri)
    if not concept_id[0]:
        return False

    object_id = get_concept_id(object_uri)
    if not object_id[0]:
        return False

    property_type_id = Relation.objects.filter(
        source_id=concept_id[1],
        target_id=object_id[1],
    ).values_list('property_type_id', flat=True).first()

    return relation_uri == PropertyType.objects.get(pk=property_type_id).uri


def getAllTranslationsForConcept(concept_uri, property_uri):
    concept_id = get_concept_id(concept_uri)
    if concept_id[0]:
        name = property_uri.rsplit('#', 1)[-1]

        result = []
        for p in Property.objects.filter(
            concept_id=concept_id[1],
            name=name,
        ).values('language', 'value'):
            result.append({
                'language': p['language'],
                'string': p['value']
            })
        return result

    raise Fault(-1, concept_id[1])


def getConceptsMatchingKeyword(keyword, searchmode, thesaurus_uri,
                               langcode=DEFAULT_LANGCODE):

    language = test_has_language(langcode)
    ns = get_namespace(thesaurus_uri)
    if searchmode in [0,1,2,3,4]:
        concepts = search_queryset(keyword, language, searchmode, ns.heading,
                                   True)
        results = []
        for concept in concepts:
            results.append(get_concept(thesaurus_uri, concept['id'], langcode))

        return results
    else:
        raise Fault(-1, 'Invalid search mode. Possible values are 0 .. 4.')


def getConceptsMatchingRegexByThesaurus(regex, thesaurus_uri,
                                        langcode=DEFAULT_LANGCODE):
    pass


def getAvailableLanguages(concept_uri):
    concept_id = get_concept_id(concept_uri)
    if concept_id[0]:
        languages = Property.objects.filter(
            concept_id=concept_id[1],
            name='prefLabel',
            ).values_list('language', flat=True)
        return [] or sorted(languages)

    raise Fault(-1, concept_id[1])


def getSupportedLanguages(thesaurus_uri):
    ns = get_namespace(thesaurus_uri)
    languages = Property.objects.filter(
        concept__namespace__url=thesaurus_uri,
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
    return getTopmostConcepts(HOST + 'theme/', langcode)


def fetchGroups(langcode=DEFAULT_LANGCODE):
    return getTopmostConcepts(HOST + 'group/', langcode)

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
dispatcher.register_function(getAvailableLanguages, 'getAvailableLanguages')
dispatcher.register_function(getSupportedLanguages, 'getSupportedLanguages')
dispatcher.register_function(getAvailableThesauri, 'getAvailableThesauri')
dispatcher.register_function(fetchThemes, 'fetchThemes')
dispatcher.register_function(fetchGroups, 'fetchGroups')
dispatcher.register_multicall_functions()
