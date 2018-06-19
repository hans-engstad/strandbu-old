from django.db import models
import datetime

# Create your models here.


class Cabin(models.Model):
	number = models.IntegerField(unique=True)
	persons = models.IntegerField()


	@classmethod
	def get_persons(self, _number):
		cabin = Cabin.objects.filter(number=_number)
		return cabin.persons

	def __str__(self):
		return "[" + self.number.__str__() + "]"


class Booking(models.Model):
	from_date = models.DateField()
	to_date = models.DateField()
	cabin_number = models.IntegerField()
	active = models.BooleanField(default=True)


	@classmethod
	def get_available_cabins(self, _from_date, _to_date, _persons):

		print(_persons)

		#check that _to_date is after _from_date
		if _to_date <= _from_date:
			return []

		#check that _persons are positive
		if _persons <= 0:
			return []

		#convert _from_date and _to_date to datetime.date
		if isinstance(_from_date, datetime.datetime):
			_from_date = _from_date.date()
		if isinstance(_to_date, datetime.datetime):
			_to_date = _to_date.date()

		#fetch cabin types matching persons
		cabin_types = Cabin.objects.filter(persons__gte = _persons)

		#fetch all bookings that are active
		bookings = Booking.objects.filter(active=True)

		#create array of dates to check
		dates_to_check = get_dates_between(_from_date, _to_date)

		

		for b in bookings:
			remove_current_cabin = True

			#check if cabin number is in cabin_types
			for c in cabin_types:
				if c.number == b.cabin_number:
					remove_current_cabin = False
					break

			booking_dates = get_dates_between(b.from_date, b.to_date)
			#if this date is in dates_to_check, remove this cabin from available
			if dates_is_overlapping(booking_dates, dates_to_check):
				#remove this cabin number from available cabins
				remove_current_cabin = True

			#remove current cabin if var is true
			if remove_current_cabin:
				cabin_types = cabin_types.exclude(number=b.cabin_number)

		#print(cabin_types)

		return cabin_types


	def __str__(self):
		return "[" + self.cabin_number.__str__() + "] " + self.from_date.__str__() + " -> " + self.to_date.__str__()






	#def create_booking(self, _from_date, _to_date, _persons):




#Helper methods

def get_dates_between(_from_date, _to_date):
	#check that _to_date is after _from_date
	if _to_date <= _from_date:
		return None

	dates_to_check = []
	temp_date = _from_date
	delta_days = (_to_date - _from_date).days
	counter = 0
	while counter < delta_days:
		dates_to_check.append(temp_date)
		temp_date = temp_date + datetime.timedelta(days=1)
		counter += 1

	return dates_to_check

def dates_is_overlapping(_date1, _date2):
	#note date1 and date2 are arrays
	for d1 in _date1:
		for d2 in _date2:
			if d1 == d2:
				return True
	return False


