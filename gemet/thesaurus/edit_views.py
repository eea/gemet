import json

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, Http404
from django.views import View
from django.urls import reverse

from gemet.thesaurus.models import FOREIGN_RELATION_TYPES, RELATION_TYPES
from gemet.thesaurus.models import Concept, Group, SuperGroup, Theme, Term
from gemet.thesaurus.models import ForeignRelation, Relation, Language
from gemet.thesaurus.models import Property, PropertyType, Version
from gemet.thesaurus.models import EditableGroup, EditableTerm, EditableTheme
from gemet.thesaurus.models import EditableSuperGroup
from gemet.thesaurus.forms import PropertyForm, ForeignRelationForm
from gemet.thesaurus.views import GroupView, SuperGroupView, TermView, ThemeView


class GroupEditView(GroupView):
    context_object_name = 'concept'
    template_name = "edit/group_edit.html"
    model = EditableGroup


class SuperGroupEditView(SuperGroupView):
    context_object_name = 'concept'
    template_name = "edit/supergroup_edit.html"
    model = EditableSuperGroup


class TermEditView(TermView):
    template_name = "edit/concept_edit.html"
    model = EditableTerm

    def get_context_data(self, **kwargs):
        context = super(TermEditView, self).get_context_data(**kwargs)
        foreign_relation_types = PropertyType.objects.filter(
            name__in=FOREIGN_RELATION_TYPES)
        context.update({
            "foreign_relation_types": foreign_relation_types,
        })
        return context


class ThemeEditView(ThemeView):
    template_name = "edit/theme_edit.html"
    model = EditableTheme
    context_object_name = 'concept'


class ConceptMixin(object):

    def _set_concept_model(self, relation_type, namespace):
        if relation_type not in RELATION_TYPES:
            raise Http404
        if relation_type == 'group':
            self.model = Group
        elif relation_type == 'theme':
            self.model = Theme
        elif relation_type == 'broader' and namespace == Group.NAMESPACE:
            self.model = SuperGroup
        elif relation_type == 'narrower' and namespace == SuperGroup.NAMESPACE:
            self.model = Group
        elif relation_type in ['broader', 'narrower', 'related', 'groupMember',
                               'themeMember']:
            self.model = Term


class JsonResponseMixin(object):

    def _get_response(self, data, status, status_code):
        response = HttpResponse(json.dumps(data),
                                content_type="application/json")
        response.status = status
        response.status_code = status_code
        return response


class UnrelatedConcepts(JsonResponseMixin, ConceptMixin, View):

    def _set_reverse_urls(self, concepts, langcode, relation):
        for concept in concepts:
            url_kwargs = {
                'langcode': langcode,
                'id': self.concept.id,
                'parent_id': concept['id'],
                'rel_type': relation,
            }
            add_url = reverse('add_relation', kwargs=url_kwargs)
            delete_url = reverse('delete_relation', kwargs=url_kwargs)
            concept_url = reverse('concept', kwargs={
                'langcode': langcode,
                'code': concept['concept__code'],
            })
            concept['add_url'] = add_url
            concept['delete_url'] = delete_url
            concept['concept_url'] = concept_url
        return concepts

    def _get_concepts(self, langcode, relation, query):
        return (
            Property.objects
            .filter(
                name='prefLabel',
                language__code=langcode,
                concept__namespace__heading=self.model.NAMESPACE,
                status__in=(Property.PENDING, Property.PUBLISHED),
                value__istartswith=query,
            )
            .exclude(
                concept_id__in=self.concept.source_relations.filter(
                    property_type__name=relation,
                    status__in=(Relation.PENDING, Relation.PUBLISHED),
                )
                .values_list('target_id', flat=True)
            )
            .extra(select={'name': 'value', 'id': 'concept_id'},
                   order_by=['name'])
            .values('name', 'id', 'concept__code')
        )

    def get(self, request, langcode, code, relation):
        self.concept = Concept.objects.get(code=code)
        self._set_concept_model(relation, self.concept.namespace.heading)

        page = int(request.GET.get('page', '1'))
        start, end = 30 * (page-1), 30 * page
        query = request.GET.get('q') or ''

        concepts = self._get_concepts(langcode, relation, query)
        items = self._set_reverse_urls(concepts[start:end], langcode, relation)

        data = {
            'items': list(items),
            'total_count': concepts.count(),
        }
        return self._get_response(data, 'success', 200)


