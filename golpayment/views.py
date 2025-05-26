from django.views.decorators.http import require_GET
from django.shortcuts import render
from paypal.standard.pdt.views import process_pdt

@require_GET
def paypal_return(request):
    pdt_obj, failed = process_pdt(request)
    context = {"failed": failed, "pdt_obj": pdt_obj}
    if not failed and pdt_obj and getattr(pdt_obj, 'receiver_email', None) == "receiver_email@example.com":
        # TODO: Replace with actual receiver email and add more checks as needed
        return render(request, 'golpayment/paypal_return.html', context)
    return render(request, 'golpayment/paypal_invalid.html', context)

@require_GET
def paypal_cancel(request):
    # Optionally handle cancel logic here
    return render(request, 'golpayment/paypal_cancel.html')
