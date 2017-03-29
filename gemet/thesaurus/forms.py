from django import forms
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm

from gemet.thesaurus.models import ForeignRelation, InspireTheme, Language
from gemet.thesaurus.models import Namespace, Property
from gemet.thesaurus.utils import get_version_choices


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
    label_error_messages = {
        'required': 'Label is required.'
    }
    uri_error_messages = {
        'required': 'Label is required.'
    }
    uri = forms.CharField(max_length=512, error_messages=uri_error_messages)
    label = forms.CharField(max_length=100, error_messages=label_error_messages)

    class Meta:
        model = ForeignRelation
        fields = ('label', 'uri')


class ConceptForm(forms.Form):

    name = forms.CharField(max_length=16000)
    namespace = forms.ModelChoiceField(
        queryset=Namespace.objects.exclude(heading=InspireTheme.NAMESPACE),
        empty_label=None)


class LDAPAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if user.username not in settings.AUTHORIZED_USERS:
            raise forms.ValidationError(
                'Your account is not authorized to login to GEMET')


class VersionForm(forms.Form):

    version = forms.ChoiceField(choices=get_version_choices)
