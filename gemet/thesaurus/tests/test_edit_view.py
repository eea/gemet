import json

from django.core.urlresolvers import reverse

from .factories import ForeignRelationFactory, RelationFactory, LanguageFactory
from .factories import PropertyTypeFactory, PropertyFactory, ConceptFactory
from .factories import ThemeFactory, UserFactory, NamespaceFactory, TermFactory
from gemet.thesaurus import PENDING, PUBLISHED, DELETED_PENDING
from gemet.thesaurus import forms
from gemet.thesaurus import models
from . import GemetTest


class TestEditPropertyView(GemetTest):

    csrf_checks = False

    def setUp(self):
        self.language = LanguageFactory()
        self.concept = TermFactory()
        self.request_kwargs = {'langcode': self.language.code,
                               'id': self.concept.id,
                               'name': 'prefLabel'}
        user = UserFactory()
        self.user = user.username

    def test_edit_property_bad_concept(self):
        self.request_kwargs['id'] = 99
        url = reverse('edit_property', kwargs=self.request_kwargs)
        response = self.app.post(url, user=self.user, params={'value': 'name1'},
                                 expect_errors=True)
        self.assertEqual(400, response.status_code)

    def test_edit_property_bad_language(self):
        self.request_kwargs['langcode'] = 'abc'
        url = reverse('edit_property', kwargs=self.request_kwargs)
        response = self.app.post(url, user=self.user, params={'value': 'name1'},
                                 expect_errors=True)
        self.assertEqual(400, response.status_code)

    def test_edit_property_request_no_value(self):
        url = reverse('edit_property', kwargs=self.request_kwargs)
        response = self.app.post(url, user=self.user, expect_errors=True)
        self.assertEqual(400, response.status_code)

    def test_edit_property_correct_request_no_property(self):
        url = reverse('edit_property', kwargs=self.request_kwargs)
        response = self.app.post(url, user=self.user, params={'value': 'name1'})
        self.assertEqual(200, response.status_code)
        self.assertEqual(json.loads(response.body)['value'], 'name1')
        new_property = self.concept.properties.first()
        self.assertIsNotNone(new_property)
        self.assertEquals(new_property.name, 'prefLabel')
        self.assertEquals(new_property.value, 'name1')
        self.assertEquals(new_property.status, PENDING)

    def test_edit_property_correct_request_published_property(self):
        property = PropertyFactory(concept=self.concept, language=self.language,
                                   name='prefLabel', value='test',
                                   status=PUBLISHED)
        url = reverse('edit_property', kwargs=self.request_kwargs)
        response = self.app.post(url, user=self.user, params={'value': 'name1'})
        self.assertEqual(200, response.status_code)
        self.assertEqual(json.loads(response.body)['value'], 'name1')
        property.refresh_from_db()
        self.assertEquals(property.status, DELETED_PENDING)
        self.assertEquals(property.value, 'test')
        new_property = models.Property.objects.filter(status=PENDING).first()
        self.assertIsNotNone(new_property)
        self.assertEquals(new_property.name, 'prefLabel')
        self.assertEquals(new_property.value, 'name1')

    def test_edit_property_correct_request_pending_property(self):
        property = PropertyFactory(concept=self.concept, language=self.language,
                                   name='prefLabel', value='test',
                                   status=PENDING)
        url = reverse('edit_property', kwargs=self.request_kwargs)
        response = self.app.post(url, user=self.user, params={'value': 'name1'})
        self.assertEqual(200, response.status_code)
        self.assertEqual(json.loads(response.body)['value'], 'name1')
        property.refresh_from_db()
        self.assertEquals(property.name, 'prefLabel')
        self.assertEquals(property.value, 'name1')
        self.assertEquals(property.status, PENDING)


