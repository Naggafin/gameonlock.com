from unittest.mock import MagicMock, patch

from django.test import Client, TestCase
from django.urls import reverse
from django.core import mail
from django.conf import settings

from .forms import PayPalPaymentForm
from .tasks import process_payment_confirmation


class PayPalPaymentFlowTests(TestCase):
    def setUp(self):
        self.client = Client()

    @patch("paypal.standard.ipn.models.PayPalIPN")
    def test_paypal_ipn_success(self, mock_ipn):
        # Simulate a successful PayPal IPN post
        mock_ipn.return_value.verify.return_value = True
        response = self.client.post(
            reverse("paypal-ipn"),
            data={
                "payment_status": "Completed",
                "mc_gross": "10.00",
                "mc_currency": "USD",
                "txn_id": "12345",
                "receiver_email": "merchant@example.com",
            },
            content_type="application/x-www-form-urlencoded",
        )
        self.assertIn(response.status_code, [200, 302])

    @patch("paypal.standard.ipn.models.PayPalIPN")
    def test_paypal_ipn_invalid(self, mock_ipn):
        # Simulate an invalid PayPal IPN post
        mock_ipn.return_value.verify.return_value = False
        response = self.client.post(
            reverse("paypal-ipn"),
            data={
                "payment_status": "Failed",
                "mc_gross": "0.00",
                "mc_currency": "USD",
                "txn_id": "54321",
                "receiver_email": "merchant@example.com",
            },
            content_type="application/x-www-form-urlencoded",
        )
        self.assertIn(response.status_code, [200, 400, 302])

    def test_paypal_ipn_get_not_allowed(self):
        # GET should not be allowed on the IPN URL
        response = self.client.get(reverse("paypal-ipn"))
        self.assertEqual(response.status_code, 405)

    def test_paypal_return_url(self):
        response = self.client.get(reverse("paypal-return"))
        self.assertEqual(response.status_code, 200)

    def test_paypal_cancel_url(self):
        response = self.client.get(reverse("paypal-cancel"))
        self.assertEqual(response.status_code, 200)

    def test_paypal_return_url_not_found(self):
        # Test a non-existent return URL
        response = self.client.get("/payment/paypal/return/invalid/")
        self.assertIn(response.status_code, [404, 302])


class PayPalViewMethodTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_paypal_return_post_not_allowed(self):
        # POST should not be allowed on the return URL
        response = self.client.post(reverse("paypal-return"))
        self.assertEqual(response.status_code, 405)

    def test_paypal_cancel_post_not_allowed(self):
        # POST should not be allowed on the cancel URL
        response = self.client.post(reverse("paypal-cancel"))
        self.assertEqual(response.status_code, 405)


class PayPalReturnViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    @patch("golpayment.views.process_pdt")
    def test_paypal_return_success(self, mock_process_pdt):
        # Valid PDT and correct receiver email
        mock_pdt = MagicMock()
        mock_pdt.receiver_email = "receiver_email@example.com"
        mock_process_pdt.return_value = (mock_pdt, False)
        response = self.client.get(reverse("paypal-return"))
        self.assertTemplateUsed(response, "golpayment/paypal_return.html")
        self.assertFalse(response.context["failed"])
        self.assertEqual(
            response.context["pdt_obj"].receiver_email, "receiver_email@example.com"
        )

    @patch("golpayment.views.process_pdt")
    def test_paypal_return_invalid_receiver(self, mock_process_pdt):
        # Valid PDT but wrong receiver email
        mock_pdt = MagicMock()
        mock_pdt.receiver_email = "wrong@example.com"
        mock_process_pdt.return_value = (mock_pdt, False)
        response = self.client.get(reverse("paypal-return"))
        self.assertTemplateUsed(response, "golpayment/paypal_invalid.html")
        self.assertFalse(response.context["failed"])
        self.assertEqual(
            response.context["pdt_obj"].receiver_email, "wrong@example.com"
        )

    @patch("golpayment.views.process_pdt")
    def test_paypal_return_failed(self, mock_process_pdt):
        # PDT processing failed
        mock_pdt = MagicMock()
        mock_process_pdt.return_value = (mock_pdt, True)
        response = self.client.get(reverse("paypal-return"))
        self.assertTemplateUsed(response, "golpayment/paypal_invalid.html")
        self.assertTrue(response.context["failed"])

    @patch("golpayment.views.process_pdt")
    def test_paypal_return_no_pdt(self, mock_process_pdt):
        # PDT returned None
        mock_process_pdt.return_value = (None, False)
        response = self.client.get(reverse("paypal-return"))
        self.assertTemplateUsed(response, "golpayment/paypal_invalid.html")
        self.assertIsNone(response.context["pdt_obj"])


class PayPalPaymentFormTests(TestCase):
    def test_valid_form_data(self):
        form_data = {
            'amount': 10.00,
            'item_name': 'Test Play',
            'item_number': '123',
            'custom': 'user123'
        }
        form = PayPalPaymentForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_amount_negative(self):
        form_data = {
            'amount': -10.00,
            'item_name': 'Test Play',
            'item_number': '123',
            'custom': 'user123'
        }
        form = PayPalPaymentForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)

    def test_invalid_amount_zero(self):
        form_data = {
            'amount': 0.00,
            'item_name': 'Test Play',
            'item_number': '123',
            'custom': 'user123'
        }
        form = PayPalPaymentForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)

    def test_missing_required_fields(self):
        form_data = {
            'item_number': '123',
            'custom': 'user123'
        }
        form = PayPalPaymentForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)
        self.assertIn('item_name', form.errors)


class PayPalTasksTests(TestCase):
    def test_process_payment_confirmation_task(self):
        # Test the Celery task for payment confirmation
        txn_id = "TEST123"
        amount = 10.00
        user_email = "user@example.com"
        
        # Call the task
        result = process_payment_confirmation(txn_id, amount, user_email)
        
        # Check email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Payment Confirmation')
        self.assertIn(str(amount), mail.outbox[0].body)
        self.assertIn(txn_id, mail.outbox[0].body)
        self.assertEqual(mail.outbox[0].from_email, settings.DEFAULT_FROM_EMAIL)
        self.assertIn(user_email, mail.outbox[0].to)
        self.assertIn(settings.ADMIN_EMAIL, mail.outbox[0].to)
        
        # Check task return value
        self.assertEqual(result, f"Payment confirmation sent for transaction {txn_id}")
