from datetime import datetime
import json

from django.contrib.auth import mixins
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.views import View
from django.urls import reverse
from django.shortcuts import redirect, render

from gemet.thesaurus import EDIT_URL_NAMES, FOREIGN_RELATION_TYPES
from gemet.thesaurus import PENDING, PUBLISHED, DELETED, DELETED_PENDING
from gemet.thesaurus import SOURCE_RELATION_TO_TARGET
from gemet.thesaurus import models
from gemet.thesaurus.forms import ConceptForm, PropertyForm, ForeignRelationForm
from gemet.thesaurus.forms import VersionForm
from gemet.thesaurus.utils import get_new_code
from gemet.thesaurus.views import GroupView, SuperGroupView, TermView, ThemeView
from gemet.thesaurus.views import HeaderMixin, VersionMixin
from gemet.thesaurus.utils import get_form_errors


class LoginRequiredMixin(mixins.LoginRequiredMixin):
    login_url = '/auth/login'


class GroupEditView(LoginRequiredMixin, GroupView):
    context_object_name = 'concept'
    template_name = "edit/group_edit.html"
    model = models.EditableGroup
    override_languages = False


class SuperGroupEditView(LoginRequiredMixin, SuperGroupView):
    context_object_name = 'concept'
    template_name = "edit/supergroup_edit.html"
    model = models.EditableSuperGroup
    override_languages = False


class TermEditView(LoginRequiredMixin, TermView):
    template_name = "edit/concept_edit.html"
    model = models.EditableTerm
    override_languages = False

    def get_object(self):
        term = super(TermEditView, self).get_object()
        if hasattr(term, 'default_definition'):
            if term.default_definition and hasattr(self, 'definition'):
                delattr(term, 'definition')
        return term

    def get_context_data(self, **kwargs):
        context = super(TermEditView, self).get_context_data(**kwargs)
        foreign_relation_types = models.PropertyType.objects.filter(
            name__in=FOREIGN_RELATION_TYPES)
        context.update({
            "foreign_relation_types": foreign_relation_types,
        })
        return context


class ThemeEditView(LoginRequiredMixin, ThemeView):
    template_name = "edit/theme_edit.html"
    model = models.EditableTheme
    context_object_name = 'concept'
    override_languages = False


class JsonResponseMixin(object):

    def _get_response(self, data, status, status_code):
        response = HttpResponse(json.dumps(data),
                                content_type="application/json")
        response.status = status
        response.status_code = status_code
        return response


