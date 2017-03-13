from models import Group, SuperGroup, Theme, Term
RELATION_TYPES = [
    'theme',
    'group',
    'broader',
    'narrower',
    'related',
    'groupMember',
    'themeMember',
]

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

CONCEPT_TYPES = {
    'Themes': Theme,
    'Groups': Group,
    'Concepts': Term,
    'Super groups': SuperGroup,
}