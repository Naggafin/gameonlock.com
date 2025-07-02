from django.urls import path

from . import views

app_name = "sportsbetting"
urlpatterns = [
	path("bet/", views.BettingView.as_view(), name="bet"),
	path("plays/create/", views.PlayCreateUpdateView.as_view(), name="play_create"),
	path(
		"plays/update/<int:id>/",
		views.PlayCreateUpdateView.as_view(),
		name="play_update",
	),
	# path("plays/delete/", views.PlayDeleteView.as_view(), name="play_delete"),
	# path("paypal/", include("paypal.standard.ipn.urls")),
	# path("payment_complete/", views.payment_complete, name="payment_complete"),
	# path("payment_cancelled/", views.payment_cancelled, name="payment_cancelled"),
]
