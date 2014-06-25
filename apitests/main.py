from argparse import ArgumentParser
import json
from urllib import urlencode
import xmlrpclib
import unittest
import sys
import requests

from config import *


class ApiTester(object):
    namespace_url = 'http://www.eionet.europa.eu/gemet/'
    inspire_url = 'http://inspire.ec.europa.eu/theme/'

    def __init__(self, request_url='', local=False, get=False):
        self.request_url = request_url
        self.LOCAL_TEST = local
        self.GET_TEST = get

    def get_full_path(self, relative_path=''):
        return self.namespace_url + relative_path

    def request(self, method, *args):
        if self.GET_TEST:
            arg = iter(args)
            return self.doGetReq(method, **dict(zip(arg, arg)))
        return self.doXmlRpc(method, *args[1::2])

    def doGetReq(self, method, **kwargs):
        url = self.request_url + method + '?'
        url += urlencode(kwargs)
        result = requests.get(url)
        if result.ok:
            return json.loads(result.text)
        return "ERROR"

    def doXmlRpc(self, method, *args):
        server = xmlrpclib.ServerProxy(self.request_url, allow_none=True)
        return getattr(server, method)(*args)


class TestGetTopmostConcepts(unittest.TestCase):
    def test_terms(self):
        top_concepts = api_tester.request(
            'getTopmostConcepts',
            'thesaurus_uri', api_tester.get_full_path('concept/'),
            'language', 'en'
        )

        result = [top_concept['preferredLabel']['string']
                  for top_concept in top_concepts]

        self.assertEqual(result, TOPMOST_TERMS)

    def test_groups(self):
        top_groups = api_tester.request(
            'getTopmostConcepts',
            'thesaurus_uri', api_tester.get_full_path('group/'),
            'language', 'en'
        )

        result = [top_group['preferredLabel']['string']
                  for top_group in top_groups]

        self.assertEqual(result, TOPMOST_GROUPS)

    def test_themes(self):
        top_themes = api_tester.request(
            'getTopmostConcepts',
            'thesaurus_uri', api_tester.get_full_path('theme/'),
            'language', 'en'
        )

        result = [top_theme['preferredLabel']['string']
                  for top_theme in top_themes]
        self.assertEqual(result, TOPMOST_THEMES)

    def test_inspire(self):
        top_inspire = api_tester.request(
            'getTopmostConcepts',
            'thesaurus_uri', api_tester.inspire_url,
            'language', 'en'
        )
        result = [top_theme['preferredLabel']['string']
                  for top_theme in top_inspire]

        self.assertEqual(result, TOPMOST_INSPIRE)


class TestGetRelatedConcepts(unittest.TestCase):

    def test_no_concept(self):
        relatives = api_tester.request(
            'getRelatedConcepts',
            'concept_uri', api_tester.get_full_path('concept/99999999'),
            'relation_uri', 'http://www.w3.org/2004/02/skos/core#related'
        )

        self.assertEqual(relatives, [])

    def test_one_concept_english(self):
        relatives = api_tester.request(
            'getRelatedConcepts',
            'concept_uri', api_tester.get_full_path('concept/42'),
            'relation_uri', 'http://www.w3.org/2004/02/skos/core#related',
            'language', 'en'
        )
        result = [relative['preferredLabel']['string']
                  for relative in relatives]

        self.assertEqual(result, ['acid rain', 'soil acidification'])

    def test_one_concept_spanish(self):
        relatives = api_tester.request(
            'getRelatedConcepts',
            'concept_uri', api_tester.get_full_path('concept/42'),
            'relation_uri', 'http://www.w3.org/2004/02/skos/core#related',
            'language', 'es'
        )

        result = [relative['preferredLabel']['string']
                  for relative in relatives]

        self.assertEqual(result,
                         [u'lluvia \xe1cida', u'acidificaci\xf3n de suelo'])

    def test_no_language(self):
        if api_tester.GET_TEST:
            self.assertEqual('ERROR',
                             api_tester.request('getRelatedConcepts', *(
                                 api_tester.get_full_path('concept/42'),
                                 'http://www.w3.org/2004/02/skos/core#related',
                                 'no_language'
                             )))
        else:
            self.assertRaises(
                xmlrpclib.Fault,
                api_tester.request,
                'getRelatedConcepts',
                'concept_uri', api_tester.get_full_path('concept/42'),
                'relation_uri', 'http://www.w3.org/2004/02/skos/core#related',
                'language', 'no_language'
            )


