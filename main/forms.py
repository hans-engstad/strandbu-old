from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
import datetime
from . import models

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
	t_booking_id = forms.IntegerField(
		widget=forms.HiddenInput(),
		required=False
	)

class Contact(forms.ModelForm):

	email = forms.CharField(required=False)
	late_arrival = forms.BooleanField(required=False)
	accept_conditions = forms.BooleanField(required=True)

	class Meta:
		model = models.ContactInfo
		fields = ('name', 'email', 'phone', 'country', 'late_arrival', 'accept_conditions')
		widgets = {'country': CountrySelectWidget()}

class Payment(forms.Form):
	card_number = forms.CharField()
	cvc = forms.CharField()
	expire_date = forms.CharField()