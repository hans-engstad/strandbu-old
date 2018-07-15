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

	args = add_message(request, args)

	return render(request, 'main/home.html', args)


def ShowCabins(request):

	if not request.method == 'POST':
		return redirect('home')


	#get fields
	from_date_field = request.POST.get('from_date')
	to_date_field = request.POST.get('to_date')
	persons  = request.POST.get('persons')
	
	#check that all fields was passed in the request
	if from_date_field == None or to_date_field == None or persons == None:
		return HttpResponse("Missing one or more post fields.")
	

	data = {'from_date': from_date_field,
			'to_date': to_date_field,
			'persons': persons}

	#instantiate form
	form = forms.CabinSearch(data)
	if form.is_valid():
		#Check database for search results

		from_date = datetime.strptime(form.cleaned_data['from_date'], "%d.%m.%y")
		to_date = datetime.strptime(form.cleaned_data['to_date'], "%d.%m.%y")
		persons = form.cleaned_data['persons']

		if from_date >= to_date:
			return HttpResponse("Checkout must be after checkin.")

		t_booking = None
		if not 'booking_action' in request.POST:
			if 't_booking_id' in request.session:
				t_booking = Booking.objects.filter(id=request.session['t_booking_id']).first()

		cabins = Booking.get_available_cabins(from_date, to_date, persons, t_booking=t_booking)

		t_booking_id = -1
		if 'booking_action' in request.POST:
			if request.POST.get('booking_action') == 'add_cabin':
				t_booking_id = request.POST.get('t_booking_id')
				# t_booking = TentativeBooking.objects.filter(id=t_booking_id).first()


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
				'from_date': form.cleaned_data['from_date'],
				'to_date': form.cleaned_data['to_date'],
				'cabin_number': c.number.__str__(),
				't_booking_id': t_booking_id,
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
			'cabin_search_form': form, 
			'info_header': info_header, 
			'from_date_str': from_date_str, 
			'to_date_str': to_date_str,
		}

		args = add_message(request, args)

		return render(request, 'main/show_cabins.html', args)
	else:
		print(form.errors)
		#TODO: kan sende en redirect til home page, der error meldigen blir sendt med og vises frem 
		#	på det spesifiserte feltet
		return HttpResponse("Input did not pass form validation")

		
# @never_cache
def BookingOverview(request):
	#Id of t_booking, -1 if nothing (Also default value in choose_form)
	t_booking_id = -1
	
	#Find session t_booking if any
	if 't_booking_id' in request.session:
		tmp_id = request.session['t_booking_id']
		t_booking = TentativeBooking.objects.filter(id=tmp_id).first()
		if not t_booking == None:
			if t_booking.is_active():
				t_booking_id = tmp_id
	elif not request.method == 'POST':
		return HttpResponse('Request method must be POST.')

	#Instantiate cabin choose form
	choose_form = forms.CabinChoose(request.POST)

	if choose_form.is_valid():
		#Note: Form field will override session if not -1
		t_booking_id_form = choose_form.cleaned_data['t_booking_id']
		if not t_booking_id_form == -1:
			t_booking_id = t_booking_id_form


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
			#Cabin no longer available, try again
			#Consider feedback to end-user here, to avoid confusion
			#Or redirect to cabin show page, with choose form.
			return redirect('home')
	else:
		#t_booking already exist
		t_booking = TentativeBooking.objects.filter(id=t_booking_id).first()
		
		#add cabin to this booking if choose form is valid
		if choose_form.is_valid():
			number = choose_form.cleaned_data['cabin_number']
			cabin = Cabin.objects.filter(number=number).first()

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


	#Define Cabin Search Form. Used when adding new cabin
	cabin_search_form = forms.CabinSearch(request.POST)
	if 'cabin_search_form_data' in request.session and not cabin_search_form.is_valid():
		cabin_search_form = forms.CabinSearch(request.session['cabin_search_form_data'])

	if not cabin_search_form.is_valid():
		return HttpResponse("Cabin search form is not valid")

	args = {
		't_booking': t_booking_info, 
		'info_form': forms.PreChargeInfoForm(), 
		'cabin_search_form': cabin_search_form, 
	}

	args = add_message(request, args)

	

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
	t_booking = TentativeBooking.objects.get(id=t_booking_id)	#TODO: We might not find this booking!
	
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

		request.session['message_starter'] = "OBS!"
		# request.session['message'] = "Session not updated. Payment not completed. Please try again."
		request.session['message'] = "Sesjon ikke oppdatert. Betaling ikke fullført. Vennligst prøv igjen."
		request.session['message_type'] = "danger"

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
	args = add_message(request, args)

	return render(request, 'main/booking_confirmation.html', args)


def add_message(request, _args):
	if 'message' in request.session:
		_args['message'] = request.session['message']
		request.session['message'] = None
	if 'message_type' in request.session:
		_args['message_type'] = request.session['message_type']
		request.session['message_type'] = None
	if 'message_starter' in request.session:
		_args['message_starter'] = request.session['message_starter']
		request.session['message_starter'] = None

	return _args