class TestGetConcept(unittest.TestCase):

    def test_no_concept(self):
        concept_uri = api_tester.get_full_path('concept/999999999')
        language = 'en'
        if api_tester.GET_TEST:
            self.assertEqual('ERROR',
                             api_tester.request(
                                 'getConcept', *(concept_uri, language)
                             ))
        else:
            self.assertRaises(xmlrpclib.Fault, api_tester.request,
                              'getConcept', 'concept_uri', concept_uri,
                              'language', language)

    def test_one_concept_english(self):
        concept_uri = api_tester.get_full_path('concept/7970')
        language = 'en'
        result = api_tester.request('getConcept', 'concept_uri', concept_uri,
                                    'language', language)

        self.assertEqual(result["definition"]["language"], language)
        self.assertEqual(result["definition"]["string"],
                         "Travel in the space beyond the earth's atmosphere "
                         "performed for scientific research purposes.")
        self.assertEqual(result["preferredLabel"]["language"], language)
        self.assertEqual(result["preferredLabel"]["string"], "space travel")
        self.assertEqual(result['thesaurus'],
                         api_tester.get_full_path('concept/'))
        if not api_tester.LOCAL_TEST:
            self.assertEqual(result['uri'],
                             api_tester.get_full_path('concept/7970'))

    def test_one_concept_spanish(self):
        concept_uri = api_tester.get_full_path('concept/7970')
        language = 'es'
        result = api_tester.request('getConcept', 'concept_uri', concept_uri,
                                    'language', language)

        self.assertEqual(result["preferredLabel"]["language"], language)
        self.assertEqual(result["preferredLabel"]["string"], "viaje espacial")
        self.assertEqual(result['thesaurus'],
                         api_tester.get_full_path('concept/'))
        if not api_tester.LOCAL_TEST:
            self.assertEqual(result['uri'],
                             api_tester.get_full_path('concept/7970'))

    def test_no_language(self):
        concept_uri = api_tester.get_full_path('concept/7970')
        language = 'no_language'
        if api_tester.GET_TEST:
            self.assertEqual('ERROR',
                             api_tester.request(
                                 'getConcept', *(concept_uri, language)
                             ))
        else:
            self.assertRaises(xmlrpclib.Fault, api_tester.request,
                              'getConcept', 'concept_uri', concept_uri,
                              'language', language)


class TestHasConcept(unittest.TestCase):

    def test_concept_1(self):
        concept_uri = api_tester.get_full_path('concept/7970')

        self.assertEqual(True, api_tester.request(
            'hasConcept', 'concept_uri', concept_uri
        ))

    def test_concept_2(self):
        concept_uri = api_tester.get_full_path('theme/33')

        self.assertEqual(True, api_tester.request(
            'hasConcept', 'concept_uri', concept_uri
        ))

    def test_no_concept(self):
        concept_uri = api_tester.get_full_path('concept/99999999')

        self.assertEqual(False, api_tester.request(
            'hasConcept', 'concept_uri', concept_uri
        ))

    def test_bad_url(self):
        bad_uri = 'sdfughkdjfng BAD URI! dduidbnJsdfsj'

        self.assertEqual(False, api_tester.request(
            'hasConcept', 'concept_uri', bad_uri
        ))


