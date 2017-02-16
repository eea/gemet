from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.views import View
from django.urls import reverse

from gemet.thesaurus.models import Concept, ForeignRelation, Group, Language
from gemet.thesaurus.models import Property, PropertyType, Relation, Theme
from gemet.thesaurus.models import Term, Version
from gemet.thesaurus.forms import PropertyForm, ForeignRelationForm
import json


class ConceptMixin(object):

    def _set_concept_model(self, parent_type):
        if parent_type == 'group':
            self.model = Group
        elif parent_type == 'theme':
            self.model = Theme
        elif parent_type in ['broader', 'narrower', 'related']:
            self.model = Term

    def _get_all_concepts_by_langcode(self, langcode, model):
        return (
            Property.published.filter(
                name='prefLabel',
                language__code=langcode,
                concept__namespace__heading=self.model.NAMESPACE,
            )
            .extra(select={'name': 'value',
                           'id': 'concept_id'
                           },
                   order_by=['name'])
            .values('name', 'id').all()
        )


class JsonResponseMixin(object):

    def _get_response(self, data, status, status_code):
        response = HttpResponse(json.dumps(data),
                                content_type="application/json")
        response.status = status
        response.status_code = status_code
        return response


class EditPropertyView(JsonResponseMixin, View):

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
                                        name=kwargs['name'])

        published_field = field.filter(status=Property.PUBLISHED).first()
        pending_field = field.filter(status=Property.PENDING).first()

        if pending_field:
            pending_field.value = form.cleaned_data['value']
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
            field = Property.objects.create(status=Property.PENDING,
                                            is_resource=is_resource,
                                            version_added=version,
                                            concept=concept, language=language,
                                            name=kwargs['name'],
                                            **form.cleaned_data)
        data = {"value": field.value}
        return self._get_response(data, 'success', 200)


class RemoveParentRelationView(JsonResponseMixin, ConceptMixin, View):

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
            property_type__name=relation_type)

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


class AddParentRelationView(JsonResponseMixin, ConceptMixin, View):

    def get_reverse_urls(self, concept_list, **kwargs):
        for concept in concept_list:
            url_args = {'langcode': kwargs['langcode'],
                        'concept_id': kwargs['concept_id'],
                        'parent_id': concept['id']}
            remove_rev = reverse('remove_parent', kwargs=url_args)
            add_rev = reverse('add_parent', kwargs=url_args)
            concept_code = Concept.objects.get(id=concept['id']).code
            concept_rev = reverse('concept', kwargs={
                'langcode': kwargs['langcode'],
                'code': concept_code})
            concept['href'] = remove_rev
            concept['href_add'] = add_rev
            concept['href_concept'] = concept_rev

    def get(self, request, **kwargs):
        relation_type = kwargs['type']
        self._set_concept_model(kwargs['type'])
        try:
            concept = Concept.objects.get(id=kwargs['concept_id'])
        except ObjectDoesNotExist:
            data = {"message": 'Object does not exist.'}
            return self._get_response(data, 'error', 400)

        concept.parents_relations = [kwargs['type']]
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
            theme_property = PropertyType.objects.get(name=relation_type)
            field = Relation(source=concept, target=parent_concept,
                             status=Property.PENDING, version_added=version,
                             property_type=theme_property)
            field.save()
        data = {}
        return self._get_response(data, 'success', 200)


class AddPropertyView(JsonResponseMixin, View):

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
        version = Version.objects.create()
        # Todo: Remove when version is stable
        field = Property.objects.create(status=Property.PENDING,
                                        version_added=version,
                                        language=language, concept=concept,
                                        name=kwargs['name'],
                                        **form.cleaned_data)
        url_args = {'langcode': kwargs['langcode'],
                    'concept_id': kwargs['concept_id']}
        remove_url = reverse('remove_property', kwargs=url_args)

        data = {"value": field.value,
                "id": field.id,
                "url": remove_url,
               }
        return self._get_response(data, 'success', 200)


class RemovePropertyView(JsonResponseMixin, View):

    def post(self, request, **kwargs):
        try:
            language = Language.objects.get(code=kwargs['langcode'])
            concept = Concept.objects.get(id=kwargs['concept_id'])
            # todo add name filtering in here.. it is not ok as it is now
            field = Property.objects.filter(language=language, concept=concept,
                                            value=request.POST['value']).first()
        except ObjectDoesNotExist:
            data = {"message": 'Object does not exist.'}
            return self._get_response(data, 'error', 400)
        field.status = Property.DELETED_PENDING
        field.save()
        data = {}
        return self._get_response(data, 'success', 200)


class AddForeignRelationView(JsonResponseMixin, ConceptMixin, View):

    def get(self, request, **kwargs):
        relation_types = [{"name": prop.name,
                           "label": prop.label,
                           "id": prop.id}
                          for prop in PropertyType.objects.all()]
        data = {"relation_types": relation_types}
        return self._get_response(data, 'success', 200)

    def post(self, request, **kwargs):
        try:
            concept = Concept.objects.get(id=kwargs['concept_id'])
            property_type = PropertyType.objects.get(id=request.POST['type'])
        except ObjectDoesNotExist:
            data = {"message": 'Object does not exist.'}
            return self._get_response(data, 'error', 400)
        form = ForeignRelationForm(request.POST)
        if form.is_valid():
            version = Version.objects.create()
            # todo remove version when stable
            new_relation = ForeignRelation.objects.create(
                version_added=version, property_type=property_type,
                concept=concept, **form.cleaned_data)
            url_kwargs = {'langcode': kwargs['langcode'],
                          'id': new_relation.id}
            data = {'id': new_relation.id,
                    'remove_url': reverse('remove_other', kwargs=url_kwargs)}
            return self._get_response(data, 'success', 200)
        data = {"message": form.errors}
        return self._get_response(data, 'error', 400)


class RemoveForeignRelationView(JsonResponseMixin, View):

    def post(self, request, **kwargs):
        try:
            foreign_relation = ForeignRelation.objects.get(id=kwargs['id'])
        except ObjectDoesNotExist:
            data = {"message": 'Object does not exist.'}
            return self._get_response(data, 'error', 400)
        foreign_relation.status = Property.DELETED_PENDING
        foreign_relation.save()
        data = {}
        return self._get_response(data, 'success', 200)
