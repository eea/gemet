from django.core.urlresolvers import reverse

from . import GemetTest
from gemet.thesaurus.tests import factories
from gemet.thesaurus.models import Concept, ForeignRelation, Group, Property
from gemet.thesaurus.models import Relation, SuperGroup, Theme, Version
from gemet.thesaurus import DELETED_PENDING, PENDING, PUBLISHED


class TestReleaseNewVersion(GemetTest):

    csrf_checks = False

    def setUp(self):
        self.language = factories.LanguageFactory()
        factories.TermFactory(status=PENDING)
        factories.PropertyFactory(status=PENDING)
        factories.PropertyFactory(status=DELETED_PENDING)
        factories.VersionFactory()
        factories.VersionFactory(identifier="", is_current=False)
        self.request_kwargs = {'langcode': self.language.code}
        user = factories.UserFactory()
        self.user = user.username

    def test_form_versions(self):
        url = reverse('release_version', kwargs=self.request_kwargs)
        response = self.app.get(url, user=self.user)
        minor_release, middle_release, major_release = (
            version[0] for version in
            response.context['form'].fields['version'].choices
        )
        self.assertEqual('1.0.1', minor_release)
        self.assertEqual('1.1.0', middle_release)
        self.assertEqual('2.0.0', major_release)

    def test_release_new_version(self):
        url = reverse('release_version', kwargs=self.request_kwargs)
        response = self.app.post(
            url, user=self.user,
            params={'version': '1.1.0', 'change_note': 'test'})
        self.assertEqual(302, response.status_code)
        new_published_version = Version.objects.get(identifier='1.1.0')
        old_version = Version.objects.get(identifier='1.0.0')
        self.assertTrue(new_published_version.is_current)
        self.assertEqual('test', new_published_version.change_note)
        self.assertFalse(old_version.is_current)
        self.assertEqual(0, Property.objects.filter(status=PENDING).count())
        self.assertEqual(0, Property.objects.filter(
            status=DELETED_PENDING
        ).count())
        self.assertEqual(0, Concept.objects.filter(status=PENDING).count())
        self.assertEqual(0, Concept.objects.filter(
            status=DELETED_PENDING
        ).count())


class TestReleaseNewVersionOtherConcepts(GemetTest):

    csrf_checks = False

    def setUp(self):
        self.language = factories.LanguageFactory()
        factories.VersionFactory()
        factories.VersionFactory(identifier="", is_current=False)
        factories.GroupFactory(status=PENDING)
        factories.ThemeFactory(status=PENDING)
        factories.SuperGroupFactory(status=PENDING)
        factories.RelationFactory(status=PENDING)
        factories.RelationFactory(status=DELETED_PENDING)
        factories.ForeignRelationFactory(status=PENDING)
        factories.ForeignRelationFactory(status=DELETED_PENDING)
        self.request_kwargs = {'langcode': self.language.code}
        user = factories.UserFactory()
        self.user = user.username

    def test_release_new_version(self):
        url = reverse('release_version', kwargs=self.request_kwargs)
        response = self.app.post(
            url, user=self.user,
            params={'version': '1.1.0', 'change_note': 'test'})
        self.assertEqual(302, response.status_code)
        new_published_version = Version.objects.get(identifier='1.1.0')
        old_version = Version.objects.get(identifier='1.0.0')
        self.assertEqual('test', new_published_version.change_note)
        self.assertTrue(new_published_version.is_current)
        self.assertFalse(old_version.is_current)
        self.assertEqual(0, Group.objects.filter(status=PENDING).count())
        self.assertEqual(0, SuperGroup.objects.filter(status=PENDING).count())
        self.assertEqual(0, Theme.objects.filter(status=PENDING).count())
        self.assertEqual(0, Relation.objects.filter(
            status=DELETED_PENDING
        ).count())
        self.assertEqual(0, Relation.objects.filter(
            status=PENDING).count())
        self.assertEqual(0, ForeignRelation.objects.filter(
            status=DELETED_PENDING
        ).count())


