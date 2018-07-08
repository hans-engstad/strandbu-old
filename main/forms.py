from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
import datetime
from . import models

class CabinSearch(forms.Form):
	from_date = forms.CharField()
	to_date = forms.CharField()
	persons = forms.IntegerField();


#Form used when creating tentative booking
class TentativeBookingForm(forms.Form):

	# cabin_number = forms.IntegerField(widget=forms.HiddenInput())
	t_booking_id = forms.IntegerField(widget=forms.HiddenInput(), initial=-1, required=False)

	from_date = forms.DateField(widget=forms.HiddenInput())
	to_date = forms.DateField(widget=forms.HiddenInput())
    

class CabinChoose(forms.Form):
	from_date = forms.CharField(widget=forms.HiddenInput())
	to_date = forms.CharField(widget=forms.HiddenInput())
	cabin_number = forms.CharField(widget=forms.HiddenInput())

	t_booking_id = forms.IntegerField(
		widget=forms.HiddenInput(),
		required=False,
		initial=-1,
	)


class ContactForm(forms.ModelForm):

	late_arrival = forms.BooleanField(widget=forms.HiddenInput(), required=False)

	class Meta:
		model = models.Contact
		fields = ('name', 'email', 'phone', 'country', 'late_arrival')

class PreChargeInfoForm(forms.Form):
	phone = forms.IntegerField()
	late_arrival = forms.BooleanField(required=False)
	accept_conditions = forms.BooleanField(required=True)

class ChargeForm(forms.Form):
	token = forms.CharField()
	t_booking_id = forms.CharField()

	total_price = forms.IntegerField()
	phone = forms.IntegerField()
	late_arrival = forms.BooleanField(required=False)



