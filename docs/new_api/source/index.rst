.. GEMET's Web services documentation master file, created by
   sphinx-quickstart on Wed Jul  2 15:07:42 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

GEMET API's documentation
*************************

GEMET's data is exposed through the Web for remote applications using XML
(RDF/SKOS), HTTP and XML/RPC. The XML output is available at
http://www.eionet.europa.eu/gemet/rdf.

What is a Concept?
==================

GEMET is language neutral. The problem is that one language might use
a single word to describe a concept. But in another language people
use two or more terms to split the concept into several concepts. As
they say; Eskimos have 40 different words for "snow". In GEMET this
extreme example would be 40 concepts, but the English terms would all be
"snow". Icelandic would have perhaps 15 words for snow, and therefore also
some overlap. Since no language is so rich it has unique terms for all
concepts, GEMET uses a number to distinguish the concepts from each other.

A concept URI is simply the thesaurus URI plus the concept
number. E.g. http://www.eionet.europa.eu/gemet/concept/7769.
Currently it is just a string, but we want to
make GEMET part of the Semantic Web and browsable as
Linked Data.
What this means is that if you visit a concept URI with a webbrowser, you'll see a webpage.
If you use a `linked data <http://wifo5-03.informatik.uni-mannheim.de/bizer/pub/LinkedDataTutorial/>`_
browser, with an **Accept-header** of ``application/rdf+xml``, then an RDF document will be returned.

Using the API as a ReST service
===============================

The methods below are described as method calls in simplified Java with the public keyword implied.
If you want to use it as a ReST api. You first need the URL where the API is implemented.
In GEMET it is http://www.eionet.europa.eu/gemet/ . Then you encode the parameters as a GET operation::

    http://www.eionet.europa.eu/gemet/getTopmostConcepts?thesaurus_uri=http://www.eionet.europa.eu/gemet/theme/&language=es

ReST has the constraint on the API that the arguments can only be text strings.
I.e. you can't send structures over to the server.
Likewise no `polymorphism <http://en.wikipedia.org/wiki/Type_polymorphism>`_ is possible.

Without specifying any additional parameter, the standard format of the output is `JSON <http://en.wikipedia.org/wiki/JSON>`_.

All JSON responses can also be wrapped as JSONP if you provide a jsonp argument. I.e.::

    http://mydomain.info/getTopmostConcepts?thesaurus_uri=­http://www.eionet.europa.eu/gemet/theme/­&language=es&jsonp=callback

will wrap the JSON response in callback method call.

|   If you don't specify a valid method name for the API(see API methods below) you will receive a 400 Bad Request Error.
|   If you don't specify all the required parameters for these methods you will receive the same error.

When designing the API we have been careful not to mix up the URL of
the method with the URL of the thesaurus. It is possible to install the
application and GEMET database somewhere else (e.g. intranet) and then
use it without being dependent on GEMET at http://www.eionet.europa.eu.
I.e.::

    http://mydomain.info/getTopmostConcepts?thesaurus_uri=­http://www.eionet.europa.eu/gemet/theme/­&language=es

must be possible.

Common methods for GEMET API
============================
The following set of functions can be called by a Web application or Web page
using either HTTP, where the parameters are specified in the query string or via
XML/RPC. A combination of such function calls ensure the full retrieval of
GEMET's content.

WebService API methods
======================


