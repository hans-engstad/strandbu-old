from django.db import models, transaction
from django.core.exceptions import ValidationError
from django_countries.fields import CountryField
from django.utils import timezone
from polymorphic.models import PolymorphicModel
import datetime
import pytz
import polymorphic
import json


class AdminSettings(models.Model):
	min_from_date = models.IntegerField(default=1, help_text="Min days from today for from_date that customer can book cabin.")
	max_from_date = models.IntegerField(default=364, help_text="Max days from today for from_date that customer can book cabin.")
	
	max_to_date = models.IntegerField(default=365, help_text="Max days from today for to_date that customer can book cabin.")

	max_date_span = models.IntegerField(default=30, help_text="Max days for booking")

	booking_close_time = models.TimeField(help_text="Time booking will close if min_from_date is 0. (if customer can book today).", default="18:00:00")

	last_edit_date = models.DateTimeField(auto_now=True)


	@classmethod
	def booking_closed_time(cls, _from_date):

		now = timezone.localtime(timezone.now())

		#Open if from_date is after today
		if _from_date > now.date():
			return False

		if now.time() > AdminSettings.objects.first().booking_close_time:
			return True

		return False
		


	@classmethod
	def get_min_from_date(cls):
		return AdminSettings.objects.first().min_from_date


	@classmethod
	def reset_to_default(cls):

		print(AdminSettings.objects.all().__str__())

		#Delete all instances
		AdminSettings.objects.all().delete()

		print(AdminSettings.objects.all().__str__())
		#Create new instance
		settings = AdminSettings.objects.create()
		settings.save()
		print(AdminSettings.objects.all().__str__())

	def save(self, *args, **kwargs):
		if AdminSettings.objects.exists() and not self.pk:
			raise ValidationError('There can be only one AdminSettings object.')
		return super(AdminSettings, self).save(*args, **kwargs)

	def __str__(self):
		return 'Admin Settings: ' + self.last_edit_date.__str__()


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

	sort_presedence = models.IntegerField(default=-1)

	@property
	def price_kr(self):
		return int(self.price * 0.01)

	"""
	def is_available(self, _from_date, _to_date):
		with transaction.atomic():
			#will lock all bookings until the end of this transaction block
			all_bookings = Booking.objects.all().select_for_update()

			for booking in all_bookings:
				for cabin in booking.cabins.all():
					if cabin.number == self.number:
						return False
			return True
	"""

	def get_available_eq_cabins(self):
		for cabin in self.equivalent_cabins.all():
			if cabin.is_available():
				return cabin
		return False


	def __str__(self):
		return "[" + self.number.__str__() + "]"

	class Meta:
		ordering = ['sort_presedence']


class Contact(models.Model):
	name = models.CharField(max_length=255)
	email = models.CharField(max_length=255)
	phone = models.CharField(max_length=30)
	country = models.CharField(max_length=255)
	# late_arrival = models.BooleanField(default=False)



