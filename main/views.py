from django.shortcuts import render
from django.shortcuts import render, HttpResponse, redirect
from main import forms
import datetime
from main.models import Booking, Cabin, TentativeBooking, Contact, AdminSettings
from django.contrib.staticfiles.templatetags.staticfiles import static
from strandbu.settings import dev as settings
from django_countries import countries
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.views.decorators.cache import never_cache
import os
import json
import stripe
from . import serializers
from rest_framework.renderers import JSONRenderer
from django.utils.six import BytesIO
from rest_framework.parsers import JSONParser
import ast



# Create your views here.
def Home(request):
	
	args = {
		'cabin_search_form': forms.CabinSearch(),
		'min_from_date' : AdminSettings.objects.first().min_from_date,
	}

	args = add_alerts_from_session(request, args)



	return render(request, 'main/home.html', args)


def BookingView(request):

	args = {
		'cabin_search_form': forms.CabinSearch(),
		'min_from_date' : AdminSettings.objects.first().min_from_date,
	}

	args = add_alerts_from_session(request, args)

	return render(request, 'main/booking.html', args)


def ShowCabins(request):

	#Retrieve cabin search form
	cabin_search_form = forms.CabinSearch(request.POST)
	if 'cabin_search_form_data' in request.session and not cabin_search_form.is_valid():
		cabin_search_form = forms.CabinSearch(request.session['cabin_search_form_data'])

	#Check that search form is valid
	if not cabin_search_form.is_valid():
		request.session = add_alert(request, 'Ugyldig søk. Vennligst prøv igjen', type='warning')
		return redirect('booking')

	args = {
		'cabin_search_form_data': cabin_search_form.cleaned_data,
		'min_from_date' : AdminSettings.objects.first().min_from_date,
	}

	#Retrieve booking action
	action = 'show'
	if 'action' in request.POST:
		action = request.POST['action']

	
	#Defualt value is to not add cabin (used for displaying template correct)
	args['action'] = action



	#Show correct view
	if action == 'show':
		return ShowCabins_show(request, args)
	elif action == 'add_cabin':
		return ShowCabins_add_cabin(request, args)
	else:
		#Not valid action
		print("Warning: \"" + action + "\" is not a recognized action. ")
		return ShowCabins_show(request, args)

	
	
		
# @never_cache
def BookingOverview(request):
	
	#Define Cabin Search Form. Used when redirecting
	cabin_search_form = forms.CabinSearch(request.POST)
	if 'cabin_search_form_data' in request.session and not cabin_search_form.is_valid():
		cabin_search_form = forms.CabinSearch(request.session['cabin_search_form_data'])

	if not cabin_search_form.is_valid():
		#Unable to retrieve search form. Redirect to booking page
		request.session = add_alert(request, 'Klarer ikke vise oversikt. Vennligst prøv igjen.', type='danger')
		return redirect('booking')

	#add search form to session, used when redirecting to show cabins
	request.session['cabin_search_form_data'] = cabin_search_form.cleaned_data

	#Declare arguments
	args = {
		'min_from_date' : AdminSettings.objects.first().min_from_date,
		'choose_form': 	forms.CabinChoose(request.POST),
		'cabin_search_form': cabin_search_form,
	}


	action = 'show'
	if 'action' in request.POST:
		action = request.POST['action']

	if action == 'show':
		return BookingOverview_show(request, args)
	elif action == 'add_cabin':
		return BookingOverview_add_cabin(request, args)
	elif action == 'remove_cabin':
		return BookingOverview_remove_cabin(request, args)
	else:
		#Not valid action
		print("Warning: \"" + action + "\" is not a recognized action. ")
		return BookingOverview_show(request, args)


