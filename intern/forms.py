from django import forms
from . import models
from main import models as main_models
from django.contrib.admin.widgets import AdminDateWidget

class LoginForm(forms.Form):
	username = forms.CharField(max_length=100)
	password = forms.CharField(widget=forms.PasswordInput(render_value=False), max_length=100)

class EditBookingForm(forms.ModelForm):

	class Meta:
		model = main_models.FinalBooking
		fields = ('from_date', 'to_date', 'contact', 'payed', 'cabins', 'late_arrival', 'active', 'id')