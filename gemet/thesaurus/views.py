from django.shortcuts import render
from gemet.thesaurus.models import Namespace, Property


def themes_list(request):
    ns = Namespace.objects.get(heading='Themes')
    themes = Property.objects.filter(concept__namespace=ns, name='prefLabel')

    return render(request, 'themes_list.html', {'themes': themes})
