from django.contrib import admin
from main.models import Booking, Cabin, CabinImage

# Register your models here.
admin.site.register(Booking)
admin.site.register(Cabin)
admin.site.register(CabinImage)