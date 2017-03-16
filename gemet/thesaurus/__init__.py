NR_CONCEPTS_ON_PAGE = 40
DEFAULT_LANGCODE = 'en'

PENDING = 0
PUBLISHED = 1
DELETED = 2
DELETED_PENDING = 3

NS_VIEW_MAPPING = {
    'Concepts': 'concept',
    'Themes': 'theme',
    'Groups': 'group',
    'Super groups': 'supergroup',
    'Inspire Themes': 'inspire_theme',
}

NS_ID_VIEW_MAPPING = {
    '1': 'concept',
    '4': 'theme',
    '3': 'group',
    '2': 'supergroup',
    '5': 'inspire_theme',
}

FOREIGN_RELATION_TYPES = [
    'exactMatch',
    'broadMatch',
    'closeMatch',
    'narrowMatch',
    'relatedMatch',
    'hasWikipediaArticle',
    'sameEEAGlossary',
    'seeAlso',
]

EDIT_URL_NAMES = {
    'Themes': 'theme_edit',
    'Groups': 'group_edit',
    'Concepts': 'concept_edit',
    'Super groups': 'supergroup_edit',
}