class TestHasRelation(unittest.TestCase):

    def test_broader(self):
        relation = (
            'concept_uri', api_tester.get_full_path('concept/100'),
            'relation_uri', 'http://www.w3.org/2004/02/skos/core#broader',
            'object_uri', api_tester.get_full_path('concept/13292')
        )

        self.assertEqual(True, api_tester.request('hasRelation', *relation))

    def test_relation(self):
        relation = (
            'concept_uri', api_tester.get_full_path('concept/100'),
            'relation_uri', 'http://www.w3.org/2004/02/skos/core#narrower',
            'object_uri', api_tester.get_full_path('concept/661')
        )

        self.assertEqual(True, api_tester.request('hasRelation', *relation))

    def test_related(self):
        relation = (
            'concept_uri', api_tester.get_full_path('concept/42'),
            'relation_uri', 'http://www.w3.org/2004/02/skos/core#related',
            'object_uri', api_tester.get_full_path('concept/51')
        )

        self.assertEqual(True, api_tester.request('hasRelation', *relation))

    def test_theme(self):
        relation = (
            'concept_uri', api_tester.get_full_path('concept/100'),
            'relation_uri',
            api_tester.get_full_path('2004/06/gemet-schema.rdf#theme'),
            'object_uri', api_tester.get_full_path('theme/1')
        )

        self.assertEqual(True, api_tester.request('hasRelation', *relation))

    def test_groupMember(self):
        relation = (
            'concept_uri', api_tester.get_full_path('group/96'),
            'relation_uri',
            api_tester.get_full_path('2004/06/gemet-schema.rdf#groupMember'),
            'object_uri', api_tester.get_full_path('concept/21')
        )

        self.assertEqual(True, api_tester.request('hasRelation', *relation))

    def test_no_concept(self):
        relation = (
            'concept_uri', api_tester.get_full_path('concept/999999'),
            'relation_uri', 'http://www.w3.org/2004/02/skos/core#broader',
            'object_uri', api_tester.get_full_path('concept/100')
        )

        self.assertEqual(False, api_tester.request('hasRelation', *relation))

    def test_no_relation(self):
        relation = (
            'concept_uri', api_tester.get_full_path('concept/100'),
            'relation_uri', 'bad_relation',
            'object_uri', api_tester.get_full_path('concept/13292')
        )

        self.assertEqual(False, api_tester.request('hasRelation', *relation))


class TestGetAllTranslationsForConcept(unittest.TestCase):

    def test_getAllTranslationsForConcept(self):
        concept = {
            'uri': api_tester.get_full_path('concept/7970'),
            'properties': {
                'http://www.w3.org/2004/02/skos/core#prefLabel': {},
                'http://www.w3.org/2004/02/skos/core#definition': {},
            }
        }

        translations = {}
        for prop_uri, prop_values in concept['properties'].iteritems():
            result = api_tester.request('getAllTranslationsForConcept',
                                        'concept_uri', concept['uri'],
                                        'property_uri', prop_uri)

            for value in result:
                translations[value['language']] = unicode(value['string'])

        self.assertEqual(sorted(translations.items()),
                         ALL_TTRANSLATIONS_FOR_CONCEPT)


class TestGetConceptsMatchingKeyword(unittest.TestCase):

    def search(self, keyword, mode):
        result = api_tester.request(
            'getConceptsMatchingKeyword', 'keyword', keyword, 'search_mode',
            mode, 'thesaurus_uri', api_tester.get_full_path('concept/'),
            'language', 'en'
        )

        return set(concept['preferredLabel']['string']
                   for concept in result)

    def test_no_wildcard(self):
        result = self.search('air', 0)
        self.assertEqual(result, TEST_NO_WILDCARD)

    def test_suffix(self):
        result = self.search('air', 1)
        self.assertEqual(result, TEST_SUFFIX)

    def test_preffix(self):
        result = self.search('air', 2)
        self.assertEqual(result, TEST_PREFFIX)

    def test_suffix_preffix(self):
        result = self.search('air', 3)
        self.assertEqual(result, TEST_SUFFIX_PREFFIX)

    def test_match_exact_term(self):
        result = self.search('travel', 4)
        self.assertEqual(result, TEST_EXACT_TERM)

    def test_match_preffix_terms(self):
        result = self.search('trave', 4)
        self.assertEqual(result, TEST_PREFFIX_TERMS)

    def test_match_suffix_terms(self):
        result = self.search('ravel', 4)
        self.assertEqual(result, TEST_SUFFIX_TERMS)

    def test_no_match(self):
        result = self.search('xyzasdf', 4)
        self.assertEqual(result, TEST_NO_MATCH)

    def test_no_match_regex(self):
        result = self.search('^air', 0)
        self.assertEqual(result, TEST_NO_MATCH_REGEX)

    def test_quote(self):
        result = self.search("'", 3)
        self.assertEqual(result, TEST_QUOTE)


class TestGetAvailableLanguages(unittest.TestCase):

    def test_getAvailableLanguages(self):
        result = api_tester.request('getAvailableLanguages', 'concept_uri',
                                    api_tester.get_full_path('concept/7970'))

        self.assertEqual(sorted(result), TEST_AVAILABLE_LANGUAGES)


