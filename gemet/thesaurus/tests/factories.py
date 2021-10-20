import factory
from django.contrib.auth.models import User

from gemet.thesaurus import PUBLISHED
from gemet.thesaurus.models import (
    Concept,
    DefinitionSource,
    ForeignRelation,
    Group,
    InspireTheme,
    Language,
    Namespace,
    Property,
    PropertyType,
    Relation,
    SuperGroup,
    Term,
    Theme,
    Version,
)


class VersionFactory(factory.django.DjangoModelFactory):
    identifier = "1.0.0"
    is_current = True

    class Meta:
        model = Version
        django_get_or_create = ("identifier",)


class LanguageFactory(factory.django.DjangoModelFactory):
    code = "en"
    name = "English"
    charset = "utf8_general_ci"

    class Meta:
        model = Language
        django_get_or_create = ("code",)


class ConceptFactory(factory.django.DjangoModelFactory):
    version_added = factory.SubFactory(VersionFactory)
    status = PUBLISHED

    class Meta:
        model = Concept


class NamespaceFactory(factory.django.DjangoModelFactory):
    heading = "Concepts"

    class Meta:
        model = Namespace


class TermFactory(factory.django.DjangoModelFactory):
    code = "1"
    version_added = factory.SubFactory(VersionFactory)
    status = PUBLISHED

    class Meta:
        model = Term


class GroupFactory(factory.django.DjangoModelFactory):
    code = "2"
    version_added = factory.SubFactory(VersionFactory)
    status = PUBLISHED

    class Meta:
        model = Group


class SuperGroupFactory(factory.django.DjangoModelFactory):
    code = "3"
    version_added = factory.SubFactory(VersionFactory)
    status = PUBLISHED

    class Meta:
        model = SuperGroup


class ThemeFactory(factory.django.DjangoModelFactory):
    code = "4"
    version_added = factory.SubFactory(VersionFactory)
    status = PUBLISHED

    class Meta:
        model = Theme


class PropertyFactory(factory.django.DjangoModelFactory):
    concept = factory.SubFactory(TermFactory)
    language = factory.SubFactory(LanguageFactory)
    version_added = factory.SubFactory(VersionFactory)
    name = "prefLabel"
    value = "administration"
    status = PUBLISHED

    class Meta:
        model = Property


class PropertyTypeFactory(factory.django.DjangoModelFactory):
    name = "themeMember"
    label = "Theme member"

    class Meta:
        model = PropertyType


class RelationFactory(factory.django.DjangoModelFactory):
    property_type = factory.SubFactory(PropertyTypeFactory)
    source = factory.SubFactory(TermFactory)
    target = factory.SubFactory(ThemeFactory)
    version_added = factory.SubFactory(VersionFactory)
    status = PUBLISHED

    class Meta:
        model = Relation


class ForeignRelationFactory(factory.django.DjangoModelFactory):
    property_type = factory.SubFactory(PropertyTypeFactory)
    concept = factory.SubFactory(TermFactory)
    version_added = factory.SubFactory(VersionFactory)
    status = PUBLISHED

    class Meta:
        model = ForeignRelation


class DataSourceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DefinitionSource


class InspireThemeFactory(factory.django.DjangoModelFactory):
    code = "ad"
    version_added = factory.SubFactory(VersionFactory)
    status = PUBLISHED

    class Meta:
        model = InspireTheme


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: "john%03d" % n)
    password = "123456"

    class Meta:
        model = User
        django_get_or_create = ("username",)
