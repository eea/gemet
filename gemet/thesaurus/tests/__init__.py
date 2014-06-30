from django_webtest import WebTest


class GemetTest(WebTest):
    fixtures = ['testing.json']