class TestAddPropertyView(GemetTest):
    csrf_checks = False

    def setUp(self):
        self.language = LanguageFactory()
        self.concept = TermFactory()
        self.request_kwargs = {'langcode': self.language.code,
                               'id': self.concept.id,
                               'name': 'prefLabel'}
        user = UserFactory()
        self.user = user.username

    def test_add_property_bad_concept(self):
        self.request_kwargs['id'] = 99
        url = reverse('add_property', kwargs=self.request_kwargs)
        response = self.app.post(url, user=self.user, params={'value': 'name1'},
                                 expect_errors=True)
        self.assertEqual(400, response.status_code)

    def test_add_property_bad_language(self):
        self.request_kwargs['langcode'] = 'abc'
        url = reverse('add_property', kwargs=self.request_kwargs)
        response = self.app.post(url, user=self.user, params={'value': 'name1'},
                                 expect_errors=True)
        self.assertEqual(400, response.status_code)

    def test_add_property_request_no_value(self):
        url = reverse('add_property', kwargs=self.request_kwargs)
        response = self.app.post(url, user=self.user, expect_errors=True)
        self.assertEqual(400, response.status_code)

    def test_add_property_correct_request(self):
        url = reverse('add_property', kwargs=self.request_kwargs)
        response = self.app.post(url, user=self.user, params={'value': 'name1'})
        self.assertEqual(200, response.status_code)
        self.assertEqual(json.loads(response.body)['value'], 'name1')
        new_property = self.concept.properties.first()
        self.assertIsNotNone(new_property)
        self.assertEquals(new_property.name, 'prefLabel')
        self.assertEquals(new_property.value, 'name1')
        self.assertEquals(new_property.status, PENDING)


class TestDeleteRelationView(GemetTest):
    csrf_checks = False

    def setUp(self):
        self.relation = RelationFactory(status=DELETED_PENDING)
        PropertyTypeFactory(label='Theme', name='theme')
        self.relation.create_reverse()
        self.request_kwargs = {
            'source_id': self.relation.source.id,
            'target_id': self.relation.target.id,
            'relation_type': self.relation.property_type.name,
        }
        user = UserFactory()
        self.user = user.username

    def test_delete_relation_bad_concept(self):
        self.request_kwargs['source_id'] = 99
        url = reverse('delete_relation', kwargs=self.request_kwargs)
        response = self.app.post(url, user=self.user, expect_errors=True)
        self.assertEqual(400, response.status_code)

    def test_delete_relation_bad_parent(self):
        self.request_kwargs['target_id'] = 99
        url = reverse('delete_relation', kwargs=self.request_kwargs)
        response = self.app.post(url, user=self.user, expect_errors=True)
        self.assertEqual(400, response.status_code)

    def test_delete_relation_no_relation(self):
        self.request_kwargs['relation_type'] = 'test'
        url = reverse('delete_relation', kwargs=self.request_kwargs)
        response = self.app.post(url, user=self.user, expect_errors=True)
        self.assertEqual(400, response.status_code)

    def test_delete_relation_correct_request_published_relation(self):
        self.relation.status = PUBLISHED
        self.relation.save()
        url = reverse('delete_relation', kwargs=self.request_kwargs)
        response = self.app.post(url, user=self.user)
        self.assertEqual(200, response.status_code)
        self.relation.refresh_from_db()
        self.assertEqual(self.relation.status, DELETED_PENDING)
        self.assertEqual(self.relation.reverse.status, DELETED_PENDING)

    def test_delete_relation_correct_request_pending_relation(self):
        self.relation.status = PENDING
        self.relation.save()
        reverse_relation_id = self.relation.reverse.id
        url = reverse('delete_relation', kwargs=self.request_kwargs)
        response = self.app.post(url, user=self.user)
        self.assertEqual(200, response.status_code)
        self.assertFalse(models.Relation.objects.filter(
            id=self.relation.id).exists())
        self.assertFalse(models.Relation.objects.filter(
            id=reverse_relation_id).exists())


