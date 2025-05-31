from django.urls import path
from paypal.standard.ipn import views as ipn_views

from .views import PayPalCancelView, PayPalReturnView

urlpatterns = [
    path("paypal-ipn/", ipn_views.ipn, name="paypal-ipn"),
    path("paypal/return/", PayPalReturnView.as_view(), name="paypal-return"),
    path("paypal/cancel/", PayPalCancelView.as_view(), name="paypal-cancel"),
]
