.. Gemet API documentation master file, created by
   sphinx-quickstart on Wed Apr  2 12:29:13 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

GEMET API's documentation
*************************

GEMET's data is exposed through the Web for remote applications using XML
(RDF/SKOS), HTTP and XML/RPC. The XML output is available at
http://www.eionet.europa.eu/gemet/rdf.

Common RPC methods for GEMET API
================================
The following set of functions can be called by a Web application or Web page
using either HTTP, where the parameters are specified in the query string or via
XML/RPC. A combination of such function calls ensure the full retrieval of
GEMET's content.


Overview - general Python class tester sample
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To prove the functionality of the XML/RPC API the following Python piece of code will be used::

    >>> import xmlrpclib
    >>> import pprint
    >>>
    >>> class ApiTester(object):
    ...
    ...     xmlrpc_url = 'http://www.eionet.europa.eu/gemet'
    ...
    ...     def doXmlRpc(self, method, *args):
    ...         server = xmlrpclib.ServerProxy(self.xmlrpc_url, allow_none=True)
    ...         return getattr(server, method)(*args)
    ...
    ...
    ... pp = pprint.PrettyPrinter(indent=4)
    ... apiTester = ApiTester()
    ...
    >>> def test_specificApiFunction(*args, **kwargs)
    >>>     TODO

The *test_specificApiFunction* in the end will be stated in all the following API primary methods to show the use of parameters and the returning result within a sample Python script.


WebService API methods
~~~~~~~~~~~~~~~~~~~~~~

.. versionadded:: 2.0


.. function:: getTopmostConcepts(thesaurus_uri, language='en')

    :func:`getTopmostConcepts` is a primary API method with which all top concepts of a specified *thesaurus_uri* can be obtained::

        >>> def test_getTopmostConcepts():
        ...       some_top_concepts = {
        ...           'http://www.eionet.europa.eu/gemet/concept/': [],
        ...           'http://www.eionet.europa.eu/gemet/group/': [],
        ...           'http://www.eionet.europa.eu/gemet/theme/': [],
        ...       }
        ...
        ...       for thesaurus_uri in some_top_concepts.keys():
        ...           top_concepts = apiTester.doXmlRpc('getTopmostConcepts', thesaurus_uri, 'en')
        ...           for top_concept in top_concepts:
        ...               print top_concept['preferredLabel']['string']
        >>> test_getTopmostConcepts()
        administration
        agriculture
        air
        animal husbandry
        biology
        building
        chemistry
        climate
        disasters, accidents, risk
        economics
        energy
        environmental policy
        fishery
        food, drinking water
        forestry
        [...]

.. function:: getAllConceptRelatives(concept_uri, target_thesaurus_uri=None, relation_uri=None)

   :func:`getAllConceptRelatives` is a primary API method that can be used to get all GEMET related resources. For a given *concept_uri* only, all other resources are extracted from within the database. By using a specific *target_thesaurus_uri* or *relation_uri* the search for 'relatives' can be narrowed.

        >>> def test_getAllConceptRelatives():
        ...        gemet_uri = 'http://www.eionet.europa.eu/gemet/'
        ...        skos_uri = 'http://www.w3.org/2004/02/skos/core#'
        ...        gemet_schema_uri = 'http://www.eionet.europa.eu/gemet/2004/06/gemet-schema.rdf#'
        ...        relations = {
        ...           'narrower': skos_uri + 'narrower',
        ...           'broader': skos_uri + 'broader',
        ...           'related': skos_uri + 'related',
        ...           'groupMember': gemet_schema_uri + 'groupMember',
        ...           'group': gemet_schema_uri + 'group',
        ...           'theme': gemet_schema_uri + 'theme',
        ...           'themeMember': gemet_schema_uri + 'themeMember',
        ...       }
        ...       some_relatives = {
        ...           'http://www.eionet.europa.eu/gemet/group/96': [],
        ...
        ...           'http://www.eionet.europa.eu/gemet/theme/1': [],
        ...
        ...           'http://www.eionet.europa.eu/gemet/concept/100': [],
        ...
        ...           'http://www.eionet.europa.eu/gemet/concept/42': [],
        ...           'http://www.eionet.europa.eu/gemet/group/8603': [],
        ...           'http://www.eionet.europa.eu/gemet/supergroup/4044': [],
        ...        }
        ...
        ...       for concept_uri in some_relatives.keys():
        ...           relatives = apiTester.doXmlRpc('getAllConceptRelatives', concept_uri)
        ...           received_relations = []
        ...           for relative in relatives:
        ...               received_relations.append('%s %s' % (relative['relation'], relative['target']))
        ...
        ...           pp.pprint(received_relations)
        ...           break
        ...
        >>> test_getAllConceptRelatives()
        [ ...
        'http://www.eionet.europa.eu/gemet/2004/06/gemet-schema.rdf#groupMember http://www.eionet.europa.eu/gemet/concept/13135',
        'http://www.eionet.europa.eu/gemet/2004/06/gemet-schema.rdf#groupMember http://www.eionet.europa.eu/gemet/concept/13142',
        'http://www.eionet.europa.eu/gemet/2004/06/gemet-schema.rdf#groupMember http://www.eionet.europa.eu/gemet/concept/13143',
        'http://www.eionet.europa.eu/gemet/2004/06/gemet-schema.rdf#groupMember http://www.eionet.europa.eu/gemet/concept/13292',
        'http://www.eionet.europa.eu/gemet/2004/06/gemet-schema.rdf#groupMember http://www.eionet.europa.eu/gemet/concept/13293',
        'http://www.eionet.europa.eu/gemet/2004/06/gemet-schema.rdf#groupMember http://www.eionet.europa.eu/gemet/concept/13294',
        'http://www.eionet.europa.eu/gemet/2004/06/gemet-schema.rdf#groupMember http://www.eionet.europa.eu/gemet/concept/13295',
        'http://www.eionet.europa.eu/gemet/2004/06/gemet-schema.rdf#groupMember http://www.eionet.europa.eu/gemet/concept/13296',
        'http://www.eionet.europa.eu/gemet/2004/06/gemet-schema.rdf#groupMember http://www.eionet.europa.eu/gemet/concept/13297'
        ....]


