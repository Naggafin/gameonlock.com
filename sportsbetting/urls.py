from django.urls import path

from . import views

app_name = "sportsbetting"
urlpatterns = [
	path("bet/", views.BettingView.as_view(), name="bet"),
	path("plays/", views.PlayListView.as_view(), name="play_list"),
	path("plays/create/", views.PlayCreateUpdateView.as_view(), name="play_create"),
	path(
		"plays/update/<int:id>/",
		views.PlayCreateUpdateView.as_view(),
		name="play_update",
	),
	# path("play/", views.play, name="play"),
	# path("paypal/", include("paypal.standard.ipn.urls")),
	# path("payment_complete/", views.payment_complete, name="payment_complete"),
	# path("payment_cancelled/", views.payment_cancelled, name="payment_cancelled"),
]
