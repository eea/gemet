from gemet.thesaurus.models import Concept


def globals(request):
    return {
        'PENDING': Concept.PENDING,
        'PUBLISHED': Concept.PUBLISHED,
        'DELETED': Concept.DELETED,
        'DELETED_PENDING': Concept.DELETED_PENDING,
    }
