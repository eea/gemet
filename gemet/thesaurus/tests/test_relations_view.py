from django.urls import reverse

from .factories import (
    LanguageFactory,
    PropertyFactory,
    RelationFactory,
    PropertyTypeFactory,
    TermFactory,
    GroupFactory,
    UserFactory,
)
from . import GemetTest, ERROR_404
from gemet.thesaurus import DELETED_PENDING, PENDING, PUBLISHED
from gemet.thesaurus.utils import exp_encrypt, exp_decrypt
from urllib.parse import urlparse, parse_qs


class TestRelationsView(GemetTest):
    def setUp(self):
        self.group = GroupFactory()
        PropertyFactory(concept=self.group, value="Group")

        self.url = reverse(
            "relations", kwargs={"group_code": self.group.code, "langcode": "en"}
        )

    def test_group_with_no_member(self):
        resp = self.app.get(self.url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context["language"].code, "en")
        self.assertEqual(resp.pyquery(".content h3").text(), "Group")
        self.assertEqual(resp.pyquery(".content ul:eq(0) > li").size(), 0)

    def test_group_with_one_member(self):
        concept = TermFactory()
        PropertyFactory(concept=concept, value="Concept")

        pt1 = PropertyTypeFactory(name="groupMember", label="Group member")
        pt2 = PropertyTypeFactory(name="group", label="Group")
        RelationFactory(property_type=pt1, source=self.group, target=concept)
        RelationFactory(property_type=pt2, source=concept, target=self.group)

        resp = self.app.get(self.url)

        self.assertEqual(200, resp.status_int)
        self.assertEqual(resp.context["language"].code, "en")
        self.assertEqual(resp.pyquery(".content h3").text(), "Group")
        self.assertEqual(resp.pyquery(".content ul:eq(0) > li").size(), 1)
        self.assertEqual(
            resp.pyquery(".content ul:eq(0) > li a:eq(0)").attr("href"),
            u"{url}?exp={exp}".format(
                url=reverse(
                    "relations",
                    kwargs={
                        "langcode": "en",
                        "group_code": self.group.code,
                    },
                ),
                exp=exp_encrypt(str(concept.id)),
            ),
        )
        self.assertEqual(
            resp.pyquery(".content ul:eq(0) > " "li a:eq(0) i").attr("class"),
            "fa fa-plus",
        )

        self.assertEqual(
            resp.pyquery(".content ul:eq(0) > li a:eq(1)").attr("href"),
            reverse("concept", kwargs={"langcode": "en", "code": concept.code}),
        )
        self.assertEqual(
            resp.pyquery(".content ul:eq(0) > li a:eq(1)").text(), "Concept"
        )

    def test_expand_list_with_one_element(self):
        concept = TermFactory()

        PropertyFactory(concept=concept, value="Concept")

        pt1 = PropertyTypeFactory(name="groupMember", label="Group member")
        pt2 = PropertyTypeFactory(name="group", label="Group")

        RelationFactory(property_type=pt1, source=self.group, target=concept)
        RelationFactory(property_type=pt2, source=concept, target=self.group)

        resp = self.app.get(self.url)
        self.assertEqual(200, resp.status_int)

        concept_url = resp.pyquery(".toggle-collapse:eq(0)").attr("href")
        params = parse_qs(urlparse(concept_url).query)
        expand_text = params.get("exp").pop().replace(" ", "+")
        expand_text = exp_decrypt(expand_text)
        expand_list = expand_text.split("-")

        self.assertEqual(expand_list, [str(concept.id)])

    def test_expand_list(self):
        group1 = GroupFactory(code="10")
        concept = TermFactory()

        PropertyFactory(concept=group1, value="Group1")
        PropertyFactory(concept=concept, value="Concept")

        pt1 = PropertyTypeFactory(name="groupMember", label="Group member")
        pt2 = PropertyTypeFactory(name="group", label="Group")

        RelationFactory(property_type=pt1, source=self.group, target=group1)
        RelationFactory(property_type=pt2, source=group1, target=self.group)

        RelationFactory(property_type=pt1, source=group1, target=concept)
        RelationFactory(property_type=pt2, source=concept, target=group1)

        url = u"{url}?exp={exp}".format(
            url=reverse(
                "relations",
                kwargs={
                    "langcode": "en",
                    "group_code": self.group.code,
                },
            ),
            exp=exp_encrypt(str(group1.id)),
        )

        resp = self.app.get(url)
        self.assertEqual(200, resp.status_int)

        concept_url = resp.pyquery(".toggle-collapse:eq(1)").attr("href")
        params = parse_qs(urlparse(concept_url).query)
        expand_text = params.get("exp").pop().replace(" ", "+")
        expand_text = exp_decrypt(expand_text)
        expand_list = expand_text.split("-")

        self.assertEqual(expand_list, [str(group1.id), str(concept.id)])

    def test_404_error(self):
        concept = TermFactory()
        PropertyFactory(concept=concept, value="Concept")

        pt1 = PropertyTypeFactory(name="groupMember", label="Group member")
        pt2 = PropertyTypeFactory(name="group", label="Group")
        RelationFactory(property_type=pt1, source=self.group, target=concept)
        RelationFactory(property_type=pt2, source=concept, target=self.group)

        url = reverse(
            "relations", kwargs={"group_code": concept.code, "langcode": "en"}
        )
        resp = self.app.get(url, expect_errors=True)

        self.assertEqual(404, resp.status_int)
        self.assertEqual(ERROR_404, resp.pyquery(".error404 h1").text())


