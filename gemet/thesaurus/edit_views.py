from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.views import View
from django.urls import reverse

from gemet.thesaurus.models import Concept, Group, Language, Property
from gemet.thesaurus.models import PropertyType, Relation, Theme, Version
from gemet.thesaurus.forms import PropertyForm
import json


class ConceptMixin(object):

    def _set_concept_model(self, parent_type):
        if parent_type == 'group':
            self.model = Group
        else:
            self.model = Theme

    def _get_all_concepts_by_langcode(self, langcode, model):
        return (
            Property.published.filter(
                name='prefLabel',
                language__code=langcode,
                concept_id__in=model.published.values_list(
                    'id', flat=True)
            )
            .extra(select={'name': 'value',
                           'id': 'concept_id'
                           },
                   order_by=['name'])
            .values('name', 'id')
        )


class ResponseMixin(object):

    def _get_response(self, data, status, status_code):
        response = HttpResponse(json.dumps(data),
                                content_type="application/json")
        response.status = status
        response.status_code = status_code
        return response


class EditPropertyView(ResponseMixin, View):

    def post(self, request, **kwargs):
        try:
            language = Language.objects.get(code=kwargs['langcode'])
            concept = Concept.objects.get(id=kwargs['concept_id'])
        except ObjectDoesNotExist:
            data = {"message": 'Object does not exist.'}
            return self._get_response(data, 'error', 400)

        form = PropertyForm(request.POST)

        if not form.is_valid():
            data = {"message": form.errors}
            return self._get_response(data, 'error', 400)

        field = Property.objects.filter(language=kwargs['langcode'],
                                        concept__id=kwargs['concept_id'],
                                        name=kwargs['property'])

        published_field = field.filter(status=Property.PUBLISHED).first()
        pending_field = field.filter(status=Property.PENDING).first()

        if pending_field:
            pending_field.value = request.POST['value']
            pending_field.save()
            field = pending_field

        else:
            is_resource = False
            if published_field:
                published_field.status = Property.DELETED_PENDING
                published_field.save()
                is_resource = published_field.is_resource

            version = Version.objects.create()
            # Todo: Remove when version is stable
            field = Property.objects.create(
                language=language, concept=concept,
                name=kwargs['property'],
                value=request.POST['value'],
                status=Property.PENDING,
                is_resource=is_resource,
                version_added=version)
        data = {"value": field.value}
        return self._get_response(data, 'success', 200)


class RemoveParentRelationView(ResponseMixin, ConceptMixin, View):

    def post(self, request, **kwargs):
        relation_type = request.POST['type']
        if not relation_type:
            data = {"message": 'Attribute type is required.'}
            return self._get_response(data, 'error', 400)

        self._set_concept_model(relation_type)
        try:
            concept = Concept.objects.get(id=kwargs['concept_id'])
            parent_concept = self.model.objects.get(id=kwargs['parent_id'])
        except ObjectDoesNotExist:
            data = {"message": 'Object does not exist.'}
            return self._get_response(data, 'error', 400)

        relation = Relation.objects.filter(
            source=concept, target=parent_concept,
            property_type__name=self.model.__name__)

        published = relation.filter(status=Property.PUBLISHED).first()
        pending = relation.filter(status=Property.PENDING).first()
        if published:
            published.status = Property.DELETED_PENDING
            published.save()
        if pending:
            pending.status = Property.DELETED_PENDING
            pending.save()
        if relation:
            data = {}
            return self._get_response(data, 'success', 200)
        data = {"message": 'Object does not exist.'}
        return self._get_response(data, 'error', 400)


class AddParentRelationView(ResponseMixin, ConceptMixin, View):

    def get_reverse_urls(self, concept_list, **kwargs):
        for concept in concept_list:
            url_args = {'langcode': kwargs['langcode'],
                        'concept_id': kwargs['concept_id'],
                        'parent_id': concept['id']}
            remove_rev = reverse('remove_parent', kwargs=url_args)
            add_rev = reverse('add_parent', kwargs=url_args)
            concept['href'] = remove_rev
            concept['href_add'] = add_rev

    def get(self, request, **kwargs):
        relation_type = request.GET['type']
        if not relation_type:
            data = {"message": 'Attribute type is required.'}
            return self._get_response(data, 'error', 400)

        self._set_concept_model(relation_type)
        try:
            concept = Concept.objects.get(id=kwargs['concept_id'])
        except ObjectDoesNotExist:
            data = {"message": 'Object does not exist.'}
            return self._get_response(data, 'error', 400)

        concept.parents_relations = [request.GET['type']]
        concept.set_parents(kwargs['langcode'])
        target_concepts = self._get_all_concepts_by_langcode(
            langcode=kwargs['langcode'], model=self.model)
        type_name = relation_type + "s"
        concept_relations = [y['id'] for y in getattr(concept, type_name)]
        unselected_concepts = [x for x in target_concepts
                               if x['id'] not in concept_relations]
        self.get_reverse_urls(unselected_concepts, **kwargs)
        data = {"parents": unselected_concepts}
        return self._get_response(data, 'success', 200)

    def post(self, request, **kwargs):
        relation_type = request.POST['type']
        if not relation_type:
            data = {"message": 'Attribute type is required.'}
            return self._get_response(data, 'error', 400)

        self._set_concept_model(relation_type)
        try:
            concept = Concept.objects.get(id=kwargs['concept_id'])
            parent_concept = self.model.objects.get(id=kwargs['parent_id'])
        except ObjectDoesNotExist:
            data = {"message": 'Object does not exist.'}
            return self._get_response(data, 'error', 400)

        relations = Relation.objects.filter(
            source=concept, target=parent_concept,
            property_type__name=relation_type)
        deleted = relations.filter(status=Property.DELETED).first()
        deleted_pending = relations.filter(
            status=Property.DELETED_PENDING).first()
        if deleted:
            deleted.status = Property.PENDING
            deleted.save()
        if deleted_pending:
            deleted_pending.status = Property.PENDING
            deleted_pending.save()
        # create a new relation if there isn't one pending or published
        check_relation_status = relations.filter(status__in=[Property.PUBLISHED,
                                                             Property.PENDING])
        if not check_relation_status:
            version = Version.objects.create()
            theme_property = PropertyType.objects.get(label=self.model.__name__)
            field = Relation(source=concept, target=parent_concept,
                             status=Property.PENDING, version_added=version,
                             property_type=theme_property)
            field.save()
        data = {}
        return self._get_response(data, 'success', 200)
