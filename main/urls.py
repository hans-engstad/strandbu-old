from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.Home, name="home"),
    url(r'^booking/show$', views.ShowCabins, name="show_cabins"),
    url(r'^booking/overview$', views.BookingOverview, name="booking_overview"),
    url(r'^booking/charge$', views.ChargeBooking, name="charge_booking"),
]