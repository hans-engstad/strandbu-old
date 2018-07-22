from django.shortcuts import render
from django.shortcuts import render, HttpResponse, redirect
from main import forms
from datetime import datetime
from main.models import Booking, Cabin, TentativeBooking, Contact
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
	
	form = forms.CabinSearch()
	args = {'cabin_search_form': form}

	request.session = add_alert(request, 'test1')
	request.session = add_alert(request, 'test2')
	args = add_alerts_from_session(request, args)


	return render(request, 'main/home.html', args)

# @never_cache
def ShowCabins(request):


	cabin_search_form = forms.CabinSearch(request.POST)
	if 'cabin_search_form_data' in request.session and not cabin_search_form.is_valid():
		cabin_search_form = forms.CabinSearch(request.session['cabin_search_form_data'])
	elif not request.method == 'POST':
		return HttpResponse('Request method must be POST.')

	if cabin_search_form.is_valid():
		#Check database for search results

		from_date = datetime.strptime(cabin_search_form.cleaned_data['from_date'], "%d.%m.%y")
		to_date = datetime.strptime(cabin_search_form.cleaned_data['to_date'], "%d.%m.%y")
		persons = cabin_search_form.cleaned_data['persons']

		if from_date >= to_date:
			return HttpResponse("Checkout must be after checkin.")

		
		t_booking = None
		t_booking_id = -1
		if 'booking_action' in request.POST:
			if request.POST.get('booking_action') == 'add_cabin':
				t_booking_id = request.POST.get('t_booking_id')
		elif 't_booking_id' in request.session:
			#Deactivate t_booking if we are not adding cabin. 
			t_booking = Booking.objects.filter(id=request.session['t_booking_id']).first()
			if not t_booking == None:
				t_booking.deactivate()
			request.session['t_booking_id'] = None

		cabins = Booking.get_available_cabins(from_date, to_date, persons, t_booking=t_booking)


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

			action = 'single_cabin'

			if 'booking_action' in request.POST:
				action = request.POST['booking_action']

			cabin_choose_data = {
				'from_date': cabin_search_form.cleaned_data['from_date'],
				'to_date': cabin_search_form.cleaned_data['to_date'],
				'cabin_number': c.number.__str__(),
				't_booking_id': t_booking_id,
				'action': action,
			}

			res['choose_form_single'] = forms.CabinChoose(initial=cabin_choose_data)

			cabins_dict['cabin_' + c.number.__str__()] = res

		info_header = ""

		if cabins.count() == 0:
			info_header = "Det er desverre ingen hytter som er ledig hele denne perioden."
		if persons >= 4:
			info_header = "Du kan bestille flere hytter ved å velge én om gangen."

		from_date_str = datetime.strftime(from_date, "%d.%m.%y")
		to_date_str = datetime.strftime(to_date, "%d.%m.%y")


		args = {
			'cabins' : cabins_dict, 
			'cabin_search_form': cabin_search_form, 
			'info_header': info_header, 
			'from_date_str': from_date_str, 
			'to_date_str': to_date_str,
		}

		args = add_alerts_from_session(request, args)

		return render(request, 'main/show_cabins.html', args)
	else:
		print(cabin_search_form.errors)
		#TODO: kan sende en redirect til home page, der error meldigen blir sendt med og vises frem 
		#	på det spesifiserte feltet
		return HttpResponse("Input did not pass form validation")

		
