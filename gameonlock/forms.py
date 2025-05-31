from allauth.account.forms import SignupForm as BaseSignupForm
from django import forms
from django.utils.translation import gettext_lazy as _
from localflavor.us.forms import USStateSelect
from phonenumber_field.formfields import PhoneNumberField


class SignupForm(BaseSignupForm):
    state = USStateSelect(label=_("State"))
    date_of_birth = forms.DateField(label=_("Date of Birth"))
    phone_number = PhoneNumberField(required=False, label=_("Phone Number"))
    alternate_email_address = forms.EmailField(
        required=False, label=_("Alternate Email Address")
    )

    def save(self, request):
        user = super().save(request)
        user.state = self.cleaned_data["state"]
        user.date_of_birth = self.cleaned_data["date_of_birth"]
        user.phone_number = self.cleaned_data["phone_number"]
        user.alternate_email_address = self.cleaned_data["alternate_email_address"]
        user.save()
        return user
