from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter
from main.models import Booking, Cabin, CabinImage, CabinEquipment, Contact, TentativeBooking, FinalBooking

# Register your models here.
admin.site.register(Cabin)
admin.site.register(CabinImage)
admin.site.register(CabinEquipment)
admin.site.register(Contact)



class BookingChildAdmin(PolymorphicChildModelAdmin):
    """ Base admin class for all child models """
    base_model = Booking  # Optional, explicitly set here.
    readonly_fields = ('created_date',)


@admin.register(TentativeBooking)
class TentativeBookingAdmin(BookingChildAdmin):
    base_model = TentativeBooking  # Explicitly set here!
    # show_in_index = True  # makes child model admin visible in main admin site
    # define custom features here


@admin.register(FinalBooking)
class FinalBookingAdmin(BookingChildAdmin):
    base_model = FinalBooking  # Explicitly set here!
    # show_in_index = True  # makes child model admin visible in main admin site
    # define custom features here


@admin.register(Booking)
class BookingParentAdmin(PolymorphicParentModelAdmin):
    """ The parent model admin """
    base_model = Booking  # Optional, explicitly set here.
    child_models = (TentativeBooking, FinalBooking)
    list_filter = (PolymorphicChildModelFilter,)  # This is optional.







"""
class TentativeBookingAdmin(admin.ModelAdmin):
	readonly_fields = ('created_date',)
admin.site.register(TentativeBooking, TentativeBookingAdmin)

class FinalBookingAdmin(admin.ModelAdmin):
	readonly_fields = ('created_date',)
admin.site.register(FinalBooking, FinalBookingAdmin)"""
