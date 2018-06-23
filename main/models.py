from django.db import models
from django_countries.fields import CountryField
import datetime

# Create your models here.


class CabinImage(models.Model):
	name = models.CharField(max_length=50, default="")
	img = models.ImageField(upload_to="cabins")

	def __str__(self):
		return self.name

class CabinEquipment(models.Model):
	eqp = models.CharField(max_length=50)

	def __str__(self):
		return self.eqp

class Cabin(models.Model):
	number = models.IntegerField(unique=True)
	persons = models.IntegerField()

	title = models.CharField(max_length=100, default="")
	short_description = models.CharField(max_length=256, default="")
	long_description = models.CharField(max_length=512, default="")

	price = models.IntegerField()

	images = models.ManyToManyField(CabinImage, blank=True)

	equipment = models.ManyToManyField(CabinEquipment, blank=True)

	@classmethod
	def get_cabin_by_number(self, _number):
		cabin = Cabin.objects.filter(number=_number)
		return cabin

	def __str__(self):
		return "[" + self.number.__str__() + "]"


class ContactInfo(models.Model):
	name = models.CharField(max_length=255)
	mail = models.CharField(max_length=255)
	phone = models.CharField(max_length=30)
	country = CountryField()


class BookingManager(models.Model):


class TentativeBooking(models.Model):
	

class Booking(models.Model):
	from_date = models.DateField(50)
	to_date = models.DateField()
	cabin_number = models.IntegerField()
	active = models.BooleanField(default=True)

	contact = models.ForeignKey(ContactInfo, on_delete=models.SET_NULL, null=True)


	@classmethod
	def get_available_cabins(cls, _from_date, _to_date, _persons):

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
			if dates_are_overlapping(booking_dates, dates_to_check):
				#remove this cabin number from available cabins
				remove_current_cabin = True

			#remove current cabin if var is true
			if remove_current_cabin:
				cabin_types = cabin_types.exclude(number=b.cabin_number)

		#print(cabin_types)

		return cabin_types

	@classmethod
	def create_booking(cls, _from_date, _to_date, _number, _contact):
		with transaction.atomic():
			all_bookings = Booking.objects.select_for_update()	#will lock all bookings until the end of this transaction block

			#Check if this is a valid booking
			booking = Booking()	

			booking.from_date = _from_date
			booking.to_date = _to_date
			booking.cabin_number = _number
			booking.contact = _contact

			if booking_is_valid(booking, all_bookings):
				booking.save()
				return True
			else:
				return False



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

def dates_are_overlapping(_date1, _date2):
	#note date1 and date2 are arrays
	for d1 in _date1:
		for d2 in _date2:
			if d1 == d2:
				return True
	return False

def booking_is_valid(cls, _booking, _all_bookings):

	#create array of dates to check
	dates_to_check = get_dates_between(_booking.from_date, booking.to_date)

	for b in bookings:
		if _booking.cabin_number == b.cabin_number:
			#Check next booking, these bookings don't affect each other
			continue

		booking_dates = get_dates_between(b.from_date, b.to_date)
		#if dates in bookings are overlapping, this booking is not valid
		if dates_are_overlapping(booking_dates, dates_to_check):
			#remove this cabin number from available cabins
			return False
	#If method comes here, then everything ok, booking is valid
	return True
