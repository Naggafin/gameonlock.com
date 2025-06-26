from django.views.generic import TemplateView
from paypal.standard.pdt.views import process_pdt


class PayPalReturnView(TemplateView):
	template_name = "golpayment/paypal_return.html"
	invalid_template_name = "golpayment/paypal_invalid.html"


def get(self, request, *args, **kwargs):
	pdt_obj, failed = process_pdt(request)
	context = {"failed": failed, "pdt_obj": pdt_obj}

	if (
		not failed
		and pdt_obj
		and getattr(pdt_obj, "receiver_email", None) == "receiver_email@example.com"
	):
		# Call Celery task for payment confirmation
		from golpayment.tasks import process_payment_confirmation

		process_payment_confirmation.delay(
			txn_id=pdt_obj.txn_id,
			amount=pdt_obj.mc_gross,
			user_email=request.user.email if request.user.is_authenticated else None,
		)
		return self.render_to_response(context)
	return self.response_class(
		request=request,
		template=self.invalid_template_name,
		context=context,
		using=self.template_engine,
	)


class PayPalCancelView(TemplateView):
	template_name = "golpayment/paypal_cancel.html"