.. function:: getTopmostConcepts(URI thesaurus_uri[, String language='en'])

    :param thesaurus_uri: The thesaurus URI from which to retrieve concepts
    :param language: The language in which the concepts are returned
    :rtype: A list of dictionaries representing the concepts

    |   The result from the method will be a list of concept structs that are determined to be top concepts of the thesaurus.
    |   The purpose is to make the thesaurus browsable. In principle all concepts that don't have a broader definition would qualify.
    |   This method replaces *fetchTopConcepts*, *fetchThemes* and *fetchGroups*.
    |   To get the themes, you would call ``getTopmostConcepts('http://www.eionet.europa.eu/gemet/theme/', 'en')``.

    A URI is a subclass of string, potentially with some methods to manipulate the URI.

    Examples:

        ::

            http://www.eionet.europa.eu/gemet/getTopmostConcepts?thesaurus_uri=http://www.eionet.europa.eu/gemet/group/&language=en
        |   `Try link <http://www.eionet.europa.eu/gemet/getTopmostConcepts?thesaurus_uri=http://www.eionet.europa.eu/gemet/group/&language=en>`_
        |
        ::

            http://www.eionet.europa.eu/gemet/getTopmostConcepts?thesaurus_uri=http://inspire.ec.europa.eu/theme/&language=en
        |   `Try link <http://www.eionet.europa.eu/gemet/getTopmostConcepts?thesaurus_uri=http://inspire.ec.europa.eu/theme/&language=en>`_

    |

.. function:: getAllConceptRelatives(URI concept_uri[, URI target_thesaurus_uri, URI relation_uri])

    :param concept_uri: A URI for the concept
    :param target_thesaurus_uri: A URI for a thesaurus representing the namespace in which to look for relatives
    :param relation_uri: A URI for the relation
    :rtype: A list of dictionaries  representing the concepts

    |    This method will return a listing of relations for the given concept.
    |    The relation can be any relationship, but only direct relationships.
    |    The *target_thesaurus_uri* argument is optional. If it isn't provided the relations can be to concepts in all thesauri in the database.
    |    The *relation_uri* argument is optional. It makes it possible to get only one type of relationship.
    |    The relation argument takes a URI, e.g. http://www.w3.org/2004/02/skos/core#narrower.
    |    See [:ref:`knownrelations`] for a list of known relations.
    |    Only thesauri that are stored in the database are included.

    |    The properties *theme* and *hasConcept* are inverse of each other. Meaning *<Concept A> theme <Theme B>* is the same as *<Theme B> hasConcept <Concept A>*.
    |    Therefore hasConcept is not actually listed in the database. Similarly are the properties *group* and *hasConcept* inverse. As are *subGroupOf* and *subGroup*.

    Examples:

        ::

            http://www.eionet.europa.eu/gemet/getAllConceptRelatives?concept_uri=http://www.eionet.europa.eu/gemet/group/234
        |   `Try link <http://www.eionet.europa.eu/gemet/getAllConceptRelatives?concept_uri=http://www.eionet.europa.eu/gemet/group/234>`_

        ::

            http://www.eionet.europa.eu/gemet/getAllConceptRelatives?concept_uri=http://www.eionet.europa.eu/gemet/concept/6740
        |   `Try link <http://www.eionet.europa.eu/gemet/getAllConceptRelatives?concept_uri=http://www.eionet.europa.eu/gemet/concept/6740>`_

        ::

            http://www.eionet.europa.eu/gemet/getAllConceptRelatives?concept_uri=http://inspire.ec.europa.eu/theme/ps
        |   `Try link <http://www.eionet.europa.eu/gemet/getAllConceptRelatives?concept_uri=http://inspire.ec.europa.eu/theme/ps>`_

    |

.. function:: getRelatedConcepts(URI concept_uri, URI relation_uri[, String language='en'])

    :param concept_uri: A URI for the concept
    :param relation_uri: A URI for the relation
    :param language: The language in which the concepts are returned
    :rtype: A list of dictionaries representing the concepts

    |   This method will return related concepts for the given concept.
    |   The relation_uri is mandatory, and must be one of the known relations listed in :func:`getAllConceptRelatives`.
    |   See [:ref:`knownrelations`] for a list of known relations.

    Example:

        ::

           http://www.eionet.europa.eu/gemet/getRelatedConcepts?concept_uri=http://www.eionet.europa.eu/gemet/concept/913&relation_uri=http://www.w3.org/2004/02/skos/core%23broader&language=fr
        |   `Try link <http://www.eionet.europa.eu/gemet/getRelatedConcepts?concept_uri=http://www.eionet.europa.eu/gemet/concept/913&relation_uri=http://www.w3.org/2004/02/skos/core%23broader&language=fr>`_

    |

