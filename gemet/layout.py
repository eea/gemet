from django.templatetags.static import static
import requests
from django.conf import settings

ZOPE_URL = 'http://eionet.europa.eu'
HEADER_URL = ZOPE_URL + '/standard_html_header'
FOOTER_URL = ZOPE_URL + '/standard_html_footer'


def layout_context_processor(request):
    if settings.USE_ZOPE_LAYOUT:
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        resp = requests.get(HEADER_URL, headers={'Authorization': auth_header})
        header_text = prepare_html(resp.text)
        title_start = header_text.find('<title>')
        title_end = header_text.find('</title>')
        head_end = header_text.find('</head>')
        HEADER_BEFORE_TITLE = header_text[:title_start + len('<title>')]
        HEADER_AFTER_TITLE = header_text[title_end:head_end]
        HEADER_END = header_text[head_end:]
        resp = requests.get(FOOTER_URL, headers={'Authorization': auth_header})
        FOOTER_TEXT = prepare_html(resp.text)
        return {'header_before_title': HEADER_BEFORE_TITLE,
                'header_after_title': HEADER_AFTER_TITLE,
                'header_end': HEADER_END,
                'footer_text': FOOTER_TEXT,
                'layout_template': 'layout_zope.html'}
    else:
        return {'layout_template': 'layout.html'}


def prepare_html(html):
    html = html.replace('href="/', 'href="' + ZOPE_URL + '/')
    html = html.replace('src="/', 'src="' + ZOPE_URL + '/')
    js_url = '<script src="' + static('thesaurus/main.js') + '"></script>'
    jquery_url = '<script src=' + \
        '"//ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js"' + \
        '></script>'
    breadcrumbs = '<div class="breadcrumbitem eionetaccronym">' + \
        '<a href="{zope_url}">Eionet</a></div>'.format(zope_url=ZOPE_URL) + \
        '<div class="breadcrumbitemlast">GEMET</div>'
    breadcrumbs_old = '<div class="breadcrumbitemlast eionetaccronym">' + \
        'Eionet</div>'
    html = html.replace(breadcrumbs_old, breadcrumbs)
    html = html.replace('</body>', jquery_url + js_url + '</body>')
    return html