class EditPropertyView(JsonResponseMixin, View):

    def post(self, request, langcode, id, name):
        try:
            language = Language.objects.get(code=langcode)
            concept = Concept.objects.get(id=id)
        except ObjectDoesNotExist:
            data = {"message": 'Object does not exist.'}
            return self._get_response(data, 'error', 400)
        form = PropertyForm(request.POST)
        if not form.is_valid():
            data = {"message": form.errors}
            return self._get_response(data, 'error', 400)
        field = Property.objects.filter(language=langcode,
                                        concept__id=id,
                                        name=name)

        published_field = field.filter(status=Property.PUBLISHED).first()
        pending_field = field.filter(status=Property.PENDING).first()

        if pending_field:
            pending_field.value = form.cleaned_data['value']
            pending_field.save()
            field = pending_field

        else:
            is_resource = False
            if published_field:
                if published_field.value == form.cleaned_data['value']:
                    data = {"message": 'Value already used.'}
                    return self._get_response(data, 'error', 400)
                published_field.status = Property.DELETED_PENDING
                published_field.save()
                is_resource = published_field.is_resource

            version = Version.objects.create()
            # Todo: Remove when version is stable
            field = Property.objects.create(status=Property.PENDING,
                                            is_resource=is_resource,
                                            version_added=version,
                                            concept=concept,
                                            language=language,
                                            name=name,
                                            **form.cleaned_data)
        data = {"value": field.value}
        return self._get_response(data, 'success', 200)


class RestoreRelationView(JsonResponseMixin, ConceptMixin, View):

    def post(self, request, langcode, id, parent_id, rel_type):
        try:
            concept = Concept.objects.get(id=id)
            self._set_concept_model(rel_type, concept.namespace.heading)
            parent_concept = self.model.objects.get(id=parent_id)
        except ObjectDoesNotExist:
            data = {"message": 'Object does not exist.'}
            return self._get_response(data, 'error', 400)

        relation = Relation.objects.filter(
            source=concept,
            target=parent_concept,
            property_type__name=rel_type,
            status=Relation.DELETED_PENDING,
        ).first()

        if not relation:
            data = {"message": 'Object does not exist.'}
            return self._get_response(data, 'error', 400)

        relation.status = Relation.PUBLISHED
        relation.save()

        delete_url = reverse('delete_relation', kwargs={
            'langcode': langcode,
            'id': id,
            'parent_id': parent_id,
            'rel_type': rel_type,
        })
        data = {'delete_url': delete_url}

        return self._get_response(data, 'success', 200)


class DeleteRelationView(JsonResponseMixin, ConceptMixin, View):

    def post(self, request, langcode, id, parent_id, rel_type):
        try:
            concept = Concept.objects.get(id=id)
            self._set_concept_model(rel_type, concept.namespace.heading)
            parent_concept = self.model.objects.get(id=parent_id)
        except ObjectDoesNotExist:
            data = {"message": 'Object does not exist.'}
            return self._get_response(data, 'error', 400)

        relation = Relation.objects.filter(
            source=concept,
            target=parent_concept,
            property_type__name=rel_type,
            status__in=(Relation.PUBLISHED, Relation.PENDING)
        ).first()

        if not relation:
            data = {"message": 'Object does not exist.'}
            return self._get_response(data, 'error', 400)

        if relation.status == Relation.PUBLISHED:
            relation.status = Relation.DELETED_PENDING
            relation.save()
        elif relation.status == Relation.PENDING:
            relation.delete()

        restore_url = reverse('restore_relation', kwargs={
            'langcode': langcode,
            'id': id,
            'parent_id': parent_id,
            'rel_type': rel_type,
        })
        data = {'restore_url': restore_url}

        return self._get_response(data, 'success', 200)


class AddRelationView(JsonResponseMixin, ConceptMixin, View):

    def post(self, request, langcode, id, parent_id, rel_type):
        try:
            concept = Concept.objects.get(id=id)
            self._set_concept_model(rel_type, concept.namespace.heading)
            parent_concept = self.model.objects.get(id=parent_id)
        except ObjectDoesNotExist:
            data = {"message": 'Object does not exist.'}
            return self._get_response(data, 'error', 400)

        relations = Relation.objects.filter(
            source=concept, target=parent_concept,
            property_type__name=rel_type)
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
            theme_property = PropertyType.objects.get(name=rel_type)
            field = Relation(source=concept, target=parent_concept,
                             status=Property.PENDING, version_added=version,
                             property_type=theme_property)
            field.save()
        data = {}
        return self._get_response(data, 'success', 200)


