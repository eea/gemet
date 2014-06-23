Views
=====

Static views
------------

* **AboutView**
    Displays static data for the about page. It presents the general information about the site.

* **ChangesView**
    Presents the history of changes that have occurred to the site.


List Views - displays a list of entries from the database
---------------------------------------------------------

* **ThemesView**
    This view displays all themes for a specific language.

* **InspireThemesView**
    Extends the ThemesView, for presenting the INSPIRE Spatial Data Themes.

* **GroupsView**
    Presents all the groups available.

* **DefinitionSourcesView**
    Displays the sources for the terms available on the GEMET.

* **AlphabetsView**
    Displays all the aplhabets avaialable.

* **RelationsView**
    Displays the existing relations inside a group, given as a parameter.

* **PaginatorView**
    A helper view, that paginates the concepts of the site. Can filter by the first letter of the concept.

* **ThemeConceptsView**
    Extends the PaginatorView, for presenting the concepts that are included in a specific Theme.

* **AlphabeticView**
    Extends the PaginatorView and presents a list of concepts in alphabetic order.

* **DefinitionsView**
    Presents all the term definitions available on the GEMET.

* **GemetGroupsView**
    Presents all the supergroups, groups and themes available on the GEMET.


Detail View - displays the details of a single entry from the database
----------------------------------------------------------------------

* **ConceptView**
    A general view for presenting the available information about a specific concept.

* **TermView**
    Extends the ConceptView and presents the details of a specific Term. This details are: definition, source, the themes and the groups to which belongs, other related terms and relations.

* **ThemeView**
    Extends the ConceptView and presents the details of a specific Theme. It presents the definition, the scope note and the concepts that are included in this Theme.

* **InspireThemeView**
    Extends the ConceptView and presents the details of a specific InspireTheme.

* **GroupView**
    Extends the ConceptView and presents the details of a specific Group. It presents the definition, the SuperGroup to which belongs and the concepts that are included in this Group.

* **SuperGroupView**
    Extends the ConceptView and presents the details of a specific SuperGroup. It presents the definition, the groups that are included in this SuperGroup and the available translations.

* **GemetRelationsView**
    A view, that presents the existing relations between concepts and the type of the relationship.

* **BackboneView**
    A view, that presents the existing inclusion relationships between concepts.

* **DownloadView**
    A view, allowing to download labels, definitions, supergroups, groups and themes in available languages in RDF format.

* **SearchView**


XML Views - displays data in XML format
---------------------------------------

* **XMLTemplateView**
    A helper view, allowing to present data in XML format.

* **BackboneRDFView**
    Extends the XMLTemplateView and presents the existing supergroups, groups, themes and relations between concepts in RDF format.

* **Skoscore**
    Extends the XMLTemplateView and presents the existing relations between concepts.

* **DefinitionsByLanguage**
    Extends the XMLTempalteView and presents the existing definitions on the GEMET in a specific language in RDF format.

* **DefinitionsByLanguage**
    Extends the XMLTempalteView and presents the existing supergroups, groups and themes on the GEMET in a specific language in RDF format.


