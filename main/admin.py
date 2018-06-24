from django.contrib import admin
from main.models import Booking, Cabin, CabinImage, CabinEquipment, ContactInfo, TentativeBooking

# Register your models here.
admin.site.register(Booking)
admin.site.register(Cabin)
admin.site.register(CabinImage)
admin.site.register(CabinEquipment)
admin.site.register(ContactInfo)

class TentativeBookingAdmin(admin.ModelAdmin):
	readonly_fields = ('created_date',)
admin.site.register(TentativeBooking, TentativeBookingAdmin)
