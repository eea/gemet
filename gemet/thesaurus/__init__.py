NR_CONCEPTS_ON_PAGE = 40
DISTANCE_NUMBER = 9
DEFAULT_LANGCODE = 'en'

PENDING = 0
PUBLISHED = 1
DELETED = 2
DELETED_PENDING = 3

SEARCH_SEPARATOR = '\t'
SEARCH_FIELDS = ['prefLabel', 'altLabel', 'notation', 'hiddenLabel']

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

SOURCE_RELATION_TO_TARGET = {
    ('Concepts', 'group'): 'Groups',
    ('Concepts', 'theme'): 'Themes',
    ('Concepts', 'broader'): 'Concepts',
    ('Concepts', 'narrower'): 'Concepts',
    ('Concepts', 'related'): 'Concepts',
    ('Groups', 'groupMember'): 'Concepts',
    ('Groups', 'broader'): 'Super groups',
    ('Super groups', 'narrower'): 'Groups',
    ('Themes', 'themeMember'): 'Concepts',
}

RELATION_PAIRS = {
    'group': 'groupMember',
    'theme': 'themeMember',
    'groupMember': 'group',
    'themeMember': 'theme',
    'broader': 'narrower',
    'narrower': 'broader',
    'related': 'related',
}

EXACT_QUERY = 0
BEGIN_WITH_QUERY = 1
END_WITH_QUERY = 2
CONTAIN_QUERY = 3
ALL_SEARCH_MODES = 4
