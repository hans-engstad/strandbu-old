from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
import datetime

class CabinSearch(forms.Form):
	from_date = forms.DateField()
	to_date = forms.DateField()
	persons = forms.IntegerField();


class CabinChoose(forms.Form):
	from_date = forms.DateField(
		widget=forms.HiddenInput()
	)
	to_date = forms.DateField(
		widget=forms.HiddenInput()
	)
	number = forms.IntegerField(
		widget=forms.HiddenInput()
	)

class Contact(forms.Form):
	full_name = forms.CharField()
	email = forms.CharField(required=False)
	country = CountryField().formfield(
		widget=CountrySelectWidget()
	)
	phone = forms.CharField()