class TestGetSupportedLanguages(unittest.TestCase):

    def test_getSupportedLanguages(self):
        result = api_tester.request('getSupportedLanguages', 'thesaurus_uri',
                                    api_tester.get_full_path('concept/'))

        if api_tester.LOCAL_TEST:
            self.assertEqual(sorted(result), sorted(TEST_SUPPORTED_LANGUAGES))
        else:
            self.assertEqual(sorted(result), sorted(
                TEST_SUPPORTED_LANGUAGES + TEST_EXTRA_LANGUAGES))


class TestGetAvailableThesauri(unittest.TestCase):
    def test_getSupportedLanguages(self):
        result = api_tester.request('getAvailableThesauri')
        self.assertEqual(result, THESAURI)


class TestFetchThemes(unittest.TestCase):

    def test_fetchThemes_english(self):
        language = 'en'
        result = api_tester.request('fetchThemes', 'language', language)

        self.assertEqual([r['preferredLabel'] for r in result],
                         THEMES_PREF_LABEL)
        if not api_tester.LOCAL_TEST:
            self.assertEqual([r['uri'] for r in result], THEMES_URI)
        self.assertEqual([r['thesaurus'] for r in result], THEMES_THESAURUS)

    def test_fetchThemes_spanish(self):
        language = 'es'
        result = api_tester.request('fetchThemes', 'language', language)

        self.assertEqual(
            'turismo',
            sorted([r['preferredLabel']['string'] for r in result])[-1]
        )
        if not api_tester.LOCAL_TEST:
            self.assertEqual(api_tester.get_full_path('theme/9'),
                             (sorted([r['uri'] for r in result])[-1]))
        self.assertEqual(api_tester.get_full_path('theme/'),
                         (sorted([r['thesaurus'] for r in result])[-1]))


class TestFetchGroups(unittest.TestCase):

    def test_fetchGroups_english(self):
        language = 'en'
        result = api_tester.request('fetchGroups', 'language', language)
        self.assertEqual([r['preferredLabel'] for r in result],
                         GROUPS_PREF_LABEL)
        if not api_tester.LOCAL_TEST:
            self.assertEqual([r['uri'] for r in result], GROUPS_URI)
        self.assertEqual([r['thesaurus'] for r in result], GROUPS_THESAURUS)

    def test_fetchGroups_spanish(self):
        language = 'es'
        result = api_tester.request('fetchGroups', 'language', language)

        self.assertEqual(u'T\xc9RMINOS GENERALES',
                         sorted([r['preferredLabel']['string']
                                 for r in result])[-1])
        if not api_tester.LOCAL_TEST:
            self.assertEqual(api_tester.get_full_path('group/96'),
                             (sorted([r['uri'] for r in result])[-1]))
        self.assertEqual(api_tester.get_full_path('group/'),
                         (sorted([r['thesaurus'] for r in result])[-1]))


class TestGetConceptsMatchingRegexByThesaurus(unittest.TestCase):

    def get_match_names(self, match):
        names = []
        for concept in match:
            names.append(concept['preferredLabel']['string'])
        return names

    def test_begins_with(self):
        query = {
            'regexp': '^space t',
            'namespace': api_tester.get_full_path('concept/'),
            'language': 'en',
        }
        match = api_tester.request('getConceptsMatchingRegexByThesaurus',
                                   'regex', query['regexp'],
                                   'thesaurus_uri', query['namespace'],
                                   'language', query['language'])
        names = self.get_match_names(match)
        self.assertEqual(names, ['space transportation', 'space travel'])

    def test_all_operators(self):
        query = {
            'regexp': '^air.+pol.+$',
            'namespace': api_tester.get_full_path('concept/'),
            'language': 'en',
        }
        match = api_tester.request('getConceptsMatchingRegexByThesaurus',
                                   'regex', query['regexp'],
                                   'thesaurus_uri', query['namespace'],
                                   'language', query['language'])
        names = self.get_match_names(match)
        self.assertEqual(names, ['air pollutant', 'air pollution'])

    def test_no_operator(self):
        query = {
            'regexp': 'so',
            'namespace': api_tester.get_full_path('theme/'),
            'language': 'en',
        }
        match = api_tester.request('getConceptsMatchingRegexByThesaurus',
                                   'regex', query['regexp'],
                                   'thesaurus_uri', query['namespace'],
                                   'language', query['language'])
        names = self.get_match_names(match)
        self.assertEqual(names, ['resources', 'social aspects, population',
                                 'soil'])


