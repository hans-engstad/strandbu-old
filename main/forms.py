from django import forms
import datetime

class CabinSearch(forms.Form):
	from_date = forms.DateField()
	to_date = forms.DateField()
	persons = forms.IntegerField();