class AddPropertyView(JsonResponseMixin, View):

    def post(self, request, langcode, id, name):
        try:
            language = Language.objects.get(code=langcode)
            concept = Concept.objects.get(id=id)
        except ObjectDoesNotExist:
            data = {"message": 'Object does not exist.'}
            return self._get_response(data, 'error', 400)

        form = PropertyForm(request.POST)
        if not form.is_valid():
            data = {"message": form.errors}
            return self._get_response(data, 'error', 400)
        prop = Property.objects.filter(status=Property.PENDING,
                                       language=language,
                                       concept=concept,
                                       name=name,
                                       value=form.cleaned_data['value'])
        if prop:
            data = {"message": 'Value must be unique.'}
            return self._get_response(data, 'error', 400)
        # TODO: Remove when version is stable
        version = Version.objects.create()
        field = Property.objects.create(status=Property.PENDING,
                                        version_added=version,
                                        language=language,
                                        concept=concept,
                                        name=name,
                                        **form.cleaned_data)
        delete_url = reverse('delete_property', kwargs={'pk': field.pk})

        data = {
            "value": field.value,
            "id": field.id,
            "status": field.status,
            "url": delete_url,
        }
        return self._get_response(data, 'success', 200)


class DeletePropertyView(JsonResponseMixin, View):

    def post(self, request, pk):
        try:
            field = Property.objects.get(pk=pk)
        except ObjectDoesNotExist:
            data = {"message": 'Object does not exist.'}
            return self._get_response(data, 'error', 400)

        # Soft delete for published records / hard delete for pending ones
        if field.status == Property.PUBLISHED:
            field.status = Property.DELETED_PENDING
            field.save()
        elif field.status == Property.PENDING:
            field.delete()

        return self._get_response({}, 'success', 200)


class AddForeignRelationView(JsonResponseMixin, ConceptMixin, View):

    def post(self, request, langcode, id):
        try:
            concept = Concept.objects.get(id=id)
            prop_type = PropertyType.objects.get(id=request.POST['rel_type'])
        except ObjectDoesNotExist:
            data = {"message": 'Object does not exist.'}
            return self._get_response(data, 'error', 400)
        form = ForeignRelationForm(request.POST)
        if form.is_valid():
            version = Version.objects.create()
            # TODO Remove version when stable
            new_relation = ForeignRelation.objects.create(
                version_added=version, property_type=prop_type,
                concept=concept, **form.cleaned_data)
            url_kwargs = {'langcode': langcode,
                          'id': id,
                          'relation_id': new_relation.id}
            data = {'id': new_relation.id,
                    'delete_url': reverse('delete_other', kwargs=url_kwargs)}
            return self._get_response(data, 'success', 200)
        data = {"message": form.errors}
        return self._get_response(data, 'error', 400)


class RestoreForeignRelationView(JsonResponseMixin, View):

    def post(self, request, langcode, id, relation_id):
        try:
            foreign_relation = ForeignRelation.objects.get(id=relation_id)
        except ObjectDoesNotExist:
            data = {"message": 'Object does not exist.'}
            return self._get_response(data, 'error', 400)

        foreign_relation.status = ForeignRelation.PUBLISHED
        foreign_relation.save()

        delete_url = reverse('delete_other', kwargs={
            'langcode': langcode,
            'id': id,
            'relation_id': relation_id,
        })

        data = {'delete_url': delete_url}

        return self._get_response(data, 'success', 200)


class DeleteForeignRelationView(JsonResponseMixin, View):

    def post(self, request, langcode, id, relation_id):
        try:
            foreign_relation = ForeignRelation.objects.get(id=relation_id)
        except ObjectDoesNotExist:
            data = {"message": 'Object does not exist.'}
            return self._get_response(data, 'error', 400)

        if foreign_relation.status == ForeignRelation.PUBLISHED:
            foreign_relation.status = ForeignRelation.DELETED_PENDING
            foreign_relation.save()
        elif foreign_relation.status == ForeignRelation.PENDING:
            foreign_relation.delete()

        restore_url = reverse('restore_other', kwargs={
            'langcode': langcode,
            'id': id,
            'relation_id': relation_id,
        })

        data = {'restore_url': restore_url}

        return self._get_response(data, 'success', 200)