class UnrelatedConcepts(LoginRequiredMixin, JsonResponseMixin, View):

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

    def _get_concepts(self, langcode, relation, target_namespace, query):
        return (
            models.Property.objects
            .filter(
                name='prefLabel',
                language__code=langcode,
                concept__namespace__heading=target_namespace,
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
        target_ns = SOURCE_RELATION_TO_TARGET.get(
            (self.concept.namespace.heading, relation), models.Term.NAMESPACE)

        page = int(request.GET.get('page', '1'))
        start, end = 30 * (page-1), 30 * page
        query = request.GET.get('q') or ''

        concepts = self._get_concepts(langcode, relation, target_ns, query)
        items = self._set_reverse_urls(concepts[start:end], langcode, relation)

        data = {
            'items': list(items),
            'total_count': concepts.count(),
        }
        return self._get_response(data, 'success', 200)


class EditPropertyView(LoginRequiredMixin, JsonResponseMixin, VersionMixin,
                       View):

    def post(self, request, langcode, id, name):
        try:
            language = models.Language.objects.get(code=langcode)
            concept = models.Concept.objects.get(id=id)
        except ObjectDoesNotExist:
            data = {"message": 'Object does not exist.'}
            return self._get_response(data, 'error', 400)

        form = PropertyForm(request.POST)
        if not form.is_valid():
            data = {"message": get_form_errors(form.errors)}
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

            field = models.Property.objects.create(
                status=PENDING,
                is_resource=is_resource,
                version_added=self.pending_version,
                concept=concept,
                language=language,
                name=name,
                **form.cleaned_data
            )
        data = {"value": field.value}
        return self._get_response(data, 'success', 200)


class AddRelationView(LoginRequiredMixin, JsonResponseMixin, VersionMixin,
                      View):

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
        relation = models.Relation(source=source, target=target,
                                   status=PENDING,
                                   version_added=self.pending_version,
                                   property_type=property_type)
        relation.save()
        data = {}
        return self._get_response(data, 'success', 200)


class DeleteRelationView(LoginRequiredMixin, JsonResponseMixin, View):

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


class RestoreRelationView(LoginRequiredMixin, JsonResponseMixin, View):

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


class AddPropertyView(LoginRequiredMixin, JsonResponseMixin, VersionMixin,
                      View):

    def post(self, request, langcode, id, name):
        try:
            language = models.Language.objects.get(code=langcode)
            concept = models.Concept.objects.get(id=id)
        except ObjectDoesNotExist:
            data = {"message": 'Object does not exist.'}
            return self._get_response(data, 'error', 400)

        form = PropertyForm(request.POST)
        if not form.is_valid():
            data = {"message": get_form_errors(form.errors)}
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

        field = models.Property.objects.create(
            status=PENDING,
            version_added=self.pending_version,
            language=language,
            concept=concept,
            name=name,
            **form.cleaned_data
        )
        delete_url = reverse('delete_property', kwargs={'pk': field.pk})

        data = {
            "value": field.value,
            "id": field.id,
            "status": field.status,
            "url": delete_url,
        }
        return self._get_response(data, 'success', 200)


class DeletePropertyView(LoginRequiredMixin, JsonResponseMixin, View):

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


class AddForeignRelationView(LoginRequiredMixin, JsonResponseMixin,
                             VersionMixin, View):

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
            new_relation = models.ForeignRelation.objects.create(
                version_added=self.pending_version, property_type=prop_type,
                concept=concept, **form.cleaned_data)
            delete_url = reverse('delete_other', kwargs={'pk': new_relation.id})
            data = {
                'id': new_relation.id,
                'delete_url': delete_url,
            }
            return self._get_response(data, 'success', 200)

        data = {"message": get_form_errors(form.errors)}
        return self._get_response(data, 'error', 400)


class RestoreForeignRelationView(LoginRequiredMixin, JsonResponseMixin, View):

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


class DeleteForeignRelationView(LoginRequiredMixin, JsonResponseMixin, View):

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


class AddConceptView(LoginRequiredMixin, HeaderMixin, VersionMixin, FormView):
    template_name = 'edit/concept_add.html'
    form_class = ConceptForm

    def form_valid(self, form):
        namespace = form.cleaned_data['namespace']
        new_concept = models.Concept(version_added=self.pending_version,
                                     namespace=namespace,
                                     status=PENDING)
        new_concept.code = get_new_code(namespace)
        new_concept.save()

        # create prefLabel property for the new concept
        models.Property.objects.create(status=PENDING,
                                       version_added=self.pending_version,
                                       concept=new_concept,
                                       language=self.language,
                                       name='prefLabel',
                                       value=form.cleaned_data['name'])
        url_name = EDIT_URL_NAMES[namespace.heading]
        url = reverse(url_name, kwargs={'langcode': self.langcode,
                                        'code': new_concept.code})
        return redirect(url)


class ReleaseVersionView(LoginRequiredMixin, HeaderMixin, VersionMixin,
                         FormView):
    template_name = 'edit/release_version.html'
    form_class = VersionForm

    def form_valid(self, form):
        self.current_version.is_current = False
        self.current_version.save()

        self.pending_version.is_current = True
        self.pending_version.identifier = form.cleaned_data['version']
        self.pending_version.publication_date = datetime.now()
        self.pending_version.save()

        models.Version.objects.create(is_current=False)

        versionable_classes = models.VersionableModel.__subclasses__()
        for versionable_class in versionable_classes:
            self._change_status(versionable_class, PENDING, PUBLISHED)
            self._change_status(versionable_class, DELETED_PENDING, DELETED)

        url = reverse('themes', kwargs={'langcode': self.langcode})
        return redirect(url)

    def _change_status(self, model_cls, old_status, new_status):
        model_cls.objects.filter(status=old_status).update(status=new_status)


class HistoryChangesView(LoginRequiredMixin, HeaderMixin, VersionMixin,
                         TemplateView):
    template_name = 'edit/history_of_changes.html'

    def get_context_data(self, **kwargs):
        context = super(HistoryChangesView, self).get_context_data(**kwargs)

        new_concepts = models.Concept.objects.filter(status=PENDING)\
            .order_by('namespace')
        concepts = []
        for concept in new_concepts:
            concept_with_name = models.Property.objects\
                .filter(concept__id=concept.id,
                        name='prefLabel',
                        status=PENDING)\
                .values('concept__id',
                        'value',
                        'concept__namespace__heading').first()
            if not concept_with_name:
                continue
            url = concept.get_absolute_url(self.langcode)
            concept_with_name.update({'url': url})
            concepts.append(concept_with_name)

        published_concepts = models.Concept.objects.filter(
            status=PUBLISHED).select_related('namespace')
        old_concepts = (
            set(published_concepts
                .filter(properties__status__in=[PENDING, DELETED_PENDING]))
            |
            set(published_concepts
                .filter(
                    source_relations__status__in=[PENDING, DELETED_PENDING]))
            |
            set(published_concepts
                .filter(
                    foreign_relations__status__in=[PENDING, DELETED_PENDING]))
        )

        for concept in old_concepts:
            concept.set_attributes(self.langcode, ['prefLabel'])
            concept.url = reverse(
                EDIT_URL_NAMES[concept.namespace.heading],
                kwargs={
                    'langcode': self.langcode,
                    'code': concept.code,
                }
            )

        context.update({
            'new_concepts': concepts,
            'old_concepts': old_concepts,
        })
        return context


class ConceptChangesView(LoginRequiredMixin, View):

    def get(self, request, langcode, id):
        concept = models.Concept.objects.get(id=id)
        language = models.Language.objects.get(code=langcode)
        concept_details = {'concept_id': concept.id}
        properties = concept.properties\
            .filter(status__in=[PENDING, DELETED_PENDING],
                    language=language)\
            .order_by('name', 'status')
        for concept_property in properties:
            if concept_property.name in concept_details.keys():
                concept_details[concept_property.name].append(concept_property)
            else:
                concept_details[concept_property.name] = [concept_property]
        relations = concept.source_relations.filter(
            status__in=[PENDING, DELETED_PENDING])
        relations = relations.values('status',
                                     'target__id',
                                     'property_type__name')
        for relation in relations:
            target_name = models.Property.objects.filter(
                concept__id=relation['target__id'],
                name='prefLabel',
                language=language,
                status__in=[PENDING, PUBLISHED, DELETED_PENDING]).first()
            if target_name:
                target_name = target_name.value
            else:
                target_name = 'Name not available'
            target_relation = {
                'target': target_name,
                'property_type': relation['property_type__name'],
                'status': relation['status']
            }
            relation_type = relation['property_type__name']
            if relation_type in concept_details.keys():
                concept_details[relation_type].append(target_relation)
            else:
                concept_details[relation_type] = [target_relation]
        foreign_relations = concept.foreign_relations.filter(
            status__in=[PENDING, DELETED_PENDING]).order_by('property_type')
        concept_details['foreign_relations'] = foreign_relations
        concept_details['namespace'] = concept.namespace.heading
        return render(request, 'edit/bits/concept_changes.html',
                      concept_details)