# @never_cache
def BookingOverview(request):
	
	#Define Cabin Search Form. Used when adding new cabin
	cabin_search_form = forms.CabinSearch(request.POST)
	if 'cabin_search_form_data' in request.session and not cabin_search_form.is_valid():
		cabin_search_form = forms.CabinSearch(request.session['cabin_search_form_data'])

	if not cabin_search_form.is_valid():
		return HttpResponse("Cabin search form is not valid")

	#Id of t_booking, -1 if nothing (Also default value in choose_form)
	t_booking_id = -1

	#Instantiate cabin choose form
	choose_form = forms.CabinChoose(request.POST)

	if choose_form.is_valid():
		

		action = choose_form.cleaned_data['action']
		if action == 'add_cabin':
			#Find session t_booking if any
			if 't_booking_id' in request.session:
				tmp_id = request.session['t_booking_id']
				t_booking = TentativeBooking.objects.filter(id=tmp_id).first()
				if not t_booking == None:
					if t_booking.is_active():
						t_booking_id = tmp_id

			#Note: Form field will override session if not -1
			t_booking_id_form = choose_form.cleaned_data['t_booking_id']
			if not t_booking_id_form == -1:
				t_booking_id = t_booking_id_form
		else:
			t_booking_id = -1
			deactivate_session_t_booking(request)



	if t_booking_id == -1:
		if not choose_form.is_valid():
			return HttpResponse("Choose form did not pass validation" + choose_form.errors.__str__())
		#create tentative booking
		from_date = datetime.strptime(choose_form.cleaned_data['from_date'], "%d.%m.%y")
		to_date = datetime.strptime(choose_form.cleaned_data['to_date'], "%d.%m.%y")

		number = choose_form.cleaned_data['cabin_number']
		cabin = Cabin.objects.filter(number=number)

		t_booking_id = Booking.create_booking(from_date, to_date, cabin, False)
		if t_booking_id == False:
			#Booking no longer valid, redirect to show_cabins	
			request.session['cabin_search_form_data'] = cabin_search_form.cleaned_data
			request = add_alert(request, "Hytte ikke lengre ledig. Vennligst prøv igjen.", type='primary')

			return redirect('show_cabins')
	else:
		#t_booking already exist
		t_booking = TentativeBooking.objects.filter(id=t_booking_id).first()
		
		if not t_booking.is_active():
			#Booking expired, try creating new
			t_booking_id = t_booking.create_active_copy()
			if not t_booking_id:
				#Unable to create copy-booking
				request.session['cabin_search_form_data'] = cabin_search_form.cleaned_data
				request = add_alert(request, "Hytte ikke lengre ledig. Vennligst prøv igjen.", type='primary')

				return redirect('show_cabins')

			t_booking = TentativeBooking.objects.filter(id=t_booking_id).first()

		#add cabin to this booking if choose form is valid
		if choose_form.is_valid():
			number = choose_form.cleaned_data['cabin_number']
			cabin = Cabin.objects.filter(number=number).first()

			if cabin in t_booking.cabins.all():
				request = add_alert(request, 'Valgt hytte er allerede lagt til. Bruk "Legg til hytte" knappen for å legge til flere.', type='primary')
			elif not cabin.is_available(t_booking.from_date, t_booking.to_date):
				#Cabin no longer avilable, try finding equivalent cabin
				eq_cabin = cabin.get_available_eq_cabin()
				if not eq_cabin:
					#No eq-cabins are available
					request = add_alert(request, 'Sesjon utløpt. Vennligst prøv igjen', type='primary')
					request.session['cabin_search_form_data'] = cabin_search_form.cleaned_data
					return redirect('show_cabins')
				cabin = eq_cabin

			t_booking.cabins.add(cabin)
			t_booking.save()


	#Current tentative booking
	t_booking = TentativeBooking.objects.filter(id=t_booking_id).first()

	#Check that we have found a tentative booking
	if t_booking == None:
		return HttpResponse('Could not find tentative booking with id')

	#Check if tentative booking session is expired
	if not t_booking.is_active():
		return HttpResponse('Session expired')

	cabins = {}
	for c in t_booking.cabins.all():
		cabins['cabin_' + c.number.__str__()] = {
			'number': c.number,
			'title': c.title,
		}

	request.session['t_booking_id'] = t_booking_id

	t_booking_info = {
		'cabins': cabins,
		'from_date': t_booking.from_date.strftime('%d.%m.%Y'),
		'to_date': t_booking.to_date.strftime('%d.%m.%Y'),
		'price': t_booking.get_price(),
		'id': t_booking.id,
		'JSON': serializers.TentativeBookingSerializer(t_booking).data,
	}


	

	args = {
		't_booking': t_booking_info, 
		'info_form': forms.PreChargeInfoForm(), 
		'cabin_search_form': cabin_search_form, 
	}

	args = add_alerts_from_session(request, args)

	

	return render(request, 'main/booking_overview.html', args)


def ChargeBooking(request):

	if not request.method == 'POST':
		return HttpResponse('Request method must be POST.')

	form = forms.ChargeForm(request.POST)

	if not form.is_valid():
		print(form.errors)
		return HttpResponse("Payment form did not pass validation. Aborting payment. Booking not created.")

	data = form.cleaned_data

	price = data['total_price']
	phone = data['phone']
	t_booking_id = data['t_booking_id']
	t_booking = TentativeBooking.objects.filter(id=t_booking_id).first()	#TODO: We might not find this booking!
	
	if t_booking == None:
		cabin_search_form = forms.CabinSearch(request.POST)
		if not cabin_search_form.is_valid():
			return HttpResponse("Cabin search form is not valid. Unable to redirect to overview. Payment aborted.")
		
		request.session['cabin_search_form_data'] = cabin_search_form.cleaned_data

		request = add_alert(request, "Sesjon ikke oppdatert. Betaling ikke fullført. Vennligst prøv igjen.", type='danger', starter='OBS!')

		return redirect('show_cabins')

	if not t_booking.is_active():
		#Try to re activate t_booking and redirect to booking overview
		t_booking_id = t_booking.create_active_copy()
		if t_booking_id == False:
			#Redirect with alert (Booking no longer valid)
			cabin_search_form = forms.CabinSearch(request.POST)
			if not cabin_search_form.is_valid():
				return HttpResponse("Cabin search form is not valid. Unable to redirect to overview. Payment aborted.")
			
			request.session['cabin_search_form_data'] = cabin_search_form.cleaned_data

			request = add_alert(request, "Sesjon ikke oppdatert. Betaling ikke fullført. Vennligst prøv igjen.", type='danger', starter='OBS!')

			return redirect('show_cabins')

		t_booking = TentativeBooking.objects.filter(id=t_booking_id).first()



	JSON_data = ast.literal_eval(data['t_booking_JSON'])
	t_booking_JSON = serializers.TentativeBookingSerializer(t_booking).data

	#Check that JSON t_booking matches t_booking
	field_names = ['id', 'from_date','to_date', 'cabins', 'created_date', 'active']
	if not JSON_data == t_booking_JSON:
		#Fields do not match, redirect to booking overview with updated booking
		request.session['t_booking_id'] = t_booking_id

		cabin_search_form = forms.CabinSearch(request.POST)
		if not cabin_search_form.is_valid():
			return HttpResponse("Cabin search form is not valid. Unable to redirect to overview. Payment aborted.")
		
		request.session['cabin_search_form_data'] = cabin_search_form.cleaned_data

		# request.session['message'] = "Session not updated. Payment not completed. Please try again."
		request = add_alert(request, "Sesjon ikke oppdatert. Betaling ikke fullført. Vennligst prøv igjen.", type='danger', starter='OBS!')

		return redirect('booking_overview')


	if t_booking == None:
		return HttpResponse("Unable to find tentative booking. Aborting payment.")

	#Check that price displayed matches t_booking price

	token = data['token']
	token_data = json.loads(token)

	contact_data = {
		'name': token_data['card']['name'],
		'email': token_data['email'],
		'phone': phone,
		'country': token_data['card']['address_country'],
		'late_arrival': data['late_arrival']
	}

	contact_form = forms.ContactForm(contact_data)

	if not contact_form.is_valid():
		return HttpResponse('Contact info did not pass validation. Aborting payment')

	contact = Contact.objects.create(
		name=contact_form.cleaned_data['name'],
		email=contact_form.cleaned_data['email'],
		phone=contact_form.cleaned_data['phone'],
		country=contact_form.cleaned_data['country'],
	)

	stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

	#if unable to create charge, HTTP error will be raised by stripe.
	charge = stripe.Charge.create(
		amount = t_booking.get_price(),
		currency = 'nok',
		description = 'Hytte booking',
		source = token_data['id'],
		#metadata = {'booking_id': booking_id},
	)

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
	}

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
	print(alerts)
	request.session['alerts'] = alerts

	return request.session


def deactivate_session_t_booking(request):
	if 't_booking_id' in request.session:
		t_booking_id = request.session['t_booking_id'] 
		t_booking = TentativeBooking.objects.filter(id=t_booking_id).first()
		if not t_booking == None:
			t_booking.deactivate()