def ChargeBooking(request):

	#Define Cabin Search Form. Used when redirecting
	cabin_search_form = forms.CabinSearch(request.POST)
	if 'cabin_search_form_data' in request.session and not cabin_search_form.is_valid():
		cabin_search_form = forms.CabinSearch(request.session['cabin_search_form_data'])

	#Check if cabin_search_form is valid
	if not cabin_search_form.is_valid():
		request.session = add_alert(request, 'En feil har oppstått. Betalingen er ikke gjennomført. Vennligst prøv igjen.', type='danger', starter='OBS!')
		return redirect('booking')

	#Update cabin_search_form_data session
	request.session['cabin_search_form_data'] = cabin_search_form.cleaned_data

	#Check that request method is POST
	if not request.method == 'POST':
		request.session = add_alert(request, 'En feil har oppstått. Betalingen er ikke gjennomført. Vennligst prøv igjen.', type='danger', starter='OBS!')
		return redirect('show_cabins')

	#Retrieve charge form
	charge_form = forms.ChargeForm(request.POST)
	if not charge_form.is_valid():
		request.session = add_alert(request, 'Klarer ikke fullføre betaling. Vennligst prøv igjen.', type='danger', starter='OBS!')
		return redirect('booking_overview')

	#Retrieve charge data from charge form
	charge_data = charge_form.cleaned_data

	price = charge_data['total_price']
	phone = charge_data['phone']
	t_booking_id = charge_data['t_booking_id']

	#Find t_booking
	t_booking = TentativeBooking.objects.filter(id=t_booking_id).first()	#TODO: We might not find this booking!
	
	if t_booking == None:
		request.session = add_alert(request, "Klarer ikke finne bestilling. Betaling ikke fullført. Vennligst prøv igjen.", type='danger', starter='OBS!')
		return redirect('show_cabins')

	if not t_booking.is_active():
		#Try to re activate t_booking and redirect to booking overview
		t_booking_id = t_booking.create_active_copy()
		if t_booking_id == False:
			#Redirect with alert (Booking no longer valid)
			request.session = add_alert(request, "Sesjon ikke oppdatert. Betaling ikke fullført. Vennligst prøv igjen.", type='danger', starter='OBS!')
			return redirect('show_cabins')

		t_booking = TentativeBooking.objects.filter(id=t_booking_id).first()

	if not t_booking.is_valid():
		request.session = add_alert(request, "Bestilling ikke lengre gyldig. Betaling ikke fullført. Vennligst prøv igjen.", type='danger', starter='OBS!')
		return redirect('show_cabins')

	#Update session variable
	request.session['t_booking_id'] = t_booking_id

	#Serialized booking from charge_form field
	charge_t_booking_serialized = ast.literal_eval(charge_data['t_booking_JSON'])
	
	#Serialized booking from db
	t_booking_serialized = serializers.TentativeBookingSerializer(t_booking).data

	#Check that t_booking matches charge-t_booking
	if not charge_t_booking_serialized == t_booking_serialized:
		#Fields do not match, redirect to booking overview with updated booking
		request.session = add_alert(request, "Sesjon ikke oppdatert. Betaling ikke fullført. Vennligst prøv igjen.", type='danger', starter='OBS!')
		return redirect('booking_overview')

	#Check that booking dates are valid
	if not t_booking.dates_are_valid():
		request.session = add_alert(request, "Bestilling ikke lengre gyldig. Betaling ikke fullført. Vennligst prøv igjen.", type='danger', starter='OBS!')
		return redirect('booking')

	#Check that price displayed matches t_booking price
	if not charge_data['total_price'] == t_booking.get_price():
		request.session = add_alert(request, "Pris stemmer ikke med sesjon. Betaling ikke fullført. Vennligst prøv igjen.", type='danger', starter='OBS!')
		return redirect('booking_overview')

	#Load token data
	token = charge_data['token']
	token_data = json.loads(token)

	#Retrieve contact data
	contact_data = {
		'name': token_data['card']['name'],
		'email': token_data['email'],
		'phone': phone,
		'country': token_data['card']['address_country'],
		'late_arrival': charge_data['late_arrival']
	}

	#Declare contact data 
	contact_form = forms.ContactForm(contact_data)

	#Check that contact data is valid
	if not contact_form.is_valid():
		request.session = add_alert(request, "Kontaktinformasjon ugyldig. Betaling ikke fullført. Vennligst prøv igjen.", type='danger', starter='OBS!')
		return redirect('booking_overview')

	#Create contact object
	contact = Contact.objects.create(
		name=contact_form.cleaned_data['name'],
		email=contact_form.cleaned_data['email'],
		phone=contact_form.cleaned_data['phone'],
		country=contact_form.cleaned_data['country'],
	)

	#Retrieve key used for making payment
	stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

	#if unable to create charge, HTTP error will be raised by stripe.
	charge = stripe.Charge.create(
		amount = t_booking.get_price(),
		currency = 'nok',
		description = 'Hytte booking',
		source = token_data['id'],
		#metadata = {'booking_id': booking_id},
	)

	#Create booking
	booking_result = Booking.create_booking_from_tentative(t_booking, contact, charge.id)
	if booking_result == False:
		#Fatal error, booking payed for, but not reserved!
		#TODO: Try giving refund here?
		return HttpResponse("Fatal error. Booking payed for but not reserved")

	booking = Booking.objects.get(id=booking_result)
	
	#Add late_arrival on booking
	booking.late_arrival = contact_form.cleaned_data['late_arrival']
	booking.save()

	#Send confirmation mail 
	cabins = booking.cabins.all()
	titles = []
	for cabin in cabins:
		titles.append(cabin.title)

	data = {
		'from_date': booking.from_date.strftime('%d.%m.%Y'),
		'to_date': booking.to_date.strftime('%d.%m.%Y'),
		'cabin_titles': titles,
		'host': request.get_host() ,
	}

	checkmark_url = request.build_absolute_uri() 

	msg_plain = render_to_string('email/confirmation.txt', data)
	msg_html = render_to_string('email/confirmation.html', data)

	send_mail(
		'Strandbu Camping - Bekreftelse',
		msg_plain,
		'some@sender.com',
		['some@receiver.com'],
		html_message=msg_html,
	)

	return redirect('booking_confirmation')
	

