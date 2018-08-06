from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from . import forms
from main.views import add_alert, add_alerts_from_session
from main import models as main_models
import datetime
from django.utils import timezone


def InternalView(request):
	if not request.user.is_authenticated:
		return redirect('login')

	args = {'user': request.user}

	return render(request, 'intern/home.html', args)

def LoginView(request):
	if request.user.is_authenticated:
		if 'login_redirect' in request.session:
			return redirect(requet.session['login_redirect'])
		return redirect('intern')

	login_form = forms.LoginForm()
	args = {'login_form': login_form}

	if 'username' in request.POST and 'password' in request.POST:
		login_form = forms.LoginForm(request.POST)
		args['login_form'] = login_form

		if not login_form.is_valid():
			args['errors'] = login_form.errors.__str__()
			return render(request, 'login.html', args)

		#Login user

		username = login_form.cleaned_data['username']
		password = login_form.cleaned_data['password']

		user = authenticate(request, username=username, password=password)

		if user is not None:
			login(request, user)
			if 'login_redirect' in request.session:
				return redirect(request.session['login_redirect'])
			return redirect('intern')

		#User failed to login
		args['errors'] = 'Feil brukernavn eller passord'
		return render(request, 'intern/login.html', args)

	args = add_alerts_from_session(request, args)

	#Display empty login form
	return render(request, 'intern/login.html', args)

def LogoutView(request):
	logout(request)
	request.session = add_alert(request, 'Du er nå logget ut.', type='primary')

	return redirect('login')

def InternalBooking(request):

	if not request.user.is_authenticated:
		request.session['login_redirect'] = 'intern_booking'
		return redirect('login')

	now = timezone.localtime(timezone.now()).date()

	from_date = now - datetime.timedelta(days=3)
	to_date = now + datetime.timedelta(days=4)

	bookings = main_models.Booking.get_final_bookings(from_date, to_date)

	dates_to_show = main_models.get_dates_between(from_date, to_date)

	cabin_rows = []
	edit_booking_forms = []

	for cabin in main_models.Cabin.objects.all().order_by('number'):
		found_booking = False
		relevant_bookings = []
		for booking in bookings:
			if booking.contains_cabin_number(cabin.number):
				found_booking = True
				relevant_bookings.append(booking)

		row_data = ['<th scope="row" class="booking-table-header-cell">' + cabin.number.__str__() + '</th>']

		for date in dates_to_show:
			date_bookings = []
			for booking in relevant_bookings:
				booking_dates = main_models.get_dates_between(booking.from_date, booking.to_date)
				if main_models.dates_overlap([date], booking_dates):
					date_bookings.append(booking)
					
			data = ""
			col_span = "1"
			card_attr = ""

			if len(date_bookings) == 1:
				booking = date_bookings[0]

				if not date == booking.from_date:
					if not booking.double_booked():
						continue


				# attr = 'data-toggle="modal" data-target="#booking-modal-' + date_bookings[0].id.__str__() + '"'
				card_attr = 'class="card bg-primary booking-card" style="color:white" onClick="showBookingModal(\'' + booking.id.__str__() + '\')"'
				
				booking_form = forms.EditBookingForm(instance=booking, contact=booking.contact)

				edit_booking_forms.append((booking, booking_form))

				data = '<div ' + card_attr + '>' + booking.contact.name + '</div>'
				if booking.double_booked():
					col_span = "1"
				else:
					col_span = booking.get_nights().__str__()
					
			if len(date_bookings) > 1:
				# Double booking!
				card_attr = ' class="card bg-danger booking-card" onClick="showBookingModal(\'' + date_bookings[0].id.__str__() + '\')"'
				data = '<div ' + card_attr + ' ><b>OBS! Dobbel booking</b></div>'
				# attr = 'data-toggle="modal" data-target="#booking-modal-' + date_bookings[0].id + '"'

			row_data.append('<td align="center" class="booking-table-cell" scope="col" colspan="' + col_span + '">' + data + '</td>')

		row = {
			'data': row_data,
			# 'cabin_number': cabin.number,
		}

		cabin_rows.append(row)



	args = {
		'cabin_rows': cabin_rows,
		'dates_to_show': dates_to_show,
		'bookings': bookings,
		'edit_booking_forms': edit_booking_forms,
	}


	return render(request, 'intern/booking.html', args)