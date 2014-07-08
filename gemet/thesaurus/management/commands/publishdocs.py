from django.core.management.base import BaseCommand
from bs4 import BeautifulSoup


class Command(BaseCommand):
    help = 'Publish the API documentation on the website'

    def handle(self, *args, **options):
        try:
            soup = BeautifulSoup(open('docs/new_api/build/html/api.html'))
            with open('gemet/thesaurus/templates/api.html', 'w') as f:
                apidoc = soup.find("div", {'class': 'documentwrapper'})
                f.write(apidoc.prettify().encode('utf-8'))
        except IOError:
            self.stderr.write('API documentation not found. Please go to '
                              'docs/new_api/ and run `make html`.')