.. function:: hasRelation(URI concept_uri, URI relation_uri, URI object_uri)

    :param concept_uri: A URI for the concept representing the source
    :param relation_uri: A URI for the relation
    :param object_uri: A URI for the concept representing the target
    :rtype: A boolean - True or False

    |   Tests if the given *concept_uri* is in the relation *relation_uri* with the *object_uri*

    Example:

        ::

            http://www.eionet.europa.eu/gemet/hasRelation?concept_uri=http://www.eionet.europa.eu/gemet/concept/100&relation_uri=http://www.w3.org/2004/02/skos/core%23broader&object_uri=http://www.eionet.europa.eu/gemet/concept/13292
        |   `Try link <http://www.eionet.europa.eu/gemet/hasRelation?concept_uri=http://www.eionet.europa.eu/gemet/concept/100&relation_uri=http://www.w3.org/2004/02/skos/core%23broader&object_uri=http://www.eionet.europa.eu/gemet/concept/13292>`_

    |

.. function:: hasConcept(URI concept_uri)

    :param concept_uri: A URI for the concept
    :rtype: A boolean - True or False

    |   This function tests if the given concept_uri represents a valid concept or not, returning true or false.

    Example:

        ::

            http://www.eionet.europa.eu/gemet/hasConcept?concept_uri=http://www.eionet.europa.eu/gemet/concept/7970
        |   `Try link <http://www.eionet.europa.eu/gemet/hasConcept?concept_uri=http://www.eionet.europa.eu/gemet/concept/7970>`_

    |

.. function:: getConcept(URI concept_uri[, String language='en'])

    :param concept_uri: A URI for the concept
    :param language: The language in which the concepts are returned
    :rtype: A dictionary representing the concept

    |   Returns a Concept struct filled out with information from the requested language.

    Examples:

        ::

            http://www.eionet.europa.eu/gemet/getConcept?concept_uri=http://inspire.ec.europa.eu/theme/ps&language=de
        |   `Try link <http://www.eionet.europa.eu/gemet/getConcept?concept_uri=http://inspire.ec.europa.eu/theme/ps&language=de>`_

        ::

            http://www.eionet.europa.eu/gemet/getConcept?concept_uri=http://www.eionet.europa.eu/gemet/concept/95&language=en
        |   `Try link <http://www.eionet.europa.eu/gemet/getConcept?concept_uri=http://www.eionet.europa.eu/gemet/concept/95&language=en>`_

    |

.. function:: getAllTranslationsForConcept(URI concept_uri, String property_uri)

    :param concept_uri: A URI for the concept
    :param property_uri: A URI for the property type one needs translations for
    :rtype: A list of dictionaries containing the language and the property value

    |   Returns all translations for a property of a given concept.
    |   The property is either a SKOS property URI, or an attribute name from the Concept class.
    |   Currently these are: definition, prefLabel, scopeNote, acronymLabel, and example.
    |   It is possible for a compliant server to have more information about a concept.
    |   These will show up as extra attributes in Concept objects, and it is legal for a client to ask about translations for any attribute of type LanguageString.

    +-------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------+
    |                                 Property URI                                  |                                      Concept attribute                                         |
    +===============================================================================+================================================================================================+
    | \http://www.w3.org/2004/02/skos/core#definition                               | definition                                                                                     |
    +-------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------+
    | \http://www.w3.org/2004/02/skos/core#prefLabel                                | preferredLabel                                                                                 |
    +-------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------+
    | \http://www.w3.org/2004/02/skos/core#scopeNote                                | scopeNote                                                                                      |
    +-------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------+
    | \http://www.w3.org/2004/02/skos/core#altLabel                                 | nonPreferredLabels                                                                             |
    +-------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------+
    | \http://www.w3.org/2004/02/skos/core#example                                  | example                                                                                        |
    +-------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------+
    | \http://www.eionet.europa.eu/gemet/2004/06/gemet-schema.rdf#acronymLabel      | acronymLabel                                                                                   |
    +-------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------+


    |   Why this business with property URIs? It is to provide an opportunity for someone who thinks in RDF terms to use the API in a natural way.

    Example:

        ::

            http://www.eionet.europa.eu/gemet/getAllTranslationsForConcept?concept_uri=http://www.eionet.europa.eu/gemet/concept/10126& property_uri=http://www.w3.org/2004/02/skos/core%23prefLabel
        |   `Try link <http://www.eionet.europa.eu/gemet/getAllTranslationsForConcept?concept_uri=http://www.eionet.europa.eu/gemet/concept/10126&property_uri=http://www.w3.org/2004/02/skos/core%23prefLabel>`_

    |   **Note**: When constructing a GET request of this type, the property URI must be URI-encoded, when it contains the "#" character (which has special meaning in a URI).