class TestGetAllConceptRelatives(unittest.TestCase):
    def setUp(self):
        skos_uri = 'http://www.w3.org/2004/02/skos/core#'
        gemet_schema_uri = api_tester.get_full_path(
            '2004/06/gemet-schema.rdf#')
        self.relations = {
            'narrower': skos_uri + 'narrower',
            'broader': skos_uri + 'broader',
            'related': skos_uri + 'related',
            'groupMember': gemet_schema_uri + 'groupMember',
            'group': gemet_schema_uri + 'group',
            'theme': gemet_schema_uri + 'theme',
            'themeMember': gemet_schema_uri + 'themeMember',
        }

    def test_random_supergroup(self):
        supergroup_uri = api_tester.get_full_path('supergroup/4044')

        relatives = api_tester.request('getAllConceptRelatives',
                                       'concept_uri', supergroup_uri)
        received_relations = []
        for relative in relatives:
            received_relations.append('%s %s' % (relative['relation'],
                                                 relative['target']))
        received_relations = sorted(received_relations)

        self.assertEqual(len(received_relations), len(SUPERGROUP_RELATIVES))
        if api_tester.LOCAL_TEST:
            pass
        else:
            for i in range(0, len(received_relations)):
                self.assertEqual(received_relations[i],
                                 SUPERGROUP_RELATIVES[i])

    def test_random_group(self):
        group_uri = api_tester.get_full_path('group/96')

        relatives = api_tester.request('getAllConceptRelatives',
                                       'concept_uri', group_uri)
        received_relations = []
        for relative in relatives:
            received_relations.append('%s %s' % (relative['relation'],
                                                 relative['target']))
        received_relations = sorted(received_relations)

        self.assertEqual(296, len(received_relations))
        if api_tester.LOCAL_TEST:
            pass
        else:
            self.assertEqual(received_relations[-1].split(' ')[0],
                             self.relations['broader'])
            self.assertEqual(received_relations[-1].split(' ')[1],
                             api_tester.get_full_path('supergroup/2894'))

            for relation in received_relations[:-2]:
                self.assertEqual(self.relations['groupMember'],
                                 relation.split(' ')[0])
            self.assertEqual(received_relations[0].split(' ')[1],
                             api_tester.get_full_path('concept/100'))
            self.assertEqual(received_relations[-2].split(' ')[1],
                             api_tester.get_full_path('concept/95'))

    def test_random_theme(self):
        theme_uri = api_tester.get_full_path('theme/1')

        relatives = api_tester.request('getAllConceptRelatives',
                                       'concept_uri', theme_uri)
        received_relations = []
        for relative in relatives:
            received_relations.append('%s %s' % (relative['relation'],
                                                 relative['target']))
        received_relations = sorted(received_relations)

        self.assertEqual(296, len(received_relations))
        if api_tester.LOCAL_TEST:
            pass
        else:
            for relation in received_relations:
                self.assertEqual(self.relations['themeMember'],
                                 relation.split(' ')[0])
            self.assertEqual(received_relations[0].split(' ')[1],
                             api_tester.get_full_path('concept/100'))
            self.assertEqual(received_relations[-1].split(' ')[1],
                             api_tester.get_full_path('concept/95'))

    def test_random_concept(self):
        concept_uri = api_tester.get_full_path('concept/100')

        relatives = api_tester.request('getAllConceptRelatives',
                                       'concept_uri', concept_uri)
        received_relations = []
        for relative in relatives:
            received_relations.append('%s %s' % (relative['relation'],
                                                 relative['target']))
        received_relations = sorted(received_relations)

        self.assertEqual(len(received_relations), len(CONCEPT_RELATIVES))
        if api_tester.LOCAL_TEST:
            pass
        else:
            for i in range(0, len(received_relations)):
                self.assertEqual(received_relations[i], CONCEPT_RELATIVES[i])


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--public', action='store_true')
    parser.add_argument('--get', action='store_true')
    options = parser.parse_args()
    argv = sys.argv

    local = not options.public
    get = options.get
    url = ('http://localhost:8000/gemet/' if local else
           'http://www.eionet.europa.eu/gemet/')
    api_tester = ApiTester(url, local, get)
    if options.public:
        argv.remove('--public')
    if options.get:
        argv.remove('--get')

    unittest.main(argv=argv)
