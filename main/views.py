from django.shortcuts import render
from django.shortcuts import render, HttpResponse, redirect
from main import forms
from datetime import datetime
from main.models import BookingManager, TentativeBooking, Cabin
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

			cabins = BookingManager.get_available_cabins(from_date, to_date, persons)

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
				res['price'] = c.price

				data = {
					'from_date': from_date,
					'to_date': to_date,
					'number': c.number
				}

				res['choose_form'] = forms.CabinChoose(initial=data)	#Used to render form that will power choose cabin button
				#res['choose_form'] = CabinChoose()


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

def ContactInfo(request):
	if request.method == 'POST':
		chooseForm = forms.CabinChoose(request.POST)
		if chooseForm.is_valid():
			#create tentative booking

			from_date = chooseForm.cleaned_data['from_date']
			to_date = chooseForm.cleaned_data['to_date']
			number = chooseForm.cleaned_data['number']

			t_booking_id = BookingManager.create_tentative_booking(from_date, to_date, number)
			if t_booking_id == False:
				#Cabin no longer available, try again
				#Consider feedback to end-user here, to avoid confusion
				return redirect('home')

			contactForm = forms.Contact()

			data = chooseForm.data.copy()
			data['t_booking_id'] = t_booking_id
			newChooseForm = forms.CabinChoose(data)

			args = {'contactForm': contactForm, 'chooseForm': newChooseForm}


			#request.session['cabinChoose_num'] = newChooseForm.data['number']
			#request.session['cabinChoose_from_date'] = newChooseForm.data['from_date']
			#request.session['cabinChoose_to_date'] = newChooseForm.data['to_date']
			request.session['cabinChoose_tentative_id'] = t_booking_id

			return render(request, 'main/booking_contact_info.html', args)
		else:
			print("Choose form did not pass validation")
			print(chooseForm.errors)
			return redirect('home')

	else:
		print("Wrong request method")
		return redirect('home')

def BookingOverview(request):
	if not request.method == 'POST':
		return HttpResponse('Request method must be POST.')

	chooseForm = forms.CabinChoose(request.POST)
	if not chooseForm.is_valid():
		return HttpResponse('Choose form did not pass validation')
	
	t_booking_id
	if chooseForm.cleaned_data['t_booking_id'] == -1:
		#create tentative booking

		from_date = chooseForm.cleaned_data['from_date']
		to_date = chooseForm.cleaned_data['to_date']
		number = chooseForm.cleaned_data['number']

		t_booking_id = BookingManager.create_tentative_booking(from_date, to_date, number)
		if t_booking_id == False:
			#Cabin no longer available, try again
			#Consider feedback to end-user here, to avoid confusion
			#Or redirect to cabin show page, with choose form.
			return redirect('home')
		
	else:
		#Tentative booking already exist
		t_booking_id = chooseForm.cleaned_data['t_booking_id']

	#Current tentative booking
	t_booking = TentativeBooking.objects.get(id=t_booking_id)

	#Check that we have found a tentative booking
	if t_booking == None:
		return HttpResponse('Could not find tentative booking with id')

	#Check if tentative booking session is expired
	if not t_booking.is_active():
		return HttpResponse('Session expired')


	payment_form = forms.Payment()

	t_booking_info = {
		'number': t_booking.cabin_number,
		'from_date': t_booking.from_date.strftime('%d.%m.%Y'),
		'to_date': t_booking.to_date.strftime('%d.%m.%Y'),
		'price': t_booking.get_price(),
		'id': t_booking.id,
	}

	args = {
		't_booking': t_booking_info,
	}

	return render(request, 'main/payment_booking.html', args)


def ChargeBooking(request):

	if not request.method == 'POST':
		return HttpResponse('Request method must be POST.')

	form = forms.ChargeForm(request.POST)

	if not form.is_valid():
		return HttpResponse('Form did not pass validation. ' + form.errors)

	return HttpResponse(request.session)