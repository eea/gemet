from django import forms
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm

from gemet.thesaurus.models import ForeignRelation, Language, Namespace
from gemet.thesaurus.models import Property, Version


class SearchForm(forms.Form):
    query = forms.CharField(max_length=255, required=False)

    def clean_query(self):
        data = self.cleaned_data['query']
        if len(data) < 2:
            raise forms.ValidationError(
                "The search text must be at least two characters long."
            )
        return data


class ExportForm(forms.Form):
    language_names = forms.ModelChoiceField(
        queryset=Language.objects.order_by(
            'name'
        ),
        empty_label=None,
        label="Choose the language",
    )


class PropertyForm(forms.ModelForm):

    class Meta:
        model = Property
        fields = ('value', )


class ForeignRelationForm(forms.ModelForm):

    class Meta:
        model = ForeignRelation
        fields = ('label', 'uri')


class ConceptForm(forms.Form):

    name = forms.CharField(max_length=16000)
    namespace = forms.ModelChoiceField(queryset=Namespace.objects.all(),
                                       empty_label=None)


class LDAPAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if user.username not in settings.AUTHORIZED_USERS:
            raise forms.ValidationError(
                'Your account is not authorized to login to GEMET')


def my_choices():
    current_identifier = Version.objects.get(is_current=True).identifier
    version_numbers = map(int, current_identifier.split("."))
    choices = []
    version_numbers[2] += 1
    identifier = ".".join(map(str, version_numbers))
    choices.append((identifier, identifier))
    version_numbers[2] = 0
    version_numbers[1] += 1
    identifier = ".".join(map(str, version_numbers))
    choices.append((identifier, identifier))
    version_numbers[1] = 0
    version_numbers[0] += 1
    identifier = ".".join(map(str, version_numbers))
    choices.append((identifier, identifier))
    return choices


class VersionForm(forms.Form):

    version = forms.ChoiceField(choices=my_choices)
