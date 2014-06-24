from django import forms

from gemet.thesaurus.models import Language


class SearchForm(forms.Form):
    query = forms.CharField(max_length=255, required=False)


class ExportForm(forms.Form):
    language_names = forms.ModelChoiceField(
        queryset=Language.objects.order_by(
            'name'
        ),
        empty_label=None,
        label="Choose the language",
    )
