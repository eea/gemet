import logging
import os
import requests

from django.core.management.base import BaseCommand
from django.conf import settings

HEADER_URL = settings.ZOPE_URL + '/standard_html_header'
FOOTER_URL = settings.ZOPE_URL + '/standard_html_footer'


def prepare_html(html):
    html = html.replace('href="/', 'href="' + settings.ZOPE_URL + '/')
    html = html.replace('src="/', 'src="' + settings.ZOPE_URL + '/')
    breadcrumbs = '<div class="breadcrumbitem">' + \
        '<a href="{}">Eionet</a></div>'.format(settings.ZOPE_URL) + \
        '<div class="breadcrumbitemlast">GEMET</div>'
    breadcrumbs_old = '<div class="breadcrumbitemlast">' + \
        'Eionet</div>'
    html = html.replace(breadcrumbs_old, breadcrumbs)
    return html


class Command(BaseCommand):
    help = 'Get zope template and prepare it for use'

    def handle(self, *args, **options):
        zope_path = os.path.join(
            settings.BASE_DIR, 'gemet', 'thesaurus', 'templates', 'zope')

        header_files = [
            'header_before_title_cached.html',
            'header_after_title_cached.html',
            'header_before_login_cached.html',
            'header_after_login_cached.html',
            'footer_cached.html',
        ]

        try:
            failed = False
            resp = requests.get(HEADER_URL)
            if resp.status_code != 200:
                failed = True
        except requests.exceptions.ConnectionError:
            failed = True

        if not failed:
            header_text = prepare_html(resp.text)

            title_start = header_text.find('<title>')
            title_end = header_text.find('</title>')
            head_end = header_text.find('</head>')
            login_start = header_text.find('<a id="loginlink"')
            login_end = header_text.find('<a id="printlink"')

            HEADER_BEFORE_TITLE = header_text[:title_start + len('<title>')]
            HEADER_AFTER_TITLE = header_text[title_end:head_end]
            HEADER_BEFORE_LOGIN = header_text[head_end:login_start]
            HEADER_AFTER_LOGIN = header_text[login_end:]

            resp = requests.get(FOOTER_URL)
            FOOTER_TEXT = prepare_html(resp.text)
            templates = {
                'header_before_title.html': HEADER_BEFORE_TITLE,
                'header_after_title.html': HEADER_AFTER_TITLE,
                'header_before_login.html': HEADER_BEFORE_LOGIN,
                'header_after_login.html': HEADER_AFTER_LOGIN,
                'footer.html': FOOTER_TEXT,
            }
        else:
            files = ['header_before_title.html', 'header_after_title.html',
                     'header_before_login.html', 'header_after_login.html',
                     'footer.html']
            templates = {}
            for template, file_name in zip(files, header_files):
                with open(os.path.join(zope_path, file_name)) as f:
                    templates[template] = f.read()
            logger = logging.getLogger('django')
            logger.info('Zope templates were taken from cache.')

        for template_name, content in templates.iteritems():
            template_path = os.path.join(zope_path, template_name)
            with open(template_path, 'w') as f:
                f.write(content)