.. function:: getRelatedConcepts(concept_uri, relation_uri, language='en')

   :func:`getRelatedConcepts` is a primary API method. For a given *concept_uri* it retrieves any other GEMET content resource if a valid relationship, defined by *relation_uri*, exists. *lang* is a string indicating the language code::

        >>> def test_getRelatedConcepts():
        ...       relatives = apiTester.doXmlRpc('getRelatedConcepts',
        ...                       'http://www.eionet.europa.eu/gemet/concept/42', # acid deposition
        ...                       'http://www.w3.org/2004/02/skos/core#related')
        ...       for relative in relatives:
        ...           print relative['preferredLabel']['string']
        ...
        >>> test_getRelatedConcepts()
        acid rain
        soil acidification

.. function:: getConcept(concept_uri, lang)

   Retrieve all the available information about a specific concept. It takes *concept_uri* as a valid resource URI and *lang* as a string indicating the language code, shown in the follow examples::

        >>> def test_getConcept():
        ...     concept_uri = 'http://www.eionet.europa.eu/gemet/concept/7970'
        ...     lang = 'en'
        ...     result = apiTester.doXmlRpc('getConcept', concept_uri, lang)
        ...     pp.pprint(result)
        ...
        >>> test_getConcept()
        {   'definition': {   'language': 'en',
                              'string': "Travel in the space beyond the earth's atmosphere performed for scientific research purposes."},
            'preferredLabel': {   'language': 'en', 'string': 'space travel'},
            'thesaurus': 'http://www.eionet.europa.eu/gemet/concept/',
            'uri': 'http://www.eionet.europa.eu/gemet/concept/7970'}
        >>>

.. function:: hasConcept(concept_uri)

   :func:`hasConcept` is a primary method that returns a boolean that states whether the *concept_uri* is a valid resource API or not::

        >>> def test_hasConcept():
        ...        good_uris = ['http://www.eionet.europa.eu/gemet/concept/7970',
        ...                     'http://www.eionet.europa.eu/gemet/theme/33']
        ...        bad_uris = ['http://www.eionet.europa.eu/gemet/concept/99999999',
        ...                     'sdfughkdjfng BAD URI! dduidbnJsdfsj']
        ...
        ...        for uri in good_uris:
        ...            result = apiTester.doXmlRpc('hasConcept', uri)
        ...            print result
        ...
        ...        for uri in bad_uris:
        ...            result = apiTester.doXmlRpc('hasConcept', uri)
        ...            print result
        ...
        >>> test_hasConcept()
        True
        True
        False
        False