class Booking(PolymorphicModel):
	#booking_ptr = models.ForeignKey(Booking, db_column='base_ptr', null=True, on_delete=models.SET_NULL)

	from_date = models.DateField()
	to_date = models.DateField()
	cabins = models.ManyToManyField(Cabin)

	created_date = models.DateTimeField(auto_now=True)
	late_arrival = models.BooleanField(default=False)

	active = models.BooleanField(default=True)


	@classmethod
	def create_booking(cls, _from_date, _to_date, _cabins, _is_final, **kwargs):
		with transaction.atomic():
			#will lock all bookings until the end of this transaction block. 
			all_bookings = Booking.objects.all().select_for_update()

			booking_error = cls.get_create_booking_error(_from_date, _to_date, _cabins, all_bookings)
			if booking_error is not None:
				return False

			#Get all bookings with given dates and active
			bookings = Booking.get_bookings(_from_date, _to_date)

			#Create booking model
			booking = TentativeBooking()
			if _is_final:
				booking = FinalBooking()
			
			booking.active = True

			booking.from_date = _from_date
			booking.to_date = _to_date
			
			
			if 'contact' in kwargs:
				booking.contact = kwargs.get('contact')
				
			if 'charge_id' in kwargs:
				booking.charge_id = kwargs.get('charge_id')

			if 'late_arrival' in kwargs:
				booking.late_arrival = kwargs.get('late_arrival')

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
	def create_booking_from_tentative(cls, _t_booking, _contact, _charge_id):
		
		from_date = _t_booking.from_date
		to_date = _t_booking.to_date
		contact = _contact
		charge_id = _charge_id
		late_arrival = _t_booking.late_arrival

		cabin_ids = list(_t_booking.cabins.all().values_list('id', flat=True))
		cabins = Cabin.objects.filter(id__in=cabin_ids)

		_t_booking.delete()

		return Booking.create_booking(from_date, to_date, cabins, True, contact=contact, charge_id=charge_id, late_arrival=late_arrival)


	@classmethod
	def get_create_booking_error(cls, _from_date, _to_date, _cabins, _all_bookings, **kwargs):
		#Remove non-relevant bookings
		_all_bookings = cls.get_relevant_bookings(_from_date, _to_date, _all_bookings)

		if 't_booking' in kwargs:
			_all_bookings = _all_bookings.exclude(id=kwargs['t_booking'].id)

		#Check if cabins is available
		for booking in _all_bookings:
			for booking_cabin in booking.cabins.all():
				for cabin in _cabins:
					if cabin.number == booking_cabin.number:
						return "Hytte ikke lengre ledig. Vennligst prøv igjen."

		#Check booking dates
		if not TentativeBooking.booking_dates_get_error(_from_date, _to_date) == None:
			return TentativeBooking.booking_dates_get_error(_from_date, _to_date)

		if AdminSettings.objects.first().booking_closed_time(_from_date):
			return "Bestilling for i dag er stengt. Kontakt oss på (+47) 777 15 340 for bestilling."

		return None

	@classmethod
	def get_available_cabins(cls, _from_date, _to_date, **kwargs):
		#Get bookings that overlap with given dates and are active
		bookings = cls.get_bookings(_from_date, _to_date)

		available_cabins = Cabin.objects.all()
		#Remove cabins that are booked in this timeframe
		for booking in bookings:
			for cabin in booking.cabins.all():
				if cabins_match(cabin, available_cabins):
					available_cabins = available_cabins.exclude(number=cabin.number)

		#Add cabins from t_booking session (if any)
		if 't_booking' in kwargs:
			t_booking = kwargs.get('t_booking')
			if not t_booking == None:
				if t_booking.is_active():
					available_cabins = (available_cabins | t_booking.cabins.all()).distinct()

		return available_cabins

	@classmethod
	def get_bookings(cls, _from_date, _to_date):
		bookings = Booking.objects.all()
		return cls.get_relevant_bookings(_from_date, _to_date, bookings)

	@classmethod
	def get_final_bookings(cls, _from_date, _to_date):
		bookings = FinalBooking.objects.all()
		return cls.get_relevant_bookings(_from_date, _to_date, bookings)
		

	@classmethod
	def get_relevant_bookings(cls, _from_date, _to_date, _all_bookings):
		dates_to_check = get_dates_between(_from_date, _to_date)
		for booking in _all_bookings:
			booking_dates = get_dates_between(booking.from_date, booking.to_date)
			if not booking.is_active():
				_all_bookings = _all_bookings.exclude(id=booking.id)
				continue
			if not dates_overlap(dates_to_check, booking_dates):
				_all_bookings = _all_bookings.exclude(id=booking.id)
		return _all_bookings

	@classmethod
	def remove_similar_cabins(cls, _cabins):
		ids = []
		for cabin in _cabins.all():
			add_this = True
			for eq_cabin in cabin.equivalent_cabins.all():
				for cabin_id in ids:
					if Cabin.objects.get(id=cabin_id).number == eq_cabin.number:
						add_this = False
						break
			if add_this:
				ids.append(cabin.id)
		return Cabin.objects.filter(id__in=ids)

	@classmethod 
	def remove_cabins_from_set(cls, _all_cabins, _t_booking):
		#Removes the cabins in t_booking from the all_cabins set
		if _t_booking == None:
			return _all_cabins
		ids = []
		for cabin in _all_cabins:
			match = False
			for booking_cabin in _t_booking.cabins.all():
				if cabin.number == booking_cabin.number:
					match = True
					break;
			if match == False:
				ids.append(cabin.id)
		return Cabin.objects.filter(id__in=ids)


	def contains_cabin_number(self, number):
		for cabin in self.cabins.all():
			if cabin.number == number:
				return True
		return False

	def get_nights(self):
		return len(get_dates_between(self.from_date, self.to_date))

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
		res = cabins + " " + self.from_date.__str__() + " -> " + self.to_date.__str__()
		return res