class TestRestoreRelationView(GemetTest):
    csrf_checks = False

    def setUp(self):
        self.relation = RelationFactory(status=DELETED_PENDING)
        PropertyTypeFactory(label='Theme', name='theme')
        self.relation.create_reverse()
        self.request_kwargs = {
            'source_id': self.relation.source.id,
            'target_id': self.relation.target.id,
            'relation_type': self.relation.property_type.name,
        }
        user = UserFactory()
        self.user = user.username

    def test_restore_relation_bad_source(self):
        self.request_kwargs['source_id'] = 99
        url = reverse('restore_relation', kwargs=self.request_kwargs)
        response = self.app.post(url, user=self.user, expect_errors=True)
        self.assertEqual(400, response.status_code)

    def test_restore_relation_bad_target(self):
        self.request_kwargs['target_id'] = 99
        url = reverse('restore_relation', kwargs=self.request_kwargs)
        response = self.app.post(url, user=self.user, expect_errors=True)
        self.assertEqual(400, response.status_code)

    def test_restore_relation_no_relation(self):
        self.request_kwargs['relation_type'] = 'test'
        url = reverse('restore_relation', kwargs=self.request_kwargs)
        response = self.app.post(url, user=self.user, expect_errors=True)
        self.assertEqual(400, response.status_code)

    def test_restore_relation_bad_status(self):
        self.relation.status = PENDING
        self.relation.save()
        url = reverse('restore_relation', kwargs=self.request_kwargs)
        response = self.app.post(url, user=self.user, expect_errors=True)
        self.assertEqual(400, response.status_code)
        self.relation.refresh_from_db()
        self.assertEqual(self.relation.status, PENDING)

    def test_restore_relation_correct_request(self):
        url = reverse('restore_relation', kwargs=self.request_kwargs)
        response = self.app.post(url, user=self.user)
        self.assertEqual(200, response.status_code)
        self.relation.refresh_from_db()
        self.assertEqual(self.relation.status, PUBLISHED)
        self.assertEqual(self.relation.reverse.status, PUBLISHED)


class TestAddRelationView(GemetTest):
    csrf_checks = False

    def setUp(self):
        self.language = LanguageFactory()
        self.term = TermFactory()
        self.theme = ThemeFactory()
        self.property = PropertyFactory(language=self.language,
                                        concept=self.theme,
                                        name='prefLabel',
                                        value='Theme 1',
                                        status=PUBLISHED)
        PropertyTypeFactory(label='Theme', name='theme')
        PropertyTypeFactory(label='Theme member', name='themeMember')
        user = UserFactory()
        self.user = user.username

    def test_post_no_concept_no_parent_object(self):
        url = reverse('add_relation', kwargs={'source_id': 33,
                                              'target_id': 45,
                                              'relation_type': 'theme'})

        response = self.app.post(url, user=self.user, expect_errors=True)
        self.assertEqual(400, response.status_code)

    def test_post_correct_request(self):
        url = reverse('add_relation', kwargs={'source_id': self.term.id,
                                              'target_id': self.theme.id,
                                              'relation_type': 'theme'})

        response = self.app.post(url, user=self.user)
        self.assertEqual(200, response.status_code)
        self.assertEqual(models.Relation.objects.count(), 2)


class TestDeletePropertyView(GemetTest):
    csrf_checks = False

    def setUp(self):
        self.property = PropertyFactory(value='new property', status=PUBLISHED)
        user = UserFactory()
        self.user = user.username

    def test_delete_property_bad_concept(self):
        url = reverse('delete_property', kwargs={'pk': 43})
        response = self.app.post(url, user=self.user, expect_errors=True)
        self.assertEqual(400, response.status_code)

    def test_delete_property_correct_request(self):
        url = reverse('delete_property', kwargs={'pk': self.property.pk})
        response = self.app.post(url, user=self.user,
                                 params={'value': 'new property'})
        self.assertEqual(200, response.status_code)
        self.property.refresh_from_db()
        self.assertEqual(self.property.status, DELETED_PENDING)


class TestAddForeignRelationView(GemetTest):
    csrf_checks = False

    def setUp(self):
        self.property_type = PropertyTypeFactory(label='has exact Match',
                                                 name='exactMatch')
        self.concept = TermFactory()
        self.params = {
            'uri': 'http://some.bogus.url',
            'rel_type': self.property_type.id,
            'label': 'Test label',
        }
        user = UserFactory()
        self.user = user.username

    def test_post_bad_concept_id(self):
        url = reverse('add_other', kwargs={'id': 999})
        response = self.app.post(url, user=self.user, params=self.params,
                                 expect_errors=True)
        self.assertEqual(400, response.status_code)

    def test_post_bad_relation_type(self):
        url = reverse('add_other', kwargs={'id': self.concept.id})
        self.params['rel_type'] = 99
        response = self.app.post(url, user=self.user, params=self.params,
                                 expect_errors=True)
        self.assertEqual(400, response.status_code)

    def test_post_correct_request(self):
        url = reverse('add_other', kwargs={'id': self.concept.id})
        response = self.app.post(url, user=self.user, params=self.params)
        self.assertEqual(200, response.status_code)
        foreign_relation = models.ForeignRelation.objects.get(
            concept=self.concept, property_type=self.property_type)
        self.assertIsNotNone(foreign_relation)
        data = json.loads(response.body)
        self.assertEqual(foreign_relation.id, data['id'])


