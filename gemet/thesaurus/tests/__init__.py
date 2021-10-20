from django_webtest import WebTest

ERROR_404 = "Error (404)"


class GemetTest(WebTest):
    fixtures = ["testing.json"]