def BookingConfirmation(request):

	args = {}
	args = add_alerts_from_session(request, args)

	return render(request, 'main/booking_confirmation.html', args)





def ShowCabins_show(request, _args):

	#Get t_booking, if any
	t_booking = get_t_booking(request)

	#Retrieve search form data
	search_form_data = _args['cabin_search_form_data']

	#Retrieve dates
	from_date = datetime.datetime.strptime(search_form_data['from_date'], "%d.%m.%y").date()
	to_date = datetime.datetime.strptime(search_form_data['to_date'], "%d.%m.%y").date()

	#Get available cabins, if t_booking is None it will be ignored in get_available_cabins method
	cabins = Booking.get_available_cabins(from_date, to_date, t_booking=t_booking)
	if _args['action'] == 'add_cabin':
		#Remove t_booking cabins
		cabins = Booking.remove_cabins_from_set(cabins, t_booking)

	#Remove equivalent cabins
	cabins = Booking.remove_similar_cabins(cabins)

	#Deactivate t_booking if we are not adding cabin. 
	if _args['action'] == 'show':
		if not t_booking == None:
			t_booking.deactivate()
		request.session['t_booking_id'] = None		

	#Declare t_booking_id
	t_booking_id = None
	if not t_booking == None:
		t_booking_id = t_booking.id

	#Create cabin dict with information about all cabins
	cabins_dict = {}
	for c in cabins:
		res = {}
		res['number'] = c.number
		res['persons'] = c.persons
		res['title'] = c.title
		res['short_description'] = c.short_description
		res['long_description'] = c.long_description
		res['equipment'] = c.equipment.all().values_list('eqp', flat=True)
		res['images'] = c.images.all().values_list('img', flat=True) 
		res['price_kr'] = c.price_kr

		cabin_choose_data = {
			'from_date': search_form_data['from_date'],
			'to_date': search_form_data['to_date'],
			'cabin_number': c.number.__str__(),
			't_booking_id': t_booking_id,
			'action': 'add_cabin',
		}

		res['choose_form_single'] = forms.CabinChoose(initial=cabin_choose_data)

		cabins_dict['cabin_' + c.number.__str__()] = res

	#Declare info header, displayed on top of page
	info_header = ""

	no_cabins = False
	if cabins.count() == 0:
		info_header = "Det er desverre ingen hytter som er ledig hele denne perioden."
		no_cabins = True

	#Check that dates are valid
	date_error = TentativeBooking.booking_dates_get_error(from_date, to_date)
	if not date_error == None:
		request.session = add_alert(request, date_error, type='warning')
		return redirect('booking')

	if AdminSettings.booking_closed_time(from_date):
		request.session = add_alert(request, 'Bestilling for i dag er stengt. Ta kontakt (+47) 777 15 340 for bestilling.', type='warning')
		return redirect('booking')

	#Convert dates to string
	from_date_str = datetime.datetime.strftime(from_date, "%d.%m.%y")
	to_date_str = datetime.datetime.strftime(to_date, "%d.%m.%y")

	#Declare arguments
	args = {
		'cabins' : cabins_dict, 
		'cabin_search_form': forms.CabinSearch(search_form_data), 
		'info_header': info_header, 
		'from_date_str': from_date_str, 
		'to_date_str': to_date_str,
		'no_cabins': no_cabins,
		'action': _args['action'],
	}

	#Merge args. Note args will override fields in _args
	args = {**_args, **args}

	args = add_alerts_from_session(request, args)

	return render(request, 'main/show_cabins.html', args)


