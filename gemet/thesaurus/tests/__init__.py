from django_webtest import WebTest


ERROR_404 = '404 Sorry, the requested page was not found.'


class GemetTest(WebTest):
    fixtures = ['testing.json']
