from django.shortcuts import render
# from django.views.generic import TemplateView
from django.shortcuts import render, HttpResponse, redirect
#from dateutil import parser
from main.forms import CabinSearch, CabinChoose, Contact
from datetime import datetime
from main.models import Booking
#from strandbu.settings import dev as settings
from django.contrib.staticfiles.templatetags.staticfiles import static
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

		data = {
			'from_date': request.POST.get('from_date'),
			'to_date': request.POST.get('to_date'),
			'number': request.POST.get('number')
		}

		chooseForm = CabinChoose(data)
		if chooseForm.is_valid():
			contactForm = Contact()
			args = {'contactForm': contactForm, 'chooseForm': chooseForm}

			return render(request, 'main/booking_contact_info.html', args)
		else:
			print("Choose form did not pass validation")
			print(chooseForm.errors)
			return redirect('home')

	else:
		print("Wrong request method")
		return redirect('home')