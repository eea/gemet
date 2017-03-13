import json

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, Http404
from django.views import View
from django.urls import reverse
from django.shortcuts import redirect, render
from gemet.thesaurus.definitions import EDIT_URL_NAMES, FOREIGN_RELATION_TYPES
from gemet.thesaurus.definitions import RELATION_TYPES
from gemet.thesaurus.forms import ConceptForm
from gemet.thesaurus.models import Concept, ForeignRelation, Group
from gemet.thesaurus.models import Language, Property, PropertyType
from gemet.thesaurus.models import Relation, SuperGroup, Theme
from gemet.thesaurus.models import Term, Version, EditableGroup, EditableTerm
from gemet.thesaurus.models import EditableTheme
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
                    status__in=(Relation.PENDING, Relation.PUBLISHED,
                                Relation.DELETED_PENDING),
                )
                .values_list('target_id', flat=True)
            )
            .extra(select={'name': 'value', 'id': 'concept_id'},
                   order_by=['name'])
            .values('name', 'id', 'concept__code')
        )

    def get(self, request, langcode, id, relation):
        self.concept = Concept.objects.get(id=id)
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

            version = Version.under_work()
            field = Property.objects.create(status=Property.PENDING,
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
            source = Concept.objects.get(id=source_id)
            target = Concept.objects.get(id=target_id)
        except ObjectDoesNotExist:
            data = {"message": 'Object does not exist.'}
            return self._get_response(data, 'error', 400)

        relation = (
            Relation.objects
            .filter(source=source, target=target,
                    property_type__name=relation_type)
            .exclude(status=Property.DELETED)
        )
        # This case should't appear for a request made from the web interface
        if relation.exists():
            data = {"message": 'A relation between the objects exists.'}
            return self._get_response(data, 'error', 400)

        property_type = PropertyType.objects.get(name=relation_type)
        version = Version.under_work()
        relation = Relation(source=source, target=target,
                            status=Property.PENDING, version_added=version,
                            property_type=property_type)
        relation.save()
        data = {}
        return self._get_response(data, 'success', 200)


class DeleteRelationView(JsonResponseMixin, View):

    def post(self, request, source_id, target_id, relation_type):
        try:
            source = Concept.objects.get(id=source_id)
            target = Concept.objects.get(id=target_id)
        except ObjectDoesNotExist:
            data = {"message": 'Object does not exist.'}
            return self._get_response(data, 'error', 400)

        relation = Relation.objects.filter(
            source=source,
            target=target,
            property_type__name=relation_type,
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
            'source_id': source_id,
            'target_id': target_id,
            'relation_type': relation_type,
        })
        data = {'restore_url': restore_url}
        return self._get_response(data, 'success', 200)


class RestoreRelationView(JsonResponseMixin, View):

    def post(self, request, source_id, target_id, relation_type):
        try:
            source = Concept.objects.get(id=source_id)
            target = Concept.objects.get(id=target_id)
        except ObjectDoesNotExist:
            data = {"message": 'Object does not exist.'}
            return self._get_response(data, 'error', 400)

        relation = Relation.objects.filter(
            source=source,
            target=target,
            property_type__name=relation_type,
            status=Relation.DELETED_PENDING,
        ).first()
        if not relation:
            data = {"message": 'Object does not exist.'}
            return self._get_response(data, 'error', 400)

        relation.status = Relation.PUBLISHED
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

        version = Version.under_work()
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


class AddForeignRelationView(JsonResponseMixin, View):

    def post(self, request, id):
        try:
            concept = Concept.objects.get(id=id)
            prop_type = PropertyType.objects.get(id=request.POST['rel_type'])
        except ObjectDoesNotExist:
            data = {"message": 'Object does not exist.'}
            return self._get_response(data, 'error', 400)

        form = ForeignRelationForm(request.POST)
        if form.is_valid():
            version = Version.under_work()
            new_relation = ForeignRelation.objects.create(
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
            foreign_relation = ForeignRelation.objects.get(id=pk)
        except ObjectDoesNotExist:
            data = {"message": 'Object does not exist.'}
            return self._get_response(data, 'error', 400)

        foreign_relation.status = ForeignRelation.PUBLISHED
        foreign_relation.save()

        delete_url = reverse('delete_other', kwargs={'pk': pk})

        data = {'delete_url': delete_url}
        return self._get_response(data, 'success', 200)


class DeleteForeignRelationView(JsonResponseMixin, View):

    def post(self, request, pk):
        try:
            foreign_relation = ForeignRelation.objects.get(pk=pk)
        except ObjectDoesNotExist:
            data = {"message": 'Object does not exist.'}
            return self._get_response(data, 'error', 400)

        if foreign_relation.status == ForeignRelation.PUBLISHED:
            foreign_relation.status = ForeignRelation.DELETED_PENDING
            foreign_relation.save()
        elif foreign_relation.status == ForeignRelation.PENDING:
            foreign_relation.delete()

        restore_url = reverse('restore_other', kwargs={'pk': pk})

        data = {'restore_url': restore_url}
        return self._get_response(data, 'success', 200)


class AddConceptView(View):

    def get(self, request, langcode):
        form = ConceptForm()
        context = {
            'language': Language.objects.get(code=langcode),
            'form': form,
        }
        return render(request, 'edit/concept_add.html', context)

    def post(self, request, langcode):
        language = Language.objects.get(code=langcode)
        version = Version.under_work()
        form = ConceptForm(request.POST)
        if form.is_valid():
            namespace = form.cleaned_data['namespace']
            new_concept = Concept(version_added=version,
                                  namespace=namespace,
                                  status=Concept.PENDING)

            codes = (Concept.objects
                     .filter(namespace=namespace)
                     .exclude(code='')
                     .values_list('code', flat=True))
            new_code = max(map(int, codes)) + 1
            new_concept.code = unicode(new_code)
            new_concept.save()
            # create prefLabel property for the new concept
            Property.objects.create(status=Property.PENDING,
                                    version_added=version,
                                    concept=new_concept,
                                    language=language,
                                    name='prefLabel',
                                    value=form.cleaned_data['name'])
            url_name = EDIT_URL_NAMES[namespace.heading]
            url = reverse(url_name, kwargs={'langcode': langcode,
                                            'code': new_code})
            return redirect(url)
