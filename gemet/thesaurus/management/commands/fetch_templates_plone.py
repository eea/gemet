import logging
import os
import requests

from django.core.management.base import BaseCommand
from django.conf import settings
from bs4 import BeautifulSoup, Tag

HEAD_URL = settings.PLONE_URL + '/external-template-head'
HEADER_URL = settings.PLONE_URL + '/external-template-header'
FOOTER_URL = settings.PLONE_URL + '/external-template-footer'



def prepare_html(html):
    html = html.replace('href="/', 'href="' + settings.PLONE_URL + '/')
    html = html.replace('src="/', 'src="' + settings.PLONE_URL + '/')
    html = html.replace('href="http://localhost:3080/', 'href="' + settings.PLONE_URL + '/')
    breadcrumbs = '<li id="breadcrumbs-home"><a href="https://plone5demo.eionet.europa.eu">Eionet</a></li>' + \
                  '<li id="breadcrumbs-1"><span id="breadcrumbs-current">GEMET</span></li>'
    breadcrumbs_old = '<li id="breadcrumbs-home"><a href="https://plone5demo.eionet.europa.eu">Eionet</a></li>'
    html = html.replace(breadcrumbs_old, breadcrumbs)
    # Replace site id for Matomo
    tracking_old = '_paq.push([\'setSiteId\', \'42\'])'
    tracking_new = '_paq.push([\'setSiteId\', \'38\'])'
    html = html.replace(tracking_old, tracking_new)
    return html.encode('utf-8').strip()

def prepare_header(header_text):
    new_tag = header_text.new_tag("a", href="/auth/login", title="Log in")
    new_tag.string = "Log in"
    header_text.find("a", {"class": "pat-plone-modal"}).decompose()
    header_text.find("div", {"class": "login"}).find('ul').decompose()
    breadcrumb =  '<li id="breadcrumbs-1"><span id="breadcrumbs-current">GEMET</span></li>'
    header_text.find('ol').append(BeautifulSoup(breadcrumb, 'html.parser'))
    return header_text

class Command(BaseCommand):
    help = 'Get plone template and prepare it for use'

    def handle(self, *args, **options):
        plone_path = os.path.join(
            settings.BASE_DIR, 'gemet', 'thesaurus',
                               'templates', 'plone')

        header_files = [
            'head_cached.html',
            'before_login_cached.html',
            'beader_cached.html',
            'header_before_container_cached.html',
            'header_after_container_cached.html',
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
            header_text = prepare_header(BeautifulSoup(prepare_html(resp.text), features="html.parser"))
            
            head = header_text.find("head")
            HEAD = head.prettify().encode('utf-8')
            
            login = header_text.body.prettify().split('<div class="login">')
            BEFORE_LOGIN = login[0].encode('utf-8') + '<div class="login"><ul><li>'
            split_header_and_footer = login[1].split('<footer id="portal-footer-wrapper"')
            HEADER =  '</li></ul>' + split_header_and_footer[0].encode('utf-8')

            split_before_and_after_container = split_header_and_footer[0].split("</main>")
            HEADER_BEFORE_CONTAINER = split_before_and_after_container[0].encode('utf-8')
            HEADER_AFTER_CONTAINER = "</main>" + split_before_and_after_container[1].encode('utf-8')
            FOOTER = '<footer id="portal-footer-wrapper"' + split_header_and_footer[1].encode('utf-8')

            templates = {
                'head.html': HEAD,
                'before_login.html': BEFORE_LOGIN,
                'header.html': HEADER,
                'header_before_container.html': HEADER_BEFORE_CONTAINER,
                'header_after_container.html': HEADER_AFTER_CONTAINER,
                'footer.html': FOOTER,
            }
        else:
            files = [
                'head.html',
                'before_login.html',
                'header.html',
                'header_before_container.html',
                'header_after_container.html',
                'footer.html',
            ]
            templates = {}
            for template, file_name in zip(files, header_files):
                with open(os.path.join(plone_path, file_name)) as f:
                    templates[template] = f.read()
            logger = logging.getLogger('django')
            logger.info('Plone templates were taken from cache.')

        for template_name, content in templates.iteritems():
            template_path = os.path.join(plone_path, template_name)
            with open(template_path, 'w') as f:
                f.write(content)
