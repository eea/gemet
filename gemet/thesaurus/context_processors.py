from gemet.thesaurus import PENDING, PUBLISHED, DELETED_PENDING, DELETED


def globals(request):
    return {
        'PENDING': PENDING,
        'PUBLISHED': PUBLISHED,
        'DELETED': DELETED,
        'DELETED_PENDING': DELETED_PENDING,
    }
