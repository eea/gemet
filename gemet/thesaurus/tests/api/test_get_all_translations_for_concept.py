from urllib.parse import urlencode
from xmlrpc.client import Fault

from django.urls import reverse

from gemet.thesaurus.tests.factories import (
    PropertyFactory,
    TermFactory,
    LanguageFactory,
)
from gemet.thesaurus.tests import GemetTest


class TestGetAllTranslationsForConcept(GemetTest):
    def setUp(self):
        self.english = LanguageFactory()
        self.ENDPOINT_URI = "http://www.eionet.europa.eu"
        self.NS_ROOT = "http://www.eionet.europa.eu/gemet/"
        self.url = reverse("api_root", args=["getAllTranslationsForConcept"]) + "?"
        self.term = TermFactory()
        self._initialize(self.term, "prefLabel1", "definition1", self.english)

    def _initialize(self, concept, preflabel, definition, lang):
        PropertyFactory(
            concept=concept, name="prefLabel", value=preflabel, language=lang
        )
        PropertyFactory(
            concept=concept, name="definition", value=definition, language=lang
        )

    def _response_valid(self, status, content_type):
        self.assertEqual(200, status)
        self.assertEqual(content_type, "application/json")

    def test_invalid_concept_uri(self):
        self.assertRaises(
            Fault,
            self.app.get,
            self.url
            + urlencode(
                {"concept_uri": "BAD_CONCEPT_URI", "property_uri": "prefLabel"}
            ),
        )

    def test_missing_concept_uri(self):
        self.assertRaises(
            Fault, self.app.get, self.url + urlencode({"property_uri": "prefLabel"})
        )

    def test_invalid_property_uri(self):
        resp = self.app.get(
            self.url
            + urlencode(
                {
                    "concept_uri": self.NS_ROOT + "concept/" + self.term.code,
                    "property_uri": "BAD_PROPERTY_URI",
                }
            )
        )

        self.assertEqual([], resp.json)

    def test_missing_proeprty_uri(self):
        self.assertRaises(
            Fault,
            self.app.get,
            self.url
            + urlencode({"concept_uri": self.NS_ROOT + "concept/" + self.term.code}),
        )

    def test_two_translations(self):
        spanish = LanguageFactory(code="es", name="Spanish")
        self._initialize(self.term, "prefLabel2", "definition2", spanish)

        resp = self.app.get(
            self.url
            + urlencode(
                {
                    "concept_uri": self.NS_ROOT + "concept/" + self.term.code,
                    "property_uri": "prefLabel",
                }
            )
        )

        self._response_valid(resp.status_int, resp.content_type)
        resp = resp.json
        self.assertEqual(len(resp), 2)
        self.assertEqual(resp[0]["string"], "prefLabel1")
        self.assertEqual(resp[0]["language"], "en")
        self.assertEqual(resp[1]["string"], "prefLabel2")
        self.assertEqual(resp[1]["language"], "es")

    def test_property_uri_with_hashtag(self):
        resp = self.app.get(
            self.url
            + urlencode(
                {
                    "concept_uri": self.NS_ROOT + "concept/" + self.term.code,
                    "property_uri": "http://www.w3.org/2004/02/skos/core#prefLabel",
                }
            )
        )

        self._response_valid(resp.status_int, resp.content_type)
        resp = resp.json
        self.assertEqual(len(resp), 1)
        self.assertEqual(resp[0]["string"], "prefLabel1")
        self.assertEqual(resp[0]["language"], "en")
