from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.Home, name="home"),
    url(r'^booking/show$', views.ShowCabins, name="show_cabins"),
    url(r'^booking/contact$', views.ContactInfo, name="contact_info"),
    url(r'^booking/confirm$', views.ConfirmBooking, name="confirm_booking"),
]