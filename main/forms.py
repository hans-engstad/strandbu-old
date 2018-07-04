from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
import datetime
from . import models

class CabinSearch(forms.Form):
	from_date = forms.DateField()
	to_date = forms.DateField()
	persons = forms.IntegerField();


#Form used when creating tentative booking
class TentativeBookingForm(forms.Form):

	# cabin_number = forms.IntegerField(widget=forms.HiddenInput())
	t_booking_id = forms.IntegerField(widget=forms.HiddenInput(), initial=-1, required=False)

	from_date = forms.DateField(widget=forms.HiddenInput())
	to_date = forms.DateField(widget=forms.HiddenInput())
    

class CabinChoose(forms.Form):
	from_date = forms.DateField(widget=forms.HiddenInput())
	to_date = forms.DateField(widget=forms.HiddenInput())
	cabin_numbers = forms.CharField(widget=forms.HiddenInput())

	t_booking_id = forms.IntegerField(
		widget=forms.HiddenInput(),
		required=False,
		initial=-1,
	)


class Contact(forms.ModelForm):

	email = forms.CharField(required=False)
	late_arrival = forms.BooleanField(required=False)
	accept_conditions = forms.BooleanField(required=True)

	class Meta:
		model = models.ContactInfo
		fields = ('name', 'email', 'phone', 'country', 'late_arrival', 'accept_conditions')
		widgets = {'country': CountrySelectWidget(
			#layout='{widget}<div class="col"><img class="country-select-flag" id="{flag_id}" style="display: inline; margin: 6px 4px 0" src="{country.flag}"></div>'
			layout='{widget}'
		)}
		labels = {
			'name': 'Fullt navn',
		}

class PreChargeInfoForm(forms.Form):
	phone = forms.IntegerField()
	late_arrival = forms.BooleanField(required=False)
	accept_conditions = forms.BooleanField(required=True)

class ChargeForm(forms.Form):
	token = forms.CharField()
	t_booking_id = forms.CharField()
