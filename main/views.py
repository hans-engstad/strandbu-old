from django.shortcuts import render
# from django.views.generic import TemplateView
from django.shortcuts import render, HttpResponse
from main.forms import CabinSearch


# Create your views here.
def Home(request):
	template_name = 'main/home.html'

	if request.method == 'POST':
		return HttpResponse("Posting to home")
	else:
		form = CabinSearch()
		
		args = {'cabin_search_form': form}
		return render(request, 'main/home.html', args)



