from django.urls import path
from paypal.standard.ipn import views as ipn_views
from . import views as golpayment_views

urlpatterns = [
    path('paypal-ipn/', ipn_views.ipn, name='paypal-ipn'),
    path('paypal-return/', golpayment_views.paypal_return, name='paypal-return'),
    path('paypal-cancel/', golpayment_views.paypal_cancel, name='paypal-cancel'),
]