.. function:: getConceptsMatchingKeyword(String keyword, int search_mode[, URI thesaurus_uri, String language])

    :param keyword: A string representing the keyword to search for
    :param search_mode: An integer in the range 0 – 4 inclusive:

                        |   0 – no wildcarding of any type ('accident' becomes '^accident$'). SQL syntax: term = 'accident'
                        |   1 – suffix regex ('accident' becomes '^accident.+$'). SQL syntax: term LIKE 'accident%'
                        |   2 – prefix regex ('accident' becomes '^.+accident$'). SQL syntax: term LIKE '%accident'
                        |   3 – prefix/suffix combined ('accident' becomes '^.+accident.+$'). SQL syntax: term LIKE '%accident%'
                        |   4 – auto search: each of the previous four expansions is tried in ascending order until a match is found
    :param thesaurus_uri: Indicates which thesaurus to search in. If the argument is empty, all thesauri in the database are searched
    :param language: The language is used both for specifying what language the keyword is and for returning the concept in the correct language
    :rtype: A list of dictionaries representing the found concepts

    |   The function retrieves a list of concepts matching a keyword for a particular thesaurus.

    Example:

        ::

            http://www.eionet.europa.eu/gemet/getConceptsMatchingKeyword?keyword=air&search_mode=0&thesaurus_uri=http://www.eionet.europa.eu/gemet/concept/&language=en
        |   `Try link <http://www.eionet.europa.eu/gemet/getConceptsMatchingKeyword?keyword=air&search_mode=0&thesaurus_uri=http://www.eionet.europa.eu/gemet/concept/&language=en>`_


    .. versionadded:: 2.1
       The *language* parameter is now set by default to **'en'**.

    |

.. function:: getConceptsMatchingRegexByThesaurus(String regex, URI thesaurus_uri[, String language])

    :param regex: A string representing the regex to search for
    :param thesaurus_uri: Indicates which thesaurus to search in
    :param language: The language is used both for specifying in what language to search for the regex and for returning the concept in the correct language
    :rtype: A list of dictionaries representing the found concepts

    |   Get a list of concepts matching a `regex <http://en.wikipedia.org/wiki/Regular_expression>`_ for a particular thesaurus.
    |   The language argument is used both for specifying what language to search in and for returning the concept in the correct language.

    Example:

        ::

            http://www.eionet.europa.eu/gemet/getConceptsMatchingRegexByThesaurus?regex=^air$&­thesaurus_uri=http://www.eionet.europa.eu/gemet/concept/&language=en
        |   `Try link <http://www.eionet.europa.eu/gemet/getConceptsMatchingRegexByThesaurus?regex=^air$&thesaurus_uri=http://www.eionet.europa.eu/gemet/concept/&language=en>`_


    .. versionadded:: 2.1
       The *language* parameter is now set by default to **'en'**.

    |

