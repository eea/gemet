from django import forms
from django.forms import ModelForm
from gemet.thesaurus.models import Language, Property


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
        fields = ('concept', 'language', 'name', 'value', 'is_resource')
