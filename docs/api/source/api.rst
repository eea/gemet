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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~

.. versionadded:: 2.0


.. function:: getTopmostConcepts(thesaurus_uri, language='en')

    :func:`getTopmostConcepts` is a primary API method.

.. function:: getAllConceptRelatives(concept_uri, target_thesaurus_uri=None, relation_uri=None)

   :func:`getAllConceptRelatives` is a primary API method.

.. function:: getRelatedConcepts(concept_uri, relation_uri, language='en')

   :func:`getRelatedConcepts` is a primary API method.

.. function:: getConcept(concept_uri, lang)

    Retrieve all the available information about a specific concept. It takes *concept_uri* as a valid resource URI and *lang* as a string indicating the language cod, shown in the follow examples::

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
        ...            result = apiTester.doXmlRpc('hasRelation', relation)
        ...            print result
        ...
        ...        for relation in bad_relations:
        ...            result = apiTester.doXmlRpc('hasRelation', relation)
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

   Given a valid *concept_uri* and a valid *property_uri* the :func:`getAllTranslationsForConcept` retrieves all available translations for that concept's property within GEMET information database.

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
        ....


.. function:: getConceptsMatchingKeyword(keyword, search_mode, thesaurus_uri, language)

   :func:`getConceptsMatchingKeyword` is a primary API method.

.. function:: getConceptsMatchingRegexByThesaurus(regex, thesaurus_uri, language)

   :func:`getConceptsMatchingRegexByThesaurus` is a primary API method.

.. function:: getAvailableLanguages(concept_uri)

   :func:`getAvailableLanguages` is a primary API method.

.. function:: getSupportedLanguages(thesaurus_uri)

   :func:`getSupportedLanguages` is a primary API method.

.. function:: getAvailableThesauri(self)

   :func:`getAvailableThesauri` is a primary API method.

.. function:: fetchThemes(language)

   :func:`fetchThemes` is a primary API method.

.. function:: fetchGroups(language)

   :func:`fetchGroups` is a primary API method.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


