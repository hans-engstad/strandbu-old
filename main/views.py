from django.shortcuts import render
# from django.views.generic import TemplateView
from django.shortcuts import render, HttpResponse
#from dateutil import parser
from main.forms import CabinSearch
from datetime import datetime
from main.models import Booking
#from strandbu.settings import dev as settings
from django.contrib.staticfiles.templatetags.staticfiles import static
import os



# Create your views here.
def Home(request):
	template_name = 'main/home.html'

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

				images = c.images.all().values_list('img', flat=True) 


				res['images'] = images
				

				cabins_dict['cabin_' + c.number.__str__()] = res

			info_header = "Det er desverre ingen hytter som er ledig hele denne perioden."
			info_header = info_header + "<br>Derimot er det mulig å dele opp i 2 perioder." 

			info_header = ""

			print(cabins_dict)

			args = {'cabins' : cabins_dict, 'from_date' : from_date, 'to_date': to_date, 'info_header': info_header}

			return render(request, 'main/show_cabins.html', args)
		else:
			print(form.errors)
			return HttpResponse("Input did not pass form validation")
		
		
	else:
		form = CabinSearch()
		
		args = {'cabin_search_form': form}
		return render(request, 'main/home.html', args)



