from SimpleXMLRPCServer import SimpleXMLRPCDispatcher
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View


xmlrpcdispatcher = SimpleXMLRPCDispatcher(allow_none=False, encoding=None)


class ApiView(View):

    def post(self, request):
        content = xmlrpcdispatcher._marshaled_dispatch(request.body)
        response = HttpResponse(content_type='text/xml')
        response.write(content)
        return response

    def get(self, request):
        return HttpResponse("Nothing to see here")

    @classmethod
    def as_view(cls, **initkwargs):
        return csrf_exempt(super(ApiView, cls).as_view(**initkwargs))


# def getTopmostConcepts(concept_uri, other):
#     return [{'preferredLabel': {'string': 'test'}}]
#
#
# xmlrpcdispatcher.register_function(getTopmostConcepts, 'getTopmostConcepts')
xmlrpcdispatcher.register_introspection_functions()
xmlrpcdispatcher.register_multicall_functions()