class TestChangesLog(GemetTest):

    csrf_checks = False

    def setUp(self):
        self.language = factories.LanguageFactory()
        self.new_concept = factories.TermFactory(status=PENDING)
        factories.PropertyFactory(status=PENDING,
                                  concept=self.new_concept)
        self.new_group = factories.GroupFactory(status=PENDING)
        factories.PropertyFactory(status=PENDING,
                                  concept=self.new_group)
        self.new_theme = factories.ThemeFactory(status=PENDING)
        factories.PropertyFactory(status=PENDING,
                                  concept=self.new_theme)
        self.old_concept = factories.TermFactory(status=PUBLISHED)
        self.old_group = factories.TermFactory(status=PUBLISHED)
        self.group_name = factories.PropertyFactory(status=PENDING,
                                                    concept=self.old_group)
        self.new_property = factories.PropertyFactory(status=PENDING,
                                                      concept=self.old_concept)
        factories.VersionFactory()
        factories.VersionFactory(identifier="", is_current=False)
        self.request_kwargs = {'langcode': self.language.code}
        user = factories.UserFactory()
        self.user = user.username

    def testChangesLog(self):
        url = reverse('change_log', kwargs=self.request_kwargs)
        response = self.app.get(url, user=self.user)
        self.assertTrue(200, response.status_code)
        self.assertEqual(3,
                         response.pyquery('.modified-container p').size())
        self.assertEqual(2,
                         response.pyquery('.modified-list.concept li').size())


class TestConceptChanges(GemetTest):

    csrf_checks = False

    def setUp(self):
        self.language = factories.LanguageFactory()
        self.concept = factories.TermFactory(status=PUBLISHED)
        self.group = factories.GroupFactory(status=PUBLISHED)
        self.concept_old_name = factories.PropertyFactory(
            status=DELETED_PENDING,
            concept=self.concept,
            value='old_name'
        )
        self.concept_new_name = factories.PropertyFactory(
            status=PENDING,
            concept=self.concept,
            value='new_name'
        )
        self.group_definition = factories.PropertyFactory(
            status=PENDING,
            concept=self.group,
            name='definition',
            value='new definition'
        )
        self.new_relation = factories.RelationFactory(
            status=PENDING,
            source=self.concept,
            target=self.group
        )

        factories.VersionFactory()
        factories.VersionFactory(identifier="", is_current=False)
        self.request_kwargs = {'langcode': self.language.code,
                               'id': self.concept.id}
        user = factories.UserFactory()
        self.user = user.username

    def test_concept_changes(self):
        url = reverse('concept_changes', kwargs=self.request_kwargs)
        response = self.app.get(url, user=self.user)
        self.assertEqual(self.concept_old_name.value,
                         response.pyquery('.prefLabel.status-3').html())
        self.assertEqual(self.concept_new_name.value,
                         response.pyquery('.prefLabel.status-0').html())

    def test_new_relation_no_name(self):
        url = reverse('concept_changes', kwargs=self.request_kwargs)
        response = self.app.get(url, user=self.user)
        self.assertEqual('Name not available in the current language',
                         response.pyquery('.status-0')[1].text)

    def test_new_relation_name_available(self):
        group_name = factories.PropertyFactory(status=PENDING,
                                               concept=self.group,
                                               value='Group name')
        url = reverse('concept_changes', kwargs=self.request_kwargs)
        response = self.app.get(url, user=self.user)
        self.assertEqual(group_name.value,
                         response.pyquery('.status-0')[1].text)

    def test_group_changes(self):
        self.request_kwargs['id'] = self.group.id
        url = reverse('concept_changes', kwargs=self.request_kwargs)
        response = self.app.get(url, user=self.user)
        self.assertEqual(self.group_definition.value,
                         response.pyquery('.definition.status-0').html())
