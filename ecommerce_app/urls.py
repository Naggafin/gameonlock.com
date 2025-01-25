from django.urls import include, path

from . import views

app_name = "ecommerce"
urlpatterns = [
	path("", views.index, name="index"),
	path(
		"product/<int:product_id>/<slug:product_slug>/",
		views.show_product,
		name="product_detail",
	),
	path("cart/", views.show_cart, name="show_cart"),
	path("checkout/", views.checkout, name="checkout"),
	path("paypal/", include("paypal.standard.ipn.urls")),
	path("payment_complete/", views.payment_complete, name="payment_complete"),
	path("payment_cancelled/", views.payment_cancelled, name="payment_cancelled"),
]
