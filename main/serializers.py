from rest_framework import serializers
from main.models import TentativeBooking, Cabin



class CabinSerializer(serializers.ModelSerializer):
	class Meta:
		model = Cabin
		fields = '__all__'

class TentativeBookingSerializer(serializers.ModelSerializer):
	# cabins = CabinSerializer(many=True)
	class Meta:
		model = TentativeBooking
		fields = ('id', 'from_date', 'to_date', 'cabins', 'created_date')