class TentativeBooking(Booking):

	last_updated_time = models.DateTimeField(auto_now=True)

	@classmethod
	def booking_dates_are_valid(cls, _from_date, _to_date):
		if cls.booking_dates_get_error(_from_date, _to_date) == None:
			return True
		return False

	@classmethod
	def booking_dates_get_error(cls, _from_date, _to_date):
		#Check that checkin is after today + AdminSettings days
		now = timezone.localtime(timezone.now()).date()

		settings = AdminSettings.objects.first()

		min_checkin = now + datetime.timedelta(days=settings.min_from_date)
		max_checkin = now + datetime.timedelta(days=settings.max_from_date)

		#Check that from_date is after min_checkin
		if _from_date < min_checkin:
			days_text = "dager"
			if settings.min_from_date == 1:
				days_text = "dag"
			return "Innsjekk må være minst " + settings.min_from_date.__str__() + " " + days_text + " etter i dag. Vennligst kontakt oss på (+47) 777 15 340 for å bestille." 

		#Check that from_date is before max_checkin
		if _from_date > max_checkin:
			return "Innsjekk for langt frem i tid. Vennligst kontakt oss for bestilling."

		#Check that checkin is before checkout
		if _from_date >= _to_date:
			return "Innsjekk må være før utsjekk. Vennligst prøv igjen."

		#Check that booking is less than max_date span
		day_span = len(get_dates_between(_from_date, _to_date))
		if day_span > settings.max_date_span:
			return "Kan ikke lage bestilling på mer enn " + settings.max_date_span.__str__() + " dager. Vennligst ta kontakt for bestilling."
		return None


	def set_updated_time_now(self):
		self.last_updated_time = timezone.localtime(timezone.now())

	def is_active(self):
		if not self.active:
			return False
		idle_max_time = 10
		
		if timezone.localtime(timezone.now()) >= self.last_updated_time + datetime.timedelta(minutes=idle_max_time):
			return False
		return True

	def is_valid(self):
		if not self.is_active():
			return False

		booking_error = Booking.get_create_booking_error(self.from_date, self.to_date, self.cabins.all(), Booking.objects.all(), t_booking=self)

		print(booking_error)

		if booking_error is not None:
			return False

		#Check that checkin is before checkout
		if self.from_date >= self.to_date:
			return False

		return True

	def dates_are_valid(self):
		return TentativeBooking.booking_dates_are_valid(self.from_date, self.to_date)

			

	def create_active_copy(self):
		return Booking.create_booking(self.from_date, self.to_date, self.cabins.all(), False)

	def deactivate(self):
		self.active = False
		self.save()

	def __str__(self):
		return Booking.__str__(self) + " T" + " (" + self.id.__str__() + ")"
	


class FinalBooking(Booking):

	contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True)

	charge_id = models.CharField(max_length=128, null=True, blank=True)

	def is_active(self):
		return self.active

	def __str__(self):
		return Booking.__str__(self) + " F" + " (" + self.id.__str__() + ")"

#Helper methods

def get_dates_between(_from_date, _to_date):
	#check that _to_date is after _from_date
	if _to_date <= _from_date:
		return None

	if isinstance(_from_date, str):
		_from_date = datetime.datetime.strptime(_from_date, '%Y-%m-%d %H:%M:%S') 

	if isinstance(_to_date, str):
		_to_date = datetime.datetime.strptime(_to_date, '%Y-%m-%d %H:%M:%S')

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
			if d1.day == d2.day and d1.month == d2.month and d1.year == d2.year:
				return True
	return False

def cabins_match(_cabin, _cabin_types):
	#check if cabin number is in cabin_types
	for c in _cabin_types:
		if c.number == _cabin.number:
			return True
	return False
