from unittest.mock import MagicMock, patch

from django.test import Client, TestCase
from django.urls import reverse


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
                "golpayment_status": "Completed",
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
                "golpayment_status": "Failed",
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