.. function:: hasRelation(concept_uri, relation_uri, object_uri)

   By using :func:`hasRelation` API primary method, the relationships between concepts can be checked. It takes *concept_uri* and *object_uri* and returns a boolean whether *relation_uri* maps or not as a relationship between them. Please note in the follow examples that the *relation_uri* may be defined from multiple RDF schemas across the web, including the standard `http://www.w3.org/` or GEMET own schema `http://www.eionet.europa.eu/gemet/2004/06/gemet-schema.rdf/` ::

        >>> def test_hasRelation():
        ...         good_relations = [
        ...             ('http://www.eionet.europa.eu/gemet/concept/100',
        ...              'http://www.w3.org/2004/02/skos/core#broader',
        ...              'http://www.eionet.europa.eu/gemet/concept/13292'),
        ...
        ...             ('http://www.eionet.europa.eu/gemet/concept/100',
        ...              'http://www.w3.org/2004/02/skos/core#narrower',
        ...              'http://www.eionet.europa.eu/gemet/concept/661'),
        ...
        ...             ('http://www.eionet.europa.eu/gemet/concept/42',
        ...              'http://www.w3.org/2004/02/skos/core#related',
        ...              'http://www.eionet.europa.eu/gemet/concept/51'),
        ...
        ...            ('http://www.eionet.europa.eu/gemet/concept/100',
        ...             'http://www.eionet.europa.eu/gemet/2004/06/gemet-schema.rdf#theme',
        ...             'http://www.eionet.europa.eu/gemet/theme/1'),
        ...
        ...            ('http://www.eionet.europa.eu/gemet/group/96',
        ...             'http://www.eionet.europa.eu/gemet/2004/06/gemet-schema.rdf#groupMember',
        ...             'http://www.eionet.europa.eu/gemet/concept/21'),
        ...        ]
        ...        bad_relations = [
        ...            ('http://www.eionet.europa.eu/gemet/concept/999999999999',
        ...             'http://www.w3.org/2004/02/skos/core#broader',
        ...             'http://www.eionet.europa.eu/gemet/concept/13292'),
        ...
        ...            ('http://www.eionet.europa.eu/gemet/concept/100',
        ...             'badrelation',
        ...             'http://www.eionet.europa.eu/gemet/concept/13292'),
        ...        ]
        ...        for relation in good_relations:
        ...            result = apiTester.doXmlRpc('hasRelation', *relation)
        ...            print result
        ...
        ...        for relation in bad_relations:
        ...            result = apiTester.doXmlRpc('hasRelation', *relation)
        ...                print result
        >>> test_hasRelation()
        True
        True
        True
        True
        True
        False
        False

.. function:: getAllTranslationsForConcept(concept_uri, property_uri)

   Given a valid *concept_uri* and a valid *property_uri* the :func:`getAllTranslationsForConcept` retrieves all available translations for that concept's property within GEMET information database::

        >>> def test_getAllTranslationsForConcept():
        ...        concepts = [
        ...            {
        ...                'uri': 'http://www.eionet.europa.eu/gemet/concept/7970',
        ...                'properties': {
        ...                    'http://www.w3.org/2004/02/skos/core#prefLabel': {},
        ...                    'http://www.w3.org/2004/02/skos/core#definition': {},
        ...                }
        ...            }
        ...        ]
        ...
        ...        for concept in concepts:
        ...            for prop_uri, prop_values in concept['properties'].iteritems():
        ...                result = apiTester.doXmlRpc('getAllTranslationsForConcept', concept['uri'], prop_uri)
        ...                for value in result:
        ...                    print value['language']
        ...                    print unicode(value['string'])
        ...
        ...
        >>> test_getAllTranslationsForConcept()
        bg
        Пътуване в пространството отвъд земната атмосфера, проведено за научни цели.
        zh-CN
        为了科学研究，在地球大气层以外的空间旅游。
        hr
        Putovanje u prostor izvan Zemljine atmosfere u svrhu znanstvenog istraživanja.
        en
        Travel in the space beyond the earth's atmosphere performed for scientific research purposes.
        pl
        podróż w przestrzeni poza atmosferą ziemską odbywana w celach naukowych
        ru
        Путешествие в космосе за пределами земной атмосферы, выполняемое в научных целях.
        bg
        Пътуване в космоса
        zh-CN
        太空旅行
        [...]

