from django.core.urlresolvers import reverse

from gemet.thesaurus.tests import GemetTest


class TestGetAvailablethesauri(GemetTest):
    def setUp(self):
        self.url = reverse('api_root') + 'getAvailableThesauri'

    def test_get_available_thesauri(self):
        host = 'http://www.eionet.europa.eu/gemet/'
        thesauri = [
            {
                'name': 'Concepts',
                'uri': host + 'concept/',
                'version': 'GEMET - Concepts, version 3.1, 2012-07-20'
            },
            {
                'name': 'Super groups',
                'uri': host + 'supergroup/',
                'version': 'GEMET - Super groups, version 2.4, 2010-01-13'
            },
            {
                'name': 'Groups',
                'uri': host + 'group/',
                'version': 'GEMET - Groups, version 2.4, 2010-01-13'
            },
            {
                'name': 'Themes',
                'uri': host + 'theme/',
                'version': 'GEMET - Themes, version 2.4, 2010-01-13'
            },
            {
                'name': 'Inspire Themes',
                'uri': 'http://inspire.ec.europa.eu/theme/',
                'version': 'GEMET - INSPIRE themes, version 1.0, 2008-06-01'
            }
        ]

        resp = self.app.get(self.url)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        resp = resp.json
        self.assertEqual(len(resp), 5)
        for i in range(0, 5):
            self.assertEqual(resp[i]['version'], thesauri[i]['version'])
            self.assertEqual(resp[i]['uri'], thesauri[i]['uri'])
            self.assertEqual(resp[i]['name'], thesauri[i]['name'])
