from django.shortcuts import render
from gemet.thesaurus.models import Namespace, Property, Language


def themes_list(request):
    
    if request.method=='GET':
        #try to get the selected language. default is 'en'
        try:
            lang_code = request.GET['langcode']
        except:
            lang_code = 'en'
        
        #get all languages
        langs = Language.objects.all()
    
        ns = Namespace.objects.get(heading='Themes')
        themes = Property.objects.filter(concept__namespace=ns, name='prefLabel', language=lang_code)
    
        return render(request, 'themes_list.html', {'themes': themes,
                                                    'langs': langs,
                                                    'lang_code': lang_code})