.. function:: getAvailableLanguages(URI concept_uri)

    :param concept_uri: A URI for the concept
    :rtype: A list of strings representing the available languages (as codes)

    |   This function returns the languages a concept's preferred label is available in.
    |   A concept must have a preferred label before it can have any other property in that language.

    Example:

        ::

            http://www.eionet.europa.eu/gemet/getAvailableLanguages?concept_uri=http://inspire.ec.europa.eu/theme/ps
        |   `Try link <http://www.eionet.europa.eu/gemet/getAvailableLanguages?concept_uri=http://inspire.ec.europa.eu/theme/ps>`_

    |

.. function:: getSupportedLanguages(URI thesaurus_uri)

    :param concept_uri: A URI for the thesaurus
    :rtype: A list of strings representing the available languages (as codes)

    This function retrieves a list containing the language codes for all the
    languages supported by a certain namespace (concept, group, theme, etc.).
    Its parameter, *thesaurus_uri*, specifies the URI for the wanted namespace.

    Example:

        ::

            http://www.eionet.europa.eu/gemet/getSupportedLanguages?thesaurus_uri=http://www.eionet.europa.eu/gemet/concept/
        |   `Try link <http://www.eionet.europa.eu/gemet/getSupportedLanguages?thesaurus_uri=http://www.eionet.europa.eu/gemet/concept/>`_

    |

.. function:: getAvailableThesauri()

    :rtype: A list of strings representing the available thesauri

    |   This function returns all the thesauri URIs the service knows of.

    Example:

        ::

            http://www.eionet.europa.eu/gemet/getAvailableThesauri
        |   `Try link <http://www.eionet.europa.eu/gemet/getAvailableThesauri>`_

    |

.. function:: fetchThemes([String language])

    :param language: The language in which the themes are returned.
    :rtype: A list of dictionaries representing the fetched themes

    |   This function retrieves all the themes the service knows of.
    |   It is a convenience method that calls getTopmostConcepts('\http://www.eionet.europa.eu/gemet/theme/', language)

    Example:

        ::

            http://www.eionet.europa.eu/gemet/fetchThemes?language=en
        |   `Try link <http://www.eionet.europa.eu/gemet/fetchThemes?language=en>`_

    .. versionadded:: 2.1
        The *language* parameter is now set by default to **'en'**.

    |

.. function:: fetchGroups([String language])

    :param language: The language in which the groups are returned.
    :rtype: A list of dictionaries representing the fetched themes

    |   This function retrieves all the groups the service knows of.
    |   It is a convenience method that calls getTopmostConcepts('\http://www.eionet.europa.eu/gemet/group/', language)

    Example:

        ::

            http://www.eionet.europa.eu/gemet/fetchGroups?language=en
        |   `Try link <http://www.eionet.europa.eu/gemet/fetchGroups?language=en>`_

    .. versionadded:: 2.1
        The *language* parameter is now set by default to **'en'**.

    |

.. function:: fetchSuperGroups([String language])

    .. versionadded:: 2.1
        This is a new method.

    :param language: The language in which super groups are returned.
    :rtype: A list of dictionaries representing the fetched themes

    |   This function retrieves all the supergroups the service knows of.
    |   In principle all groups that don't have a broader definition would qualify.
    |   It is a convenience method that calls getTopmostConcepts('\http://www.eionet.europa.eu/gemet/supergroup/', language)

    Example:

        ::

            http://www.eionet.europa.eu/gemet/fetchSuperGroups?language=en
        |   `Try link <http://www.eionet.europa.eu/gemet/fetchSupergroups?language=en>`_

    |

.. _knownrelations:

**Known relations**
===================

