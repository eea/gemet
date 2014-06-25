from django.templatetags.static import static
import requests
from django.conf import settings

ZOPE_URL = 'http://eionet.europa.eu'
HEADER_URL = ZOPE_URL + '/standard_html_header'
FOOTER_URL = ZOPE_URL + '/standard_html_footer'

HEADER_TEXT = ''
FOOTER_TEXT = ''


class LayoutMiddleware(object):

    def process_request(self, request):
        global HEADER_TEXT, FOOTER_TEXT
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        resp = requests.get(HEADER_URL, headers={'Authorization': auth_header})
        HEADER_TEXT = prepare_html(resp.text)
        resp = requests.get(FOOTER_URL, headers={'Authorization': auth_header})
        FOOTER_TEXT = prepare_html(resp.text)
        return None


def layout_context_processor(request):
    if settings.USE_ZOPE_LAYOUT:
        return {'header_text': HEADER_TEXT, 'footer_text': FOOTER_TEXT,
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
    html = html.replace('</head>', css_url + '</head>')
    html = html.replace('</body>', jquery_url + js_url + '</body>')
    return html
