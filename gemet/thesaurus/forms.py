from django import forms
from django.forms import ModelForm

from gemet.thesaurus.models import ForeignRelation, Language, Namespace
from gemet.thesaurus.models import Property


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


class PropertyForm(ModelForm):

    class Meta:
        model = Property
        fields = ('value', )


class ForeignRelationForm(ModelForm):

    class Meta:
        model = ForeignRelation
        fields = ('label', 'uri')


class ConceptForm(forms.Form):

    name = forms.CharField(max_length=16000)
    namespace = forms.ModelChoiceField(queryset=Namespace.objects.all(),
                                       empty_label=None)
