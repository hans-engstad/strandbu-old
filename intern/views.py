from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from . import forms
from main.views import add_alert


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

	#Display empty login form
	return render(request, 'intern/login.html', args)

def LogoutView(request):
	logout(request)
	request.session = add_alert(request, 'Du er nå logget ut.', type='primary')

	return redirect('home')

def InternalBooking(request):

	if not request.user.is_authenticated:
		request.session['login_redirect'] = 'intern_booking'
		return redirect('login')

	

	return redirect('home')