.. Gemet API documentation master file, created by
   sphinx-quickstart on Wed Apr  2 12:29:13 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

GEMET API's documentation
*************************

GEMET's data is exposed through the Web for remote applications using XML
(RDF/SKOS), HTTP and XML/RPC. The XML output is available at
http://www.eionet.europa.eu/gemet/rdf.

API for XML/RPC and HTTP
=======================
The following set of functions can be called by a Web application or Web page
using either HTTP, where the parameters are specified in the query string or via
XML/RPC. A combination of such function calls ensure the full retrieval of
GEMET's content.


.. function:: getTopmostConcepts(thesaurus_uri, language='en')

    :func:`getTopmostConcepts` is a primary API method.

.. function:: getAllConceptRelatives(concept_uri, target_thesaurus_uri=None, relation_uri=None)

   :func:`getAllConceptRelatives` is a primary API method.

.. function:: getRelatedConcepts(concept_uri, relation_uri, language='en')

   :func:`getRelatedConcepts` is a primary API method.

.. function:: getConcept(concept_uri, lang)

    :func:`getConcept` is a primary API method. It gets all the available information about a specific concept. It takes *concept_uri* as a valid resource GEMET URI and *lang* as a string indicating the language code.

.. function:: hasConcept(concept_uri)

   :func:`hasConcept` is a primary API method.

.. function:: hasRelation(concept_uri, relation_uri, object_uri)

   :func:`hasRelation` is a primary API method.

.. function:: getAllTranslationsForConcept(concept_uri, property_uri)

   :func:`getAllTranslationsForConcept` is a primary API method.

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