.. function:: getConceptsMatchingKeyword(keyword, search_mode, thesaurus_uri, language)

   :func:`getConceptsMatchingKeyword` is a powerful API method. For a term defined by *keyword*, the function searches the GEMET content looking for matches. The *search_mode* argument indicates the type of term expansion to try when looking for a match as follows:
    - 0 no wildcarding of any type; match 'clothes' exactly
    - 1 suffix regex ('accident' becomes 'accident.+$')
    - 2 prefix regex ('accident' becomes '^.+accident')
    - 3 prefix/suffix combined ('accident' becomes '^.+accident.+$')
    - 4 auto search: each of the previous four expansions is tried in ascending order until a match is found

   Moreover, *thesaurus_uri* represents the GEMET resource in which to look up for, while *lang* is a string that indicates the language code::

        >>> def test_getConceptsMatchingKeyword():
        ...
        ...       def search(keyword, mode):
        ...           result = apiTester.doXmlRpc('getConceptsMatchingKeyword', keyword, mode,
        ...                   'http://www.eionet.europa.eu/gemet/concept/', 'en')
        ...           print set(concept['preferredLabel']['string'] for concept in result)
        ...
        ...       result = search('air', 0) # no wildcard
        ...       result = search('air', 1) # suffix
        ...       result = search('air', 2) # preffix
        ...       result = search('air', 3) # preffix/suffix
        ...       result = search('travel', 4) # should match exact term
        ...       result = search('trave', 4) # should match prefix terms
        ...       result = search('ravel', 4) # should match suffix terms
        ...       result = search('xyzasdf', 4) # should match nothing
        ...       result = search('^air', 0) # should match nothing (regex chars are escaped)
        ...       result = search("'", 3)
        ...
        >>> test_getConceptsMatchingKeyword()
        set(['air'])
        set(['air traffic law', 'aircraft engine emission', 'air quality monitoring', [...]])
        set(['waste air', 'emission to air', 'respiratory air', 'soil air', 'air'])
        set(['air traffic law', 'military air traffic', 'respiratory air', 'aircraft engine emission', [...]])
        set(['travel'])
        set(['travel cost', 'travel'])
        set(['travel', 'gravel', 'space travel'])
        set([])
        set([])
        set(["earth's crust", "woman's status", "Chagas' disease", "public prosecutor's office"])

.. function:: getConceptsMatchingRegexByThesaurus(regex, thesaurus_uri, language)

   This function refines and extends the behaviour of :func:`getConceptsMatchingKeyword` such that one can lookp up in the GEMET content by *regex*. Instead of using any of the conventional aforementioned *search_mode*, a full *regex* expression can be send to refine granularity from the API. *thesaurus_uri* represents the GEMET resource in which to look up for, while *lang* is a string that indicates the language code::

        >>> def test_getConceptsMatchingRegexByThesaurus():
        ...
        ...       reference = [
        ...           {
        ...               'regexp': '^space t',
        ...               'namespace': 'http://www.eionet.europa.eu/gemet/concept/',
        ...               'language': 'en',
        ...           },
        ...           {
        ...               'regexp': '^air.+pol.+$',
        ...               'namespace': 'http://www.eionet.europa.eu/gemet/concept/',
        ...               'language': 'en',
        ...           },
        ...           {
        ...               'regexp': 'so',
        ...               'namespace': 'http://www.eionet.europa.eu/gemet/theme/',
        ...               'language': 'en',
        ...           },
        ...           {
        ...               'regexp': u'гия$',
        ...               'namespace': 'http://www.eionet.europa.eu/gemet/theme/',
        ...               'language': 'ru',
        ...           },
        ...       ]
        ...
        ...       def get_match_names(match):
        ...          names = []
        ...          for concept in match:
        ...              names.append(concept['preferredLabel']['string'])
        ...          return names
        ...
        ...      for query in reference:
        ...          match = apiTester.doXmlRpc('getConceptsMatchingRegexByThesaurus',
        ...                  query['regexp'], query['namespace'], query['language'])
        ...          names = get_match_names(match)
        ...         for name in names:
        ...               print unicode(name)
        ...
        >>> test_getConceptsMatchingRegexByThesaurus()
        space transportation
        space travel
        air pollutant
        air pollution
        resources
        social aspects, population
        soil
        энергия
        биология

.. function:: getAvailableLanguages(concept_uri)

   Given an URI that uniquely identifies a concept, the
   :func:`getAvailableLanguages` primary API method returns a list of
   languages available for translation. It takes the *concept_uri* parameters
   which defines a valid URI for a concept. ::

        >>> def test_getAvailableLanguages():
        ...     concept_uri = 'http://www.eionet.europa.eu/gemet/concept/7970'
        ...     result = apiTester.doXmlRpc('getAvailableLanguages', concept_uri)
        ...     pp.pprint(result)
        ...
        >>> test_getAvailableLanguages()
        [   'ar',
            'bg',
            'ca',
            [...]
            'zh-CN']