class TestDeleteForeignRelationView(GemetTest):
    csrf_checks = False

    def setUp(self):
        self.foreign_relation = ForeignRelationFactory()
        user = UserFactory()
        self.user = user.username

    def test_delete_foreign_relation_no_relation(self):
        url = reverse('delete_other', kwargs={'pk': 99})
        response = self.app.post(url, user=self.user, expect_errors=True)
        self.assertEqual(400, response.status_code)

    def test_delete_foreign_relation_correct_request(self):
        url = reverse('delete_other', kwargs={'pk': self.foreign_relation.pk})
        response = self.app.post(url, user=self.user)
        self.foreign_relation.refresh_from_db()
        self.assertEqual(200, response.status_code)
        self.assertEqual(self.foreign_relation.status, DELETED_PENDING)


class TestRestoreForeignRelationView(GemetTest):
    csrf_checks = False

    def setUp(self):
        user = UserFactory()
        self.user = user.username

    def test_restore_foreign_relation_no_relation(self):
        url = reverse('restore_other', kwargs={'pk': 99})
        response = self.app.post(url, user=self.user, expect_errors=True)
        self.assertEqual(400, response.status_code)

    def test_restore_foreign_relation_not_deleted(self):
        foreign_relation = ForeignRelationFactory(status=PENDING)
        url = reverse('restore_other', kwargs={'pk': foreign_relation.pk})
        response = self.app.post(url, user=self.user, expect_errors=True)
        self.assertEqual(400, response.status_code)
        foreign_relation.refresh_from_db()
        self.assertEqual(foreign_relation.status, PENDING)

    def test_restore_foreign_relation_correct_request(self):
        foreign_relation = ForeignRelationFactory(status=DELETED_PENDING)
        url = reverse('restore_other', kwargs={'pk': foreign_relation.pk})
        response = self.app.post(url, user=self.user)
        self.assertEqual(200, response.status_code)
        foreign_relation.refresh_from_db()
        self.assertEqual(foreign_relation.status, PUBLISHED)


class TestAddNewConcept(GemetTest):
    csrf_checks = False

    def setUp(self):
        self.language = LanguageFactory()
        self.namespace = NamespaceFactory()
        self.concept = ConceptFactory(namespace=self.namespace, code='200')
        user = UserFactory()
        self.user = user.username

    def test_get_sets_form(self):
        url = reverse('concept_add', kwargs={'langcode': self.language.code})
        response = self.app.get(url, user=self.user)
        self.assertEqual(200, response.status_code)
        self.assertEqual(forms.ConceptForm, type(response.context['form']))

    def test_post_correct_form(self):
        url = reverse('concept_add', kwargs={'langcode': self.language.code})
        response = self.app.post(url, user=self.user,
                                 params={'name': 'test',
                                         'namespace': self.namespace.id})

        self.assertEqual(302, response.status_code)
        self.assertEqual(2, len(models.Concept.objects.all()))
        self.assertEqual('201', models.Concept.objects.last().code)
        self.assertEqual('test',
                         models.Property.objects.get(name='prefLabel',
                                                     concept__code='201').value)


class TestDeleteNewConcept(GemetTest):
    def setUp(self):
        self.language = LanguageFactory()
        self.namespace = NamespaceFactory()
        self.concept = ConceptFactory(namespace=self.namespace, code='200',
                                      status=PENDING)
        self.property = PropertyFactory(concept=self.concept)
        self.relation = RelationFactory(source=self.concept)
        self.relation = RelationFactory(target=self.concept)
        self.foreignrelation = ForeignRelationFactory(concept=self.concept)
        user = UserFactory()
        self.user = user.username

    def test_objects_are_deleted(self):
        url = reverse('concept_delete', kwargs={'langcode': self.language.code,
                                                'pk': self.concept.id})
        self.app.get(url, user=self.user)
        self.assertEqual(0,
                         len(models.Concept.objects.filter(id=self.concept.id)))
        self.assertEqual(0,
                         len(models.Property.objects.filter(
                             concept=self.concept
                         )))
        self.assertEqual(0,
                         len(models.Relation.objects.filter(
                             source=self.concept
                         )))
        self.assertEqual(0,
                         len(models.ForeignRelation.objects.filter(
                             concept=self.concept
                         )))
