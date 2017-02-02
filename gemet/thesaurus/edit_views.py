from django.http import HttpResponse
from django.views import View

from gemet.thesaurus.models import Concept, Language, Property

import json


class EditPropertyView(View):

    def post(self, request):

        field = Property.objects.filter(language=request.POST['lang'],
                                        concept__code=request.POST['concept'],
                                        name=request.POST['type'])

        published_field = field.filter(status=1).first()
        pending_field = field.filter(status=0).first()

        if pending_field:
            pending_field.value = request.POST['value']
            pending_field.save()
            field = pending_field

        else:
            language = Language.objects.get(code=request.POST['lang'])
            concept = Concept.objects.get(code=request.POST['concept'])

            field = Property.objects.create(
                language=language, concept=concept, name=request.POST['type'],
                value=request.POST['value'], status=0,
                is_resource=published_field.is_resource or False)

        return HttpResponse(
            json.dumps({"data": "success", "status_code": "200",
                        "value": field.value}),
            content_type="application/json"
        )

