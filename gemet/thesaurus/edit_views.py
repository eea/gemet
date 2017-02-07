from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.views import View

from gemet.thesaurus.models import Concept, Language, Property, Version
from gemet.thesaurus.forms import PropertyForm
import json


class EditPropertyView(View):

    def post(self, request, *args, **kwargs):
        try:
            language = Language.objects.get(code=kwargs['langcode'])
            concept = Concept.objects.get(id=kwargs['concept_id'])
        except ObjectDoesNotExist:
            response = HttpResponse(json.dumps({
                                    "message": 'Object does not exist.'}),
                                    content_type="application/json")
            response.status = 'error'
            response.status_code = 400
            return response

        form = PropertyForm(request.POST)

        if not form.is_valid():
            response = HttpResponse(json.dumps({"message": form.errors}),
                                    content_type="application/json")
            response.status = 'error'
            response.status_code = 400
            return response
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

        response = HttpResponse(json.dumps({"value": field.value}),
                                content_type="application/json")
        response.status = 'success'
        response.status_code = 200
        return response