def ShowCabins_add_cabin(request, _args):

	#Add cabin to t_booking
	t_booking = get_valid_t_booking(request)

	if t_booking == False:
		request.session = add_alert(request, 'Klarer ikke legge til hytte. Finner ikke bestilling. Vennligst prøv igjen.', type='warning')
		return redirect('show_cabins')

	return ShowCabins_show(request, _args)

#Show current booking overview based on session
def BookingOverview_show(request, _args):
	t_booking = get_valid_t_booking(request)
	if t_booking == False:
		request.session = add_alert(request, "Klarer ikke finne bestilling. Vennligst prøv igjen.", type='warning')
		return redirect('show_cabins')

	#Check that t_booking is active, replace if not active
	if not t_booking.is_active():
		#t_booking not active, try creating active copy
		t_booking = t_booking.create_active_copy()
		if t_booking == False:
			#Unable to create active copy, redirecting
			request.session = add_alert(request, "Sesjon utløpt. Vennligst prøv igjen.", type='primary')
			return redirect('show_cabins')	
		request.session['t_booking_id'] = t_booking_id

	#Check that t_booking not empty
	if t_booking.cabins.all().count() == 0:
		request.session = add_alert(request, "Klarer ikke vise bestilling. Vennligst prøv igjen.", type='warning')
		return redirect('show_cabins')	

	#Check that booking dates are valid
	if t_booking.dates_are_valid() == False:
		request.session = add_alert(request, 'Ugyldig datoer. Vennligst prøv igjen.', type="warning")
		request.session['t_booking_id'] = None
		return redirect('show_cabins')

	#Serialize cabins
	cabins = {}
	for c in t_booking.cabins.all():
		cabins['cabin_' + c.number.__str__()] = {
			'number': c.number,
			'title': c.title,
		}

	#Serialize t_booking information
	t_booking_info = {
		'cabins': cabins,
		'from_date': t_booking.from_date.strftime('%d.%m.%Y'),
		'to_date': t_booking.to_date.strftime('%d.%m.%Y'),
		'price': t_booking.get_price(),
		'id': t_booking.id,
		'JSON': serializers.TentativeBookingSerializer(t_booking).data,
	}

	#Declare arguments
	args = {
		't_booking': t_booking_info, 
		'info_form': forms.PreChargeInfoForm(), 
		'cabin_search_form': _args['cabin_search_form'],
	}

	#Add alerts to args
	args = add_alerts_from_session(request, args)

	return render(request, 'main/booking_overview.html', args)


