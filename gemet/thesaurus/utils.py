import re
import sys
from base64 import encodebytes, decodebytes
from zlib import compress, decompress
from redis import ConnectionError

from django_q.brokers import get_broker
from django_q.status import Stat

from django.db import models
from django.db.models.functions import Cast

from gemet.thesaurus import PENDING, PUBLISHED, DELETED_PENDING
from gemet.thesaurus import SEARCH_FIELDS, SEARCH_SEPARATOR
from gemet.thesaurus import EXACT_QUERY, END_WITH_QUERY, BEGIN_WITH_QUERY
from gemet.thesaurus import CONTAIN_QUERY, ALL_SEARCH_MODES
from gemet.thesaurus.models import Concept, Group, Property, Version


def is_rdf(request):
    accepts = request.META.get("HTTP_ACCEPT", "*/*")
    parts = accepts.split(",")
    return "application/rdf+xml" in parts


def regex_search(query, language, heading):
    return (
        Property.published.filter(
            name="prefLabel",
            language__code=language.code,
            concept__namespace__heading=heading,
            value__iregex=r"%s" % query,
        )
        .extra(
            select={
                "value_coll": "value".format(language.charset),
                "name": "value",
                "id": "concept_id",
            },
            order_by=["value_coll"],
        )
        .values("id", "concept__code", "name")
    )


def search_queryset(
    query,
    language,
    search_mode=EXACT_QUERY,
    heading="Concepts",
    api_call=False,
    status_values=[],
):
    status_values = status_values or Property.PUBLISHED_STATUS_OPTIONS
    if api_call:
        if search_mode == ALL_SEARCH_MODES:
            values = (
                api_search(query, language, status_values, EXACT_QUERY, heading)
                or api_search(query, language, status_values, BEGIN_WITH_QUERY, heading)
                or api_search(query, language, status_values, END_WITH_QUERY, heading)
                or api_search(query, language, status_values, CONTAIN_QUERY, heading)
            )
        else:
            values = api_search(query, language, status_values, search_mode, heading)
    else:
        values = insite_search(query, language, status_values, heading)

    return values


def api_search(query, language, status_values, search_mode, headings):
    search_types = {
        EXACT_QUERY: [query],
        BEGIN_WITH_QUERY: [query + "%%"],
        END_WITH_QUERY: ["%%" + query],
        CONTAIN_QUERY: ["%%" + query + "%%"],
    }
    query_search = search_types.get(search_mode)
    return (
        Property.objects.filter(
            name="prefLabel",
            language__code=language.code,
            status__in=status_values,
            concept__namespace__heading__in=headings,
        )
        .extra(
            where=["value like %s"],
            params=query_search,
        )
        .extra(
            select={
                "value_coll": "value",
                "name": "value",
                "id": "concept_id",
            },
            order_by=["value_coll"],
        )
        .values("id", "concept__code", "name")
    )


def insite_search(query, language, status_values, heading):

    return (
        Property.objects.filter(
            name="searchText",
            language__code=language.code,
            status__in=status_values,
            concept__namespace__heading=heading,
        )
        .extra(
            where=["value like %s"],
            params=["%%" + query + "%%"],
        )
        .extra(
            select={
                "search_text": "value",
                "id": "concept_id",
            },
            order_by=["search_text"],
        )
        .values("id", "search_text", "concept__code")
    )


def get_version_choices():
    current_identifier = Version.objects.get(is_current=True).identifier
    major, middle, minor = map(int, current_identifier.split("."))
    choices = (
        ".".join(map(str, version_parts))
        for version_parts in (
            (major, middle, minor + 1),
            (major, middle + 1, 0),
            (major + 1, 0, 0),
        )
    )
    return ((choice, choice) for choice in choices)


def exp_encrypt(exp):
    return encodebytes(compress(exp.encode("utf-8"))).decode("utf-8")


def exp_decrypt(exp):
    return decompress(decodebytes(exp.encode("utf-8"))).decode("utf-8")


def get_form_errors(errors):
    # errors is a dictionary with a list as value for each key;
    # the function returns the a string with all the values flattened
    return " ".join(["".join(error) for error in errors.values()])


def get_new_code(namespace):
    # We cannot use an autoincrement integer field for `code` because some
    # existing production values (i.e. for Inspire Themes) are not integers.
    return str(
        (
            Concept.objects.filter(namespace=namespace)
            .annotate(int_code=Cast("code", models.IntegerField()))
            .order_by("-int_code")
            .values_list("int_code", flat=True)
            .first()
            or 0
        )
        + 1
    )


def split_text_into_terms(raw_text):
    pattern = re.compile("[^a-zA-Z\d \-\\)\\(:]")
    term_list = pattern.split(raw_text)
    term_list = [
        term.strip(" :").lower() for term in term_list if term.strip(" :").lower() != ""
    ]
    return term_list


def concept_has_unique_relation(concept, relation_type):
    # returns True if the concept already has a relation with the given
    # relation_type (only for group and broader for Groups)
    broader_relation = (
        relation_type == "broader" and concept.namespace.heading == Group.NAMESPACE
    )
    group_relation = relation_type == "group"
    if not (group_relation or broader_relation):
        return False

    return concept.source_relations.filter(
        property_type__name=relation_type,
        status__in=[PUBLISHED, PENDING],
    ).exists()


def get_search_text(concept_id, language_code, status, version):
    search_properties = Property.objects.filter(
        concept_id=concept_id,
        language_id=language_code,
        name__in=SEARCH_FIELDS,
        status__in=[PUBLISHED, PENDING],
    ).values_list("value", flat=True)

    if not search_properties:
        return

    search_text = SEARCH_SEPARATOR.join(search_properties)
    search_text = SEARCH_SEPARATOR + search_text + SEARCH_SEPARATOR

    return Property(
        concept_id=concept_id,
        language_id=language_code,
        name="searchText",
        value=search_text,
        status=status,
        version_added=version,
    )


def refresh_search_text(concept_id, language_code, version=None):
    version = version or Version.under_work()
    new_search = get_search_text(concept_id, language_code, PENDING, version)
    if not new_search:
        return

    search_property = Property.objects.filter(
        concept_id=concept_id,
        language_id=language_code,
        name="searchText",
        status__in=[PUBLISHED, PENDING],
    ).first()
    if not search_property:
        pass
    elif search_property.status == PENDING:
        search_property.delete()
    elif search_property.status == PUBLISHED:
        search_property.status = DELETED_PENDING
        search_property.save()

    new_search.save()


def check_running_workers():
    if "test" in sys.argv:
        # skip validation during testing
        return True, ""
    broker = get_broker()
    try:
        broker.ping()
    except ConnectionError:
        return False, "Can not connect to Redis server."
    stat = Stat.get_all(broker=broker)
    if not len(stat):
        return False, "No running workers found."
    return True, ""