.. function:: getSupportedLanguages(thesaurus_uri)

   The :func:`getSupportedLanguages` method retrieves a list containing the
   language codes for all the languages supported by a certain namespace
   (concept, group, theme, etc.). Its parameter, *thesaurus_uri*, specifies the
   URI for the wanted namespace. ::

        >>> def test_getSupportedLanguages():
        ...     thesaurus_uri = 'http://www.eionet.europa.eu/gemet/concept/'
        ...     result = apiTester.doXmlRpc('getSupportedLanguages', thesaurus_uri)
        ...     pp.pprint(result)
        ...
        >>> test_getSupportedLanguages()
        [   'ar',
            'bg',
            'ca',
            [...]
            'zh']

.. function:: getAvailableThesauri()

   This API method is used to fetch a list of all the possible namespaces a
   concept can be classified in. For each namespace a series of more detailed
   information is provided: its name, its URI and its current version. ::

        >>> def test_getAvailableThesauri():
        ...     result = apiTester.doXmlRpc('getAvailableThesauri')
        ...     pp.pprint(result)
        ...
        >>> test_getAvailableThesauri()
        [   {   'name': 'Concepts',
                'uri': 'http://www.eionet.europa.eu/gemet/concept/',
                'version': 'GEMET - Concepts, version 3.1, 2012-07-20'},
            {   'name': 'Super groups',
                'uri': 'http://www.eionet.europa.eu/gemet/supergroup/',
                'version': 'GEMET - Super groups, version 2.4, 2010-01-13'},
            {   'name': 'Groups',
                'uri': 'http://www.eionet.europa.eu/gemet/group/',
                'version': 'GEMET - Groups, version 2.4, 2010-01-13'},
            {   'name': 'Themes',
                'uri': 'http://www.eionet.europa.eu/gemet/theme/',
                'version': 'GEMET - Themes, version 2.4, 2010-01-13'},
            {   'name': 'Inspire Themes',
                'uri': 'http://inspire.ec.europa.eu/theme/',
                'version': 'GEMET - INSPIRE themes, version 1.0, 2008-06-01'}]

.. function:: fetchThemes(lang)

   For the given language, :func:`fetchThemes` method returns the list of
   themes found in the GEMET database. Its only parameter, *lang* represents
   the language code. ::

        >>> def test_fetchThemes():
        ...     lang = 'en'
        ...     result = apiTester.doXmlRpc('fetchThemes', lang)
        ...     pp.pprint(result)
        ...
        >>> test_fetchThemes()
        [   {   'preferredLabel': {   'language': 'en', 'string': 'administration'},
                'thesaurus': 'http://www.eionet.europa.eu/gemet/theme/',
                        'uri': 'http://www.eionet.europa.eu/gemet/theme/1'},
            [...]
            {   'preferredLabel': {   'language': 'en', 'string': 'water'},
                'thesaurus': 'http://www.eionet.europa.eu/gemet/theme/',
                'uri': 'http://www.eionet.europa.eu/gemet/theme/40'}]

.. function:: fetchGroups(lang)

   :func:`fetchGroups` is a primary API method. It retrieves the list of groups
   from the GEMET database for a given language. It takes *lang* as a
   parameter indicating the language code. ::

        >>> def test_fetchGroups():
        ...     lang = 'en'
        ...     result = apiTester.doXmlRpc('fetchGroups', lang)
        ...     pp.pprint(result)
        ...
        >>> test_fetchGroups()
        [   {   'preferredLabel': {   'language': 'en',
                                      'string': 'ADMINISTRATION, MANAGEMENT, POLICY, POLITICS, INSTITUTIONS, PLANNING'},
                'thesaurus': 'http://www.eionet.europa.eu/gemet/group/',
                'uri': 'http://www.eionet.europa.eu/gemet/group/96'},
            [...]
            {   'preferredLabel': {   'language': 'en',
                                      'string': 'WASTES, POLLUTANTS, POLLUTION'},
                'thesaurus': 'http://www.eionet.europa.eu/gemet/group/',
                'uri': 'http://www.eionet.europa.eu/gemet/group/9117'}]


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
