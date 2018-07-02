from django.db import models, transaction
from django_countries.fields import CountryField
from django.utils import timezone
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
	late_arrival = models.BooleanField(default=False)



class = Booking(models.Model):
	from_date = models.DateField()
	to_date = models.DateField()
	cabins = models.ManyToManyField(Cabin)

	created_date = models.DateTimeField(auto_now=True)
	late_arrival = models.BooleanField()

class TentativeBooking(Booking):
	from_date = models.DateField()
	to_date = models.DateField()
	cabins = models.ManyToManyField(Cabin)

	created_date = models.DateTimeField(auto_now=True)
	late_arrival = models.BooleanField()

	def is_active(self):
		active_time = 20

		#Add active time if cabin if booking multiple cabins
		if len(self.cabins) >= 2:
			active_time = 20

		if timezone.now() >= self.created_date + datetime.timedelta(minutes=active_time):
			return False
		return True

	def get_price(self):
		nights = len(get_dates_between(self.from_date, self.to_date))
		price = 0
		for cabin in self.cabins:
			price = price + (cabin.price * nights)
		return price

	@classmethod
	def get_active_bookings(cls):
		ids = []
		for t_b in TentativeBooking.objects.all():
			if t_b.is_active():
				ids.append(t_b.id)
		return TentativeBooking.objects.filter(id__in=ids)

	def __str__(self):
		return "[" + self.cabin_number.__str__() + "] " + self.from_date.__str__() + " -> " + self.to_date.__str__() + " (" + self.created_date.__str__() + ")" + " <" + self.id.__str__() + ">"



class FinalBooking(Booking):
	from_date = models.DateField()
	to_date = models.DateField()
	cabin_number = models.IntegerField()
	active = models.BooleanField(default=True)

	contact = models.ForeignKey(ContactInfo, on_delete=models.SET_NULL, null=True)
	late_arrival = models.BooleanField()

	def __str__(self):
		return "[" + self.cabin_number.__str__() + "] " + self.from_date.__str__() + " -> " + self.to_date.__str__()



class BookingManager(models.Model):
	bookings = Booking.objects.all()
	tentative_bookings = TentativeBooking.objects.all()	#Not really using these fields

	@classmethod
	def get_available_cabins(cls, _from_date, _to_date, _persons):

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

		available_cabins = Cabin.objects.all()

		#fetch all bookings that are active
		bookings = Booking.objects.filter(active=True)

		#fetch all tentative bookings
		tentative_bookings = TentativeBooking.get_active_bookings()

		#create array of dates to check
		dates_to_check = get_dates_between(_from_date, _to_date)

		#check normal bookings
		for b in bookings:
			if not b.active:
				#Booking not active, check next booking
				continue

			#The dates in this booking
			booking_dates = get_dates_between(b.from_date, b.to_date)

			#Check all cabins in this booking
			for cabin in b.cabins:
				if not cabin_number_match(cabin.number, available_cabins):
					#cabin not in available cains, check next cabin
					continue
				#Check if overlap
				if dates_are_overlapping(booking_dates, dates_to_check):
					#remove this cabin number from available cabins
					available_cabins = available_cabins.exclude(number=cabin.number)
		
		#check tentative bookings
		for t_b in tentative_bookings:
			if not t_b.is_active():
				#Booking not active, ignore this, check next
				continue

			booking_dates = get_dates_between(t_b.from_date, t_b.to_date)
			for cabin in t_b.cabins:
				if not cabin_number_match(cabin.number, available_cabins):
					#Booking-cabin is not in cabin types, check next cabin
					continue
				#Check if dates are overlapping
				if dates_are_overlapping(booking_dates, dates_to_check):
					#remove this cabin number from available cabins
					available_cabins = available_cabins.exclude(number=cabin.number)


		#Remove cabins that don't match persons requirement
		available_cabins = available_cabins.filter(persons__gte=_persons)

		return available_cabins

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

	@classmethod
	def create_tentative_booking(cls, _from_date, _to_date, _number):
		with transaction.atomic():
			all_bookings = Booking.objects.select_for_update()	#will lock all bookings and tentative bookings until the end of this transaction block
			all_tentative_bookings = TentativeBooking.objects.select_for_update() #lock all tentative bookings

			#Check if this is a valid booking
			tentative_booking = TentativeBooking()	

			tentative_booking.from_date = _from_date
			tentative_booking.to_date = _to_date
			tentative_booking.cabin_number = _number
			#tentative_booking.created_date = datetime.date.now()	#Has auto_now

			print("---------------")
			print(tentative_booking)
			print(all_bookings)
			print(all_tentative_bookings)
			print(tentative_booking.from_date)
			print("----------------")

			if tentative_booking_is_valid(tentative_booking, all_bookings, all_tentative_bookings):
				tentative_booking.save()
				return tentative_booking.id
			else:
				return False


#Helper methods

def get_dates_between(_from_date, _to_date):
	#check that _to_date is after _from_date
	if _to_date <= _from_date:
		return None

	if isinstance(_from_date, str):
		_from_date = datetime.datetime.strptime(_from_date, '%Y-%m-%d') 

	if isinstance(_to_date, str):
		_to_date = datetime.datetime.strptime(_to_date, '%Y-%m-%d')

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

def cabin_number_match(_cabin_number, _cabin_types):
	number_is_relevant = False
	#check if cabin number is in cabin_types
	for c in _cabin_types:
		if c.number == _cabin_number:
			number_is_relevant = True
			break

	return number_is_relevant

def booking_is_valid(_booking, _all_bookings):
	#note: _booking might be tentativeBooking, consider making a superclass
	#create array of dates to check
	dates_to_check = get_dates_between(_booking.from_date, _booking.to_date)

	for b in _all_bookings:
		for 
		if not (_booking.cabin_number == b.cabin_number or b.active == False):
			#Check next booking, these bookings don't affect each other
			continue

		booking_dates = get_dates_between(b.from_date, b.to_date)
		#if dates in bookings are overlapping, this booking is not valid
		if dates_are_overlapping(booking_dates, dates_to_check):
			#bookings overlap, booking not valid
			return False
	#If method comes here, then everything ok, booking is valid
	return True

def tentative_booking_is_valid(_t_booking, _all_bookings, _all_t_bookings):
	#create array of dates to check
	dates_to_check = get_dates_between(_t_booking.from_date, _t_booking.to_date)

	#check noraml bookings
	if not booking_is_valid(_t_booking, _all_bookings):
		return False

	#check tentative bookings
	for t_b in _all_t_bookings:
		if not _t_booking.cabin_number == t_b.cabin_number or not t_b.is_active():
			#Check next booking, these bookings don't affect each other
			continue

		booking_dates = get_dates_between(t_b.from_date, t_b.to_date)
		#if dates in bookings are overlapping, this booking is not valid
		if dates_are_overlapping(booking_dates, dates_to_check):
			#remove this cabin number from available cabins
			return False

	#If method comes here, then everything ok, booking is valid
	return True

def bookings_overlap(b1, b2):
	#note: bookings might be tentative
	#Therefore method do not check if bookings are active!
	if not b1.cabin_number == b2.cabin_number:
		return False

	dates_1 = get_dates_between(b1.from_date, b1.to_date)
	dates_2 = get_dates_between(b2.from_date, b2.to_date)

	if dates_are_overlapping(dates_1, dates_2):
		return True
	return False