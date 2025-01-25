from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.views.decorators.csrf import csrf_exempt
from paypal.standard.forms import PayPalPaymentsForm

from . import cart
from .forms import CartForm, CheckoutForm
from .models import LineItem, Order, Product

# Create your views here.


def index(request):
	all_products = Product.objects.all()
	return render(
		request,
		"ecommerce_app/index.html",
		{
			"all_products": all_products,
		},
	)


def show_product(request, product_id, product_slug):
	product = get_object_or_404(Product, id=product_id)

	if request.method == "POST":
		form = CartForm(request, request.POST)
		if form.is_valid():
			request.form_data = form.cleaned_data
			cart.add_item_to_cart(request)
			return redirect("show_cart")

	form = CartForm(request, initial={"product_id": product.id})
	return render(
		request,
		"ecommerce_app/product_detail.html",
		{
			"product": product,
			"form": form,
		},
	)


def show_cart(request):
	if request.method == "POST":
		if request.POST.get("submit") == "Update":
			cart.update_item(request)
		if request.POST.get("submit") == "Remove":
			cart.remove_item(request)

	cart_items = cart.get_all_cart_items(request)
	cart_subtotal = cart.subtotal(request)
	return render(
		request,
		"ecommerce_app/cart.html",
		{
			"cart_items": cart_items,
			"cart_subtotal": cart_subtotal,
		},
	)


def checkout(request):
	if request.method == "POST":
		form = CheckoutForm(request.POST)
		if form.is_valid():
			cleaned_data = form.cleaned_data
			o = Order(
				name=cleaned_data.get("name"),
				email=cleaned_data.get("email"),
				postal_code=cleaned_data.get("postal_code"),
				address=cleaned_data.get("address"),
			)
			o.save()

			all_items = cart.get_all_cart_items(request)
			for cart_item in all_items:
				li = LineItem(
					product_id=cart_item.product_id,
					price=cart_item.price,
					quantity=cart_item.quantity,
					order_id=o.id,
				)

				li.save()

			cart.clear(request)

			request.session["order_id"] = o.id

			paypal_dict = {
				"business": settings.PAYPAL_RECEIVER_EMAIL,
				"amount": play.bet_amount.quantize(Decimal(".01")),
				"currency_code": "USD",
				"item_name": "GOL Shop Order",
				"invoice": o.id,
				"notify_url": request.build_absolute_uri(
					reverse("ecommerce:paypal-ipn")
				),
				"return_url": request.build_absolute_uri(
					reverse("ecommerce:payment_complete")
				),
				"cancel_return": request.build_absolute_uri(
					reverse("ecommerce:payment_cancelled")
				),
				"lc": "EN",
			}

			paypal_form = PayPalPaymentsForm(initial=paypal_dict)

			messages.add_message(request, messages.INFO, "Order Placed!")
			return redirect("checkout")

	else:
		form = CheckoutForm()
		return render(request, "ecommerce_app/checkout.html", {"form": form})


@csrf_exempt
def payment_complete(request):
	return render(request, "ecommerce_app/payment_complete.html")


@csrf_exempt
def payment_cancelled(request):
	return render(request, "ecommerce_app/payment_cancelled.html")
