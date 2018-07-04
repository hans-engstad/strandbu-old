from django.db import models, transaction
from django.core.exceptions import ValidationError
from django_countries.fields import CountryField
from django.utils import timezone
from polymorphic.models import PolymorphicModel
import datetime
import pytz
import polymorphic


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

	price = models.IntegerField()	#Price in øre

	images = models.ManyToManyField(CabinImage, blank=True)

	equipment = models.ManyToManyField(CabinEquipment, blank=True)

	equivalent_cabins = models.ManyToManyField("self", blank=True)

	@property
	def price_kr(self):
		return int(self.price * 0.01)

	def is_available(self, _from_date, _to_date):
		bookings = Booking.get_bookings(_from_date, _to_date)
		for booking in bookings:
			for cabin in booking.cabins.all():
				if cabin.number == self.number:
					return False
		return True

	def __str__(self):
		return "[" + self.number.__str__() + "]"


class Contact(models.Model):
	name = models.CharField(max_length=255)
	email = models.CharField(max_length=255)
	phone = models.CharField(max_length=30)
	country = models.CharField(max_length=255)
	late_arrival = models.BooleanField(default=False)



class Booking(PolymorphicModel):
	#booking_ptr = models.ForeignKey(Booking, db_column='base_ptr', null=True, on_delete=models.SET_NULL)

	from_date = models.DateField()
	to_date = models.DateField()
	cabins = models.ManyToManyField(Cabin)

	created_date = models.DateTimeField(auto_now=True)
	late_arrival = models.BooleanField(default=False)

	


	@classmethod
	def create_booking(cls, _from_date, _to_date, _cabins, _is_final, **kwargs):
		with transaction.atomic():

			#check that booking is in future
			from_date_datetime = datetime.datetime.combine(_from_date, datetime.datetime.min.time())
			from_date_datetime_tz = pytz.timezone(timezone.get_default_timezone_name()).localize(from_date_datetime)
			if timezone.now() >= from_date_datetime_tz:
				return False

			all_bookings = Booking.objects.all().select_for_update()	#will lock all bookings until the end of this transaction block

			#Get all bookings with given dates and active
			bookings = Booking.get_bookings(_from_date, _to_date)

			#Check if this is a valid booking
			for cabin in _cabins:
				if not cabin.is_available(_from_date, _to_date):
					return False

				
			#Create booking model
			booking = TentativeBooking()
			if _is_final:
				booking = FinalBooking()
				booking.active = True

			booking.from_date = _from_date
			booking.to_date = _to_date
			
			
			if _is_final:
				booking.contact = kwargs.get("contact")

			#Validate booking fields
			try:
				booking.full_clean()
			except ValidationError as e:
				return False

			#Save booking
			booking.save()

			for cabin in _cabins:
				booking.cabins.add(cabin)

			booking.save()

			#Return id of the booking created
			return booking.id

	@classmethod
	def get_available_cabins(cls, _from_date, _to_date, _persons):
		#Get bookings that overlap with given dates and are active
		bookings = cls.get_bookings(_from_date, _to_date)

		available_cabins = Cabin.objects.all()
		#Remove cabins that are booked in this timeframe
		for booking in bookings:
			for cabin in booking.cabins.all():
				print(cabin)
				print(available_cabins.__str__())
				if cabins_match(cabin, available_cabins):
					print("MATCH")
					available_cabins = available_cabins.exclude(number=cabin.number)

		#Exclude cabins with not enough beds
		available_cabins = available_cabins.filter(persons__gte=_persons)

		return available_cabins

	@classmethod
	def get_bookings(cls, _from_date, _to_date):
		bookings = Booking.objects.all()
		dates_to_check = get_dates_between(_from_date, _to_date)

		for booking in bookings:
			booking_dates = get_dates_between(booking.from_date, booking.to_date)
			if not booking.is_active():
				bookings = bookings.exclude(id=booking.id)
				continue
			if not dates_overlap(dates_to_check, booking_dates):
				bookings = bookings.exclude(id=booking.id)



		return bookings

	


	def get_price(self):
		nights = len(get_dates_between(self.from_date, self.to_date))
		price = 0
		for cabin in self.cabins.all():
			price = price + (cabin.price * nights)
		return price

	def __str__(self):
		cabins ="["
		for c in self.cabins.all():
			cabins = cabins + c.number.__str__() + ","
		cabins = cabins[:-1]
		cabins = cabins + "]"
		res = cabins + " " + self.from_date.__str__() + " -> " + self.to_date.__str__() + " (" + self.created_date.__str__() + ")"
		return res


class TentativeBooking(Booking):

	def is_active(self):
		active_time = 10

		#Add active time if booking multiple cabins
		if self.cabins.count() >= 2:
			active_time = 20

		print("-----")
		print(self)
		
		if timezone.now() >= self.created_date + datetime.timedelta(minutes=active_time):
			print("FALSE")
			print(" ")
			return False
		print(" ")
		return True

	def __str__(self):
		return Booking.__str__(self) + " T"
	


class FinalBooking(Booking):

	active = models.BooleanField(default=True)
	contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True)

	charge_id = models.CharField(max_length=128, null=True, blank=True)

	def is_active(self):
		return self.active

	def __str__(self):
		return Booking.__str__(self) + " F"

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

def dates_overlap(_date1, _date2):
	#note date1 and date2 are arrays
	for d1 in _date1:
		for d2 in _date2:
			if d1 == d2:
				return True
	return False

def cabins_match(_cabin, _cabin_types):
	#check if cabin number is in cabin_types
	for c in _cabin_types:
		if c.number == _cabin.number:
			return True
	return False
