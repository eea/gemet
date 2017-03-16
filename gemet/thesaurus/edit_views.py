import json

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.views import View
from django.urls import reverse
from django.shortcuts import redirect, render

from gemet.thesaurus import EDIT_URL_NAMES, FOREIGN_RELATION_TYPES
from gemet.thesaurus import PENDING, PUBLISHED, DELETED, DELETED_PENDING
from gemet.thesaurus import models
from gemet.thesaurus.forms import ConceptForm, PropertyForm, ForeignRelationForm
from gemet.thesaurus.views import GroupView, SuperGroupView, TermView, ThemeView


class GroupEditView(GroupView):
    context_object_name = 'concept'
    template_name = "edit/group_edit.html"
    model = models.EditableGroup


class SuperGroupEditView(SuperGroupView):
    context_object_name = 'concept'
    template_name = "edit/supergroup_edit.html"
    model = models.EditableSuperGroup


class TermEditView(TermView):
    template_name = "edit/concept_edit.html"
    model = models.EditableTerm

    def get_context_data(self, **kwargs):
        context = super(TermEditView, self).get_context_data(**kwargs)
        foreign_relation_types = models.PropertyType.objects.filter(
            name__in=FOREIGN_RELATION_TYPES)
        context.update({
            "foreign_relation_types": foreign_relation_types,
        })
        return context


class ThemeEditView(ThemeView):
    template_name = "edit/theme_edit.html"
    model = models.EditableTheme
    context_object_name = 'concept'


class JsonResponseMixin(object):

    def _get_response(self, data, status, status_code):
        response = HttpResponse(json.dumps(data),
                                content_type="application/json")
        response.status = status
        response.status_code = status_code
        return response


class UnrelatedConcepts(JsonResponseMixin, View):

    def _set_reverse_urls(self, concepts, langcode, relation):
        for concept in concepts:
            url_kwargs = {
                'source_id': self.concept.id,
                'target_id': concept['id'],
                'relation_type': relation,
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
            models.Property.objects
            .filter(
                name='prefLabel',
                language__code=langcode,
                concept__namespace__heading=self.concept.namespace.heading,
                status__in=(PENDING, PUBLISHED),
                value__istartswith=query,
            )
            .exclude(
                concept_id__in=self.concept.source_relations.filter(
                    property_type__name=relation,
                    status__in=(PENDING, PUBLISHED, DELETED_PENDING),
                )
                .values_list('target_id', flat=True)
            )
            .extra(select={'name': 'value', 'id': 'concept_id'},
                   order_by=['name'])
            .values('name', 'id', 'concept__code')
        )

    def get(self, request, langcode, id, relation):
        self.concept = models.Concept.objects.get(id=id)

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
            language = models.Language.objects.get(code=langcode)
            concept = models.Concept.objects.get(id=id)
        except ObjectDoesNotExist:
            data = {"message": 'Object does not exist.'}
            return self._get_response(data, 'error', 400)

        form = PropertyForm(request.POST)
        if not form.is_valid():
            data = {"message": form.errors}
            return self._get_response(data, 'error', 400)

        field = models.Property.objects.filter(language=langcode,
                                               concept__id=id,
                                               name=name)

        published_field = field.filter(status=PUBLISHED).first()
        pending_field = field.filter(status=PENDING).first()

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
                published_field.status = DELETED_PENDING
                published_field.save()
                is_resource = published_field.is_resource

            version = models.Version.under_work()
            field = models.Property.objects.create(status=PENDING,
                                                   is_resource=is_resource,
                                                   version_added=version,
                                                   concept=concept,
                                                   language=language,
                                                   name=name,
                                                   **form.cleaned_data)
        data = {"value": field.value}
        return self._get_response(data, 'success', 200)


class AddRelationView(JsonResponseMixin, View):

    def post(self, request, source_id, target_id, relation_type):
        try:
            source = models.Concept.objects.get(id=source_id)
            target = models.Concept.objects.get(id=target_id)
        except ObjectDoesNotExist:
            data = {"message": 'Object does not exist.'}
            return self._get_response(data, 'error', 400)

        relation = (
            models.Relation.objects
            .filter(source=source, target=target,
                    property_type__name=relation_type)
            .exclude(status=DELETED)
        )
        # This case should't appear for a request made from the web interface
        if relation.exists():
            data = {"message": 'A relation between the objects exists.'}
            return self._get_response(data, 'error', 400)

        property_type = models.PropertyType.objects.get(name=relation_type)
        version = models.Version.under_work()
        relation = models.Relation(source=source, target=target,
                                   status=PENDING, version_added=version,
                                   property_type=property_type)
        relation.save()
        data = {}
        return self._get_response(data, 'success', 200)


class DeleteRelationView(JsonResponseMixin, View):

    def post(self, request, source_id, target_id, relation_type):
        try:
            source = models.Concept.objects.get(id=source_id)
            target = models.Concept.objects.get(id=target_id)
        except ObjectDoesNotExist:
            data = {"message": 'Object does not exist.'}
            return self._get_response(data, 'error', 400)

        relation = models.Relation.objects.filter(
            source=source,
            target=target,
            property_type__name=relation_type,
            status__in=(PUBLISHED, PENDING)
        ).first()
        if not relation:
            data = {"message": 'Object does not exist.'}
            return self._get_response(data, 'error', 400)

        if relation.status == PUBLISHED:
            relation.status = DELETED_PENDING
            relation.save()
        elif relation.status == PENDING:
            relation.delete()

        restore_url = reverse('restore_relation', kwargs={
            'source_id': source_id,
            'target_id': target_id,
            'relation_type': relation_type,
        })
        data = {'restore_url': restore_url}
        return self._get_response(data, 'success', 200)


class RestoreRelationView(JsonResponseMixin, View):

    def post(self, request, source_id, target_id, relation_type):
        try:
            source = models.Concept.objects.get(id=source_id)
            target = models.Concept.objects.get(id=target_id)
        except ObjectDoesNotExist:
            data = {"message": 'Object does not exist.'}
            return self._get_response(data, 'error', 400)

        relation = models.Relation.objects.filter(
            source=source,
            target=target,
            property_type__name=relation_type,
            status=DELETED_PENDING,
        ).first()
        if not relation:
            data = {"message": 'Object does not exist.'}
            return self._get_response(data, 'error', 400)

        relation.status = PUBLISHED
        relation.save()

        delete_url = reverse('delete_relation', kwargs={
            'source_id': source_id,
            'target_id': target_id,
            'relation_type': relation_type,
        })
        data = {'delete_url': delete_url}
        return self._get_response(data, 'success', 200)


class AddPropertyView(JsonResponseMixin, View):

    def post(self, request, langcode, id, name):
        try:
            language = models.Language.objects.get(code=langcode)
            concept = models.Concept.objects.get(id=id)
        except ObjectDoesNotExist:
            data = {"message": 'Object does not exist.'}
            return self._get_response(data, 'error', 400)

        form = PropertyForm(request.POST)
        if not form.is_valid():
            data = {"message": form.errors}
            return self._get_response(data, 'error', 400)

        prop = (
            models.Property.objects.filter(
                language=language,
                concept=concept,
                name=name,
                value=form.cleaned_data['value'],
            )
            .exclude(status=DELETED)
        )
        if prop.exists():
            data = {"message": 'A property with this value already exists.'}
            return self._get_response(data, 'error', 400)

        version = models.Version.under_work()
        field = models.Property.objects.create(status=PENDING,
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
            field = models.Property.objects.get(pk=pk)
        except ObjectDoesNotExist:
            data = {"message": 'Object does not exist.'}
            return self._get_response(data, 'error', 400)

        # Soft delete for published records / hard delete for pending ones
        if field.status == PUBLISHED:
            field.status = DELETED_PENDING
            field.save()
        elif field.status == PENDING:
            field.delete()

        return self._get_response({}, 'success', 200)


class AddForeignRelationView(JsonResponseMixin, View):

    def post(self, request, id):
        try:
            concept = models.Concept.objects.get(id=id)
            proptype_id = request.POST.get('rel_type')
            prop_type = models.PropertyType.objects.get(id=proptype_id)
        except ObjectDoesNotExist:
            data = {"message": 'Object does not exist.'}
            return self._get_response(data, 'error', 400)

        form = ForeignRelationForm(request.POST)
        if form.is_valid():
            version = models.Version.under_work()
            new_relation = models.ForeignRelation.objects.create(
                version_added=version, property_type=prop_type,
                concept=concept, **form.cleaned_data)
            delete_url = reverse('delete_other', kwargs={'pk': new_relation.id})
            data = {
                'id': new_relation.id,
                'delete_url': delete_url,
            }
            return self._get_response(data, 'success', 200)

        data = {"message": form.errors}
        return self._get_response(data, 'error', 400)


class RestoreForeignRelationView(JsonResponseMixin, View):

    def post(self, request, pk):
        try:
            foreign_relation = models.ForeignRelation.objects.get(
                pk=pk,
                status=DELETED_PENDING,
            )
        except ObjectDoesNotExist:
            data = {"message": 'Object does not exist.'}
            return self._get_response(data, 'error', 400)

        foreign_relation.status = PUBLISHED
        foreign_relation.save()

        delete_url = reverse('delete_other', kwargs={'pk': pk})

        data = {'delete_url': delete_url}
        return self._get_response(data, 'success', 200)


class DeleteForeignRelationView(JsonResponseMixin, View):

    def post(self, request, pk):
        try:
            foreign_relation = models.ForeignRelation.objects.get(pk=pk)
        except ObjectDoesNotExist:
            data = {"message": 'Object does not exist.'}
            return self._get_response(data, 'error', 400)

        if foreign_relation.status == PUBLISHED:
            foreign_relation.status = DELETED_PENDING
            foreign_relation.save()
        elif foreign_relation.status == PENDING:
            foreign_relation.delete()

        restore_url = reverse('restore_other', kwargs={'pk': pk})

        data = {'restore_url': restore_url}
        return self._get_response(data, 'success', 200)


class AddConceptView(View):

    def get(self, request, langcode):
        form = ConceptForm()
        context = {
            'language': models.Language.objects.get(code=langcode),
            'form': form,
        }
        return render(request, 'edit/concept_add.html', context)

    def post(self, request, langcode):
        language = models.Language.objects.get(code=langcode)
        version = models.Version.under_work()
        form = ConceptForm(request.POST)
        if form.is_valid():
            namespace = form.cleaned_data['namespace']
            new_concept = models.Concept(version_added=version,
                                         namespace=namespace,
                                         status=PENDING)

            codes = (models.Concept.objects
                     .filter(namespace=namespace)
                     .exclude(code='')
                     .values_list('code', flat=True))
            new_code = max(map(int, codes)) + 1
            new_concept.code = unicode(new_code)
            new_concept.save()
            # create prefLabel property for the new concept
            models.Property.objects.create(status=PENDING,
                                           version_added=version,
                                           concept=new_concept,
                                           language=language,
                                           name='prefLabel',
                                           value=form.cleaned_data['name'])
            url_name = EDIT_URL_NAMES[namespace.heading]
            url = reverse(url_name, kwargs={'langcode': langcode,
                                            'code': new_code})
            return redirect(url)