+------------------------------------------------------------------------+------------------------------------------------------------------------------------------------+
|                                 Relation                               |                                      Description                                               |
+========================================================================+================================================================================================+
| \http://www.w3.org/2004/02/skos/core#narrower                          | Narrower concept                                                                               |
+------------------------------------------------------------------------+------------------------------------------------------------------------------------------------+
| \http://www.w3.org/2004/02/skos/core#broader                           | Broader concept                                                                                |
+------------------------------------------------------------------------+------------------------------------------------------------------------------------------------+
| \http://www.w3.org/2004/02/skos/core#related                           | Related, but not a synonym                                                                     |
+------------------------------------------------------------------------+------------------------------------------------------------------------------------------------+
| \http://www.eionet.europa.eu/gemet/2004/06/gemet-schema.rdf#theme      | Theme relationship of a concept. Implemented in RDF, but it is unclear whether it is relevant. |
|                                                                        | Equivalent to broader, but a theme is not a broader concept of a concept                       |
+------------------------------------------------------------------------+------------------------------------------------------------------------------------------------+
| \http://www.eionet.europa.eu/gemet/2004/06/gemet-schema.rdf#themeMember| Theme member relationship of a concept.                                                        |
|                                                                        | Equivalent to narrower, but a theme is not a narrower concept of a concept                     |
+------------------------------------------------------------------------+------------------------------------------------------------------------------------------------+
| \http://www.eionet.europa.eu/gemet/2004/06/gemet-schema.rdf#hasConcept | Source is a theme or group, target is a concept, equivalent to *narrower*                      |
+------------------------------------------------------------------------+------------------------------------------------------------------------------------------------+
| \http://www.eionet.europa.eu/gemet/2004/06/gemet-schema.rdf#group      | Source is a concept, target is a group. Equivalent to *broader*                                |
+------------------------------------------------------------------------+------------------------------------------------------------------------------------------------+
| \http://www.eionet.europa.eu/gemet/2004/06/gemet-schema.rdf#groupMember| Source is a group, target is a concept. Equivalent to *narrower*                               |
+------------------------------------------------------------------------+------------------------------------------------------------------------------------------------+
| \http://www.eionet.europa.eu/gemet/2004/06/gemet-schema.rdf#subGroupOf | Source is a group, target is one of the four super groups. Equivalent to *broader*             |
+------------------------------------------------------------------------+------------------------------------------------------------------------------------------------+
| \http://www.eionet.europa.eu/gemet/2004/06/gemet-schema.rdf#subGroup   | Source is one of the four super groups, target is a group. Equivalent to *narrower*            |
+------------------------------------------------------------------------+------------------------------------------------------------------------------------------------+

**Note**: when using the RESTful API you have to encode the '#' as %23 in URLs, otherwise the webbrowser assumes you're referring to a fragment inside the result document.


**Known thesauri**
==================

+------------------------------------------------------------------------+------------------------------------------------------------------------------------------------+
|                                 Thesauri                               |                                      Description                                               |
+========================================================================+================================================================================================+
| \http://www.eionet.europa.eu/gemet/concept/                            | thesaurus URI for Concepts                                                                     |
+------------------------------------------------------------------------+------------------------------------------------------------------------------------------------+
| \http://www.eionet.europa.eu/gemet/theme/                              | thesaurus URI for Themes                                                                       |
+------------------------------------------------------------------------+------------------------------------------------------------------------------------------------+
| \http://www.eionet.europa.eu/gemet/group/                              | thesaurus URI for Groups                                                                       |
+------------------------------------------------------------------------+------------------------------------------------------------------------------------------------+
| \http://www.eionet.europa.eu/gemet/supergroup/                         | thesaurus URI for SuperGroups                                                                  |
+------------------------------------------------------------------------+------------------------------------------------------------------------------------------------+
| \http://inspire.ec.europa.eu/theme/                                    | thesaurus URI for Inspire Themes                                                               |
+------------------------------------------------------------------------+------------------------------------------------------------------------------------------------+

**Note**: To retrieve the available thesauri, use the function :func:`getAvailableThesauri()`
