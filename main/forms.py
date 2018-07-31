from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
import datetime
from . import models
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class CabinSearch(forms.Form):
	from_date = forms.CharField()
	to_date = forms.CharField()
	# persons = forms.IntegerField();


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

	action = forms.CharField(widget=forms.HiddenInput())

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
	t_booking_JSON = forms.CharField()


class BookingAdminForm(forms.ModelForm):
	time_widget = forms.widgets.TimeInput()
	valid_time_formats = ['%H:%M:%S']

	booking_close_time = forms.TimeField(widget=time_widget, input_formats=valid_time_formats)


	class Meta:
		model = models.AdminSettings
		exclude = ('',)



