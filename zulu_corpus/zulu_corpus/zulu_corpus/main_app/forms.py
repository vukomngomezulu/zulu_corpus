from django import forms

class SearchForm(forms.Form):
    q = forms.CharField(
        label='Search',
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter isiZulu word...',
            'class': 'search-input'
        })
    )