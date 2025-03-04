from django.urls import path

from . import views

app_name = "sportsbetting"
urlpatterns = [
	path("", views.BettingFormView.as_view(), name="betting"),
	# path("play/", views.play, name="play"),
	# path("paypal/", include("paypal.standard.ipn.urls")),
	# path("payment_complete/", views.payment_complete, name="payment_complete"),
	# path("payment_cancelled/", views.payment_cancelled, name="payment_cancelled"),
]
