from django.contrib import admin
from paypal.standard.models import PayPalIPN

# Register PayPal IPN model for admin visibility
admin.site.register(PayPalIPN)
