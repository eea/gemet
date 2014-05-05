from django import forms


class SearchForm(forms.Form):
    query = forms.CharField(max_length=255)
    langcode = forms.CharField(max_length=10, widget=forms.HiddenInput())
