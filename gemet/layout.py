from django.templatetags.static import static
import requests
from django.conf import settings

ZOPE_URL = 'http://eionet.europa.eu'
HEADER_URL = ZOPE_URL + '/standard_html_header'
FOOTER_URL = ZOPE_URL + '/standard_html_footer'

HEADER_TEXT_PREFFIX = ''
HEADER_TEXT_SUFFIX = ''


def layout_context_processor(request):
    if settings.USE_ZOPE_LAYOUT:
        global HEADER_TEXT_SUFFIX, HEADER_TEXT_PREFFIX, FOOTER_TEXT
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        resp = requests.get(HEADER_URL, headers={'Authorization': auth_header})
        header_text = prepare_html(resp.text)
        title_start = header_text.find('<title>')
        title_end = header_text.find('</title>')
        HEADER_TEXT_PREFFIX = header_text[:title_start + len('<title>')]
        HEADER_TEXT_SUFFIX = header_text[title_end:]
        resp = requests.get(FOOTER_URL, headers={'Authorization': auth_header})
        FOOTER_TEXT = prepare_html(resp.text)
        return {'header_text_preffix': HEADER_TEXT_PREFFIX,
                'header_text_suffix': HEADER_TEXT_SUFFIX,
                'footer_text': FOOTER_TEXT,
                'layout_template': 'layout_zope.html'}
    else:
        return {'layout_template': 'layout.html'}


def prepare_html(html):
    html = html.replace('href="/', 'href="' + ZOPE_URL + '/')
    html = html.replace('src="/', 'src="' + ZOPE_URL + '/')
    css_url = '<link rel="stylesheet" href="' + static('thesaurus/style.css') \
              + '" />'
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
    html = html.replace('</head>', css_url + '</head>')
    html = html.replace('</body>', jquery_url + js_url + '</body>')
    return html