def BookingOverview_add_cabin(request, _args):
	#Retrieve choose_form
	choose_form = _args['choose_form']
	if not choose_form.is_valid():
		request.session = add_alert(request, 'Klarer ikke legge til hytte. Vennligst prøv igjen.', type='danger')
		return redirect('show_cabins')

	#retrieve data from choose_form
	from_date = datetime.datetime.strptime(choose_form.cleaned_data['from_date'], "%d.%m.%y").date()
	to_date = datetime.datetime.strptime(choose_form.cleaned_data['to_date'], "%d.%m.%y").date()
	number = choose_form.cleaned_data['cabin_number']
	cabin = Cabin.objects.filter(number=number)

	#Find t_booking
	t_booking = get_t_booking(request)
	if t_booking == None:
		#Create t_booking
		t_booking_id = Booking.create_booking(from_date, to_date, cabin, False)

		if t_booking_id == False:
			#NOTE: retrieving error based on booking without lock
			booking_error = Booking.get_create_booking_error(from_date, to_date, cabin, Booking.objects.all())
			if booking_error == None:
				booking_error = "En feil har oppstått. Vennligst prøv igjen."

			request.session = add_alert(request, booking_error, type='primary')
			return redirect('show_cabins')	

		t_booking = TentativeBooking.objects.get(id=t_booking_id)
		request.session['t_booking_id'] = t_booking_id
		
	else:
		#Add cabin to existing t_booking
		t_booking.cabins.add(cabin.first())
		t_booking.save()
		if not t_booking.is_valid():
			request.session = add_alert(request, "Bestilling ikke lengre gyldig. Vennligst prøv igjen.", type='primary')
			t_booking.deactivate()
			return redirect('show_cabins')
	request.session['t_booking_id'] = t_booking.id

	return BookingOverview_show(request, _args)



def BookingOverview_remove_cabin(request, _args):

	t_booking = get_t_booking(request)
	if t_booking == None:
		request.session = add_alert(request, "Klarer ikke fjerne hytte, finner ikke bestilling. Vennligst prøv igjen.", type='warning')
		return redirect('show_cabins')

	if not t_booking.is_valid():
		request.session = add_alert(request, "Sesjon utløpt. Vennligst prøv igjen.", type='primary')
		return BookingOverview_show(request, _args)

	if not 'cabin_number' in request.POST:
		request.session = add_alert(request, "Klarer ikke fjerne hytte, finner ikke hytte. Vennligst prøv igjen.", type='warning')
		return redirect('show_cabins')

	cabin_number = request.POST['cabin_number']

	cabin = Cabin.objects.filter(number=cabin_number).first()
	if cabin == None:
		request.session = add_alert(request, "Klarer ikke fjerne hytte, finner ikke hytte. Vennligst prøv igjen.", type='danger')

	t_booking.cabins.remove(cabin)
	t_booking.save()

	if t_booking.cabins.all().count() == 0:
		request.session = add_alert(request, "Alle hytter fjernet. Velg hytte på nytt.", type='primary')
		return redirect('show_cabins')		

	return BookingOverview_show(request, _args)




def add_alerts_from_session(request, _args):
	if 'alerts' in request.session:
		_args['alerts'] = request.session['alerts']
		
	request.session['alerts'] = None
	return _args


def add_alert(request, _alert, **kwargs):

	a_type = 'primary'
	if 'type' in kwargs:
		a_type = kwargs['type']

	a_starter = ''
	if 'starter' in kwargs:
		a_starter = kwargs['starter']

	alerts = []
	if 'alerts' in request.session:
		if request.session['alerts'] is not None:
			alerts = request.session['alerts']

	alerts.append((_alert, a_type, a_starter))
	request.session['alerts'] = alerts

	return request.session


def deactivate_session_t_booking(request):
	if 't_booking_id' in request.session:
		t_booking_id = request.session['t_booking_id'] 
		t_booking = TentativeBooking.objects.filter(id=t_booking_id).first()
		if not t_booking == None:
			t_booking.deactivate()

def get_t_booking(request):
	if 't_booking_id' in request.session:
		t_id = request.session['t_booking_id']
		t_booking = TentativeBooking.objects.filter(id=t_id).first()
		if not t_booking == None:
				return t_booking
	return None

def get_valid_t_booking(request):
	t_booking = get_t_booking(request)
	if t_booking == None:
		return False
	if t_booking.is_valid():
		return t_booking

	if not t_booking.is_active():
		t_booking_id = t_booking.create_active_copy()
		if t_booking_id == False:
			return False
		return TentativeBooking.objects.get(id=t_booking_id)
	return False

