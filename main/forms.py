from django import forms
import datetime

class CabinSearch(forms.Form):
	from_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'search-cabin-input', 'id': 'from-date-field'}))
	to_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'search-cabin-input', 'id': 'to-date-field'}))
	guest_amount = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'search-cabin-input'}));