class TestRelationsViewWithUser(GemetTest):
    def setUp(self):
        self.group = GroupFactory()
        user = UserFactory()
        LanguageFactory()
        self.user = user.username
        self.group_name = PropertyFactory(
            concept=self.group, value="Group", status=PUBLISHED
        )

        self.url = reverse(
            "relations", kwargs={"group_code": self.group.code, "langcode": "en"}
        )

    def test_group_with_pending_name(self):
        self.group_name.status = DELETED_PENDING
        self.group_name.save()
        PropertyFactory(concept=self.group, value="NewGroup", status=PENDING)
        resp = self.app.get(self.url, user=self.user)
        self.assertEqual(resp.pyquery(".content h3").text(), "NewGroup")

    def test_pending_relations_are_displayed(self):
        concept = TermFactory()
        PropertyFactory(concept=concept, value="Concept", status=PUBLISHED)

        pt1 = PropertyTypeFactory(name="groupMember", label="Group member")
        pt2 = PropertyTypeFactory(name="group", label="Group")
        RelationFactory(
            property_type=pt1, source=self.group, target=concept, status=PENDING
        )
        RelationFactory(
            property_type=pt2, source=concept, target=self.group, status=PENDING
        )
        resp = self.app.get(self.url, user=self.user)
        self.assertEqual(resp.pyquery(".content ul:eq(0) > li").size(), 1)
        url = reverse(
            "relations",
            kwargs={
                "langcode": "en",
                "group_code": self.group.code,
            },
        )
        self.assertEqual(
            resp.pyquery(".content ul:eq(0) > li a:eq(0)").attr("href"),
            u"{url}?exp={exp}".format(url=url, exp=exp_encrypt(str(concept.id))),
        )
        self.assertEqual(
            resp.pyquery(".content ul:eq(0) > " "li a:eq(0) i").attr("class"),
            "fa fa-plus",
        )

        self.assertEqual(
            resp.pyquery(".content ul:eq(0) > li a:eq(1)").attr("href"),
            reverse("concept", kwargs={"langcode": "en", "code": concept.code}),
        )
        self.assertEqual(
            resp.pyquery(".content ul:eq(0) > li a:eq(1)").text(), "Concept"
        )

    def test_pending_name_of_concept_is_displayed(self):
        concept = TermFactory()
        PropertyFactory(concept=concept, value="OldConcept", status=DELETED_PENDING)
        PropertyFactory(concept=concept, value="NewConcept", status=PENDING)

        pt1 = PropertyTypeFactory(name="groupMember", label="Group member")
        pt2 = PropertyTypeFactory(name="group", label="Group")
        RelationFactory(
            property_type=pt1, source=self.group, target=concept, status=PENDING
        )
        RelationFactory(
            property_type=pt2, source=concept, target=self.group, status=PENDING
        )
        resp = self.app.get(self.url, user=self.user)
        self.assertEqual(
            resp.pyquery(".content ul:eq(0) > li a:eq(1)").text(), "NewConcept"
        )
