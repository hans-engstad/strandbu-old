from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^intern$', views.InternalView, name="intern"),
    url(r'^intern/login$', views.LoginView, name="login"),
    url(r'^intern/logout$', views.LogoutView, name="logout"),
    url(r'^intern/booking$', views.InternalBooking, name="intern_booking"),

]