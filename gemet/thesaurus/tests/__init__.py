from django_webtest import WebTest


ERROR_404 = "404. That's an error."


class GemetTest(WebTest):
    fixtures = ['testing.json']
