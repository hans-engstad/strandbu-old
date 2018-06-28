from django.shortcuts import render
from django.shortcuts import render, HttpResponse, redirect
from main.forms import CabinSearch, CabinChoose, Contact
from datetime import datetime
from main.models import BookingManager, TentativeBooking, Cabin
from django.contrib.staticfiles.templatetags.staticfiles import static
from strandbu.settings.dev import STRIPE_TEST_PUBLIC_KEY as stripe_pk
import os



# Create your views here.
def Home(request):

	form = CabinSearch()
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
		form = CabinSearch(data)
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

				res['choose_form'] = CabinChoose(initial=data)	#Used to render form that will power choose cabin button
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
		chooseForm = CabinChoose(request.POST)
		if chooseForm.is_valid():
			#create tentative booking

			from_date = chooseForm.data['from_date']
			to_date = chooseForm.data['to_date']
			number = chooseForm.data['number']

			t_booking_id = BookingManager.create_tentative_booking(from_date, to_date, number)
			if t_booking_id == False:
				#Cabin no longer available, try again
				#Consider feedback to end-user here, to avoid confusion
				return redirect('home')

			contactForm = Contact()

			data = chooseForm.data.copy()
			data['t_booking_id'] = t_booking_id
			newChooseForm = CabinChoose(data)

			args = {'contactForm': contactForm, 'chooseForm': newChooseForm}


			request.session['cabinChoose_num'] = newChooseForm.data['number']
			request.session['cabinChoose_from_date'] = newChooseForm.data['from_date']
			request.session['cabinChoose_to_date'] = newChooseForm.data['to_date']
			request.session['cabinChoose_tentative_id'] = t_booking_id

			return render(request, 'main/booking_contact_info.html', args)
		else:
			print("Choose form did not pass validation")
			print(chooseForm.errors)
			return redirect('home')

	else:
		print("Wrong request method")
		return redirect('home')

def ConfirmBooking(request):

	contactForm = Contact(request.POST)
	cabinChooseForm = CabinChoose(request.POST)

	booking_id = cabinChooseForm.data.get('t_booking_id')
	if not booking_id:
		return HttpResponse('Could not find tentative booking id')


	booking = TentativeBooking.objects.get(id=booking_id)

	if booking == None:
		#Booking does not exist, user have not taken correct path to this view
		return HttpResponse('Could not find booking with requested id')
	elif not booking.is_active():
		#Booking has expired
		print(booking)
		return HttpResponse('session have expired')
	elif contactForm.is_valid() and cabinChooseForm.is_valid() and booking_id:
		
		cabin = Cabin.objects.get(number=cabinChooseForm.data.get('number'))



		request.session['first_name'] = contactForm.data.get('full_name')
		request.session['email'] = contactForm.data.get('mail')
		request.session['phone'] = contactForm.data.get('phone')
		request.session['country'] = contactForm.data.get('country')

		args = {
			'contactForm': contactForm,
			'chooseForm': cabinChooseForm,
			'from_date': cabinChooseForm.data['from_date'],
			'to_date': cabinChooseForm.data['to_date'],
			'cabin': cabin,
			'stripe_pk': stripe_pk,
		}

		return render(request, 'main/confirm_booking.html', args)
	else:
		return HttpResponse('contactForm or cabinChooseForm did not pass validation')


def ChargeBooking(request):
	return HttpResponse(request.session)