from django.shortcuts import render
from django.shortcuts import render, HttpResponse, redirect
from main import forms
from datetime import datetime
from main.models import Booking, Cabin, TentativeBooking
from django.contrib.staticfiles.templatetags.staticfiles import static
from strandbu.settings.dev import STRIPE_TEST_PUBLIC_KEY as stripe_pk
import os



# Create your views here.
def Home(request):

	form = forms.CabinSearch()
	args = {'cabin_search_form': form}
	
	return render(request, 'main/home.html', args)




def ShowCabins(request):
	if request.method == 'POST':
		#get fields
		from_date_field = request.POST.get('from-date')
		to_date = request.POST.get('to-date')
		persons  = request.POST.get('persons')
		
		#check that all fields was passed in the request
		if from_date_field == None or to_date == None or persons == None:
			return HttpResponse("Missing one or more post fields.")
		
		#parse dates
		from_date = datetime.strptime(from_date_field, "%d.%m.%y")
		to_date = datetime.strptime(to_date, "%d.%m.%y")

		data = {'from_date': from_date,
				'to_date': to_date,
				'persons': persons}

		#instantiate form
		form = forms.CabinSearch(data)
		if form.is_valid():
			#Check database for search results

			from_date = form.cleaned_data['from_date']
			to_date = form.cleaned_data['to_date']
			persons = form.cleaned_data['persons']

			cabins = Booking.get_available_cabins(from_date, to_date, persons)

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
					'from_date': from_date,
					'to_date': to_date,
					'cabin_numbers': c.number,
				}

				res['choose_form_single'] = forms.CabinChoose(initial=cabin_choose_data)

				cabins_dict['cabin_' + c.number.__str__()] = res

			info_header = ""

			if cabins.count() == 0:
				info_header = "Det er desverre ingen hytter som er ledig hele denne perioden."
			
			print(cabins_dict)

			args = {'cabins' : cabins_dict, 'from_date' : from_date, 'to_date': to_date, 'info_header': info_header}

			return render(request, 'main/show_cabins.html', args)
		else:
			print(form.errors)
			#TODO: kan sende en redirect til home page, der error meldigen blir sendt med og vises frem 
			#	på det spesifiserte feltet
			return HttpResponse("Input did not pass form validation")
	else:
		return redirect('home')

def BookingOverview(request):
	if not request.method == 'POST':
		return HttpResponse('Request method must be POST.')

	choose_form = forms.CabinChoose(request.POST)
	if not choose_form.is_valid():
		return HttpResponse('Choose form did not pass validation: ' + choose_form.errors.__str__())
	
	t_booking_id = choose_form.cleaned_data['t_booking_id']
	if t_booking_id == -1:

		#create tentative booking
		from_date = choose_form.cleaned_data['from_date']
		to_date = choose_form.cleaned_data['to_date']

		numbers = list(map(int, choose_form.cleaned_data['cabin_numbers'].split(',')))
		cabins = Cabin.objects.filter(number__in=numbers)

		t_booking_id = Booking.create_booking(from_date, to_date, cabins, False)
		if t_booking_id == False:
			#Cabin no longer available, try again
			#Consider feedback to end-user here, to avoid confusion
			#Or redirect to cabin show page, with choose form.
			return redirect('home')

	#Current tentative booking
	t_booking = TentativeBooking.objects.get(id=t_booking_id)

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

	t_booking_info = {
		'cabins': cabins,
		'from_date': t_booking.from_date.strftime('%d.%m.%Y'),
		'to_date': t_booking.to_date.strftime('%d.%m.%Y'),
		'price': t_booking.get_price(),
		'id': t_booking.id,
	}

	args = {
		't_booking': t_booking_info, 'info_form': forms.PreChargeInfoForm()
	}

	print(request.POST)

	print(t_booking)

	return render(request, 'main/booking_overview.html', args)


def ChargeBooking(request):

	if not request.method == 'POST':
		return HttpResponse('Request method must be POST.')

	form = forms.ChargeForm(request.POST)

	print(request.POST)

	if not form.is_valid():
		return HttpResponse('Form did not pass validation. ' + form.errors)

	return HttpResponse(request.session)