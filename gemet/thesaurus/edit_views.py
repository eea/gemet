from django.http import HttpResponse
from django.views import View

from gemet.thesaurus.models import Concept, Language, Property, Version
from gemet.thesaurus.forms import PropertyForm
import json


class EditPropertyView(View):

    def post(self, request):
        form = PropertyForm(request.POST)
        if not form.is_valid():
            response = HttpResponse(json.dumps({"errors": form.errors}),
                                    content_type="application/json")
            response.status_code = 400
            return response

        field = Property.objects.filter(language=request.POST['language'],
                                        concept__code=request.POST['concept'],
                                        name=request.POST['name'])

        published_field = field.filter(status=1).first()
        pending_field = field.filter(status=0).first()

        if pending_field:
            pending_field.value = request.POST['value']
            pending_field.save()
            field = pending_field

        else:
            language = Language.objects.get(code=request.POST['language'])
            concept = Concept.objects.get(code=request.POST['concept'])

            is_resource = False
            if published_field:
                is_resource = published_field.is_resource

            version = Version.objects.create()
            # Todo: Remove when version is stable
            field = Property.objects.create(
                language=language, concept=concept,
                name=request.POST['name'], value=request.POST['value'],
                status=0,
                is_resource=is_resource,
                version_added=version)

        return HttpResponse(
            json.dumps({"data": "success", "status_code": "200",
                        "value": field.value}),
            content_type="application/json"
        )

