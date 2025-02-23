import datetime
from smtplib import SMTPException

from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.db import IntegrityError
from django.shortcuts import redirect
from django.urls import path

from .models import (
	Participant,
	Sport,
	SpreadEntry,
	SpreadPick,
	Ticket,
	TicketPlay,
	UnderOverEntry,
	UnderOverPick,
)
from .util import (
	generate_ticket_page,
	generate_ticket_spreadsheet,
	parse_ticket,
	read_uploaded_ticket,
)

admin.site.register(Sport)


class UploadTicketForm(forms.Form):
	name = forms.CharField(
		label="Ticket name",
		max_length=255,
		initial=settings.SPORTS["default_ticket_name"],
	)
	date = forms.DateField(label="Publish date", initial=datetime.date.today())
	end_date = forms.DateField(
		label="End date",
		required=False,
		help_text="If left blank, an end date for the ticket will be calculated automatically",
	)
	file = forms.FileField()


class ChangeTicket(forms.Form):
	object_id = forms.CharField(widget=forms.HiddenInput)
	end_date = forms.DateField(
		label="End date",
		required=False,
		help_text="If left blank, an end date for the ticket will be calculated automatically",
	)
	file = forms.FileField()


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
	list_display = ("sport", "short", "name")
	list_filter = [
		"sport",
	]
	search_fields = ["name"]


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
	class SpreadEntryInline(admin.TabularInline):
		model = SpreadEntry

	class UnderOverEntryInline(admin.TabularInline):
		model = UnderOverEntry

	add_form_template = "admin/sportsbetting/ticket/admin_add_ticket_form.html"
	change_form_template = "admin/sportsbetting/ticket/admin_change_ticket_form.html"
	fields = ("name", "pub_date", "end_date")
	list_display = ("name", "pub_date", "end_date")
	list_filter = ["pub_date", "end_date"]
	search_fields = ["name"]
	inlines = [SpreadEntryInline, UnderOverEntryInline]

	def add_view(self, request, form_url="", extra_context=None):
		extra_context = extra_context or {}
		extra_context["form"] = UploadTicketForm()
		return super(TicketAdmin, self).add_view(request, form_url, extra_context)

	def change_view(self, request, object_id, form_url="", extra_context=None):
		extra_context = extra_context or {}
		old_ticket = Ticket.objects.get(pk=object_id)
		extra_context["form"] = ChangeTicket(
			initial={"object_id": object_id, "end_date": old_ticket.end_date}
		)
		return super(TicketAdmin, self).change_view(
			request, object_id, form_url, extra_context
		)

	def get_urls(self):
		urls = super().get_urls()
		my_urls = [
			path(
				"upload_ticket/",
				self.admin_site.admin_view(self.upload_ticket),
				name="upload_ticket",
			),
			path(
				"change_ticket/",
				self.admin_site.admin_view(self.change_ticket),
				name="change_ticket",
			),
			path(
				"generate_ticket/",
				self.admin_site.admin_view(self.generate_ticket),
				name="generate_ticket",
			),
		]
		return my_urls + urls

	def upload_ticket(self, request):
		if request.method == "POST":
			form = UploadTicketForm(request.POST, request.FILES)
			if form.is_valid():
				ticket = Ticket(
					name=form.cleaned_data.get("name"),
					pub_date=form.cleaned_data.get("date"),
				)

				try:
					ticket.save()
					read_uploaded_ticket(
						request, ticket, form.cleaned_data.get("end_date")
					)
				except IntegrityError:
					messages.error(
						request,
						f"Error: A ticket with a pub_date of {form.cleaned_data.get('date')} already exists, or invalid data was submitted",
					)

		return redirect("admin:index")  # TODO: Redirect to change lists page instead

	def change_ticket(self, request):
		if request.method == "POST":
			form = ChangeTicket(request.POST, request.FILES)
			if form.is_valid():
				try:
					old_ticket = Ticket.objects.get(
						pk=form.cleaned_data.get("object_id")
					)
				except ObjectDoesNotExist:
					messages.error(
						request,
						f"Error: It seems the given ticket does not exist (tried to look up by ID {form.get('object_id')})",
					)
				else:
					new_ticket = Ticket(
						name=old_ticket.name,
						pub_date=old_ticket.pub_date,
					)

					end_date = form.cleaned_data.get("end_date")

					if parse_ticket(request, new_ticket, end_date):
						try:
							old_ticket.delete()
							new_ticket.save()
						except IntegrityError:
							messages.error(
								request,
								f"Error: Unable to save clone of ticket {form.cleaned_data.get('object_id')}",
							)
						else:
							read_uploaded_ticket(request, new_ticket, end_date)

		return redirect("admin:index")  # TODO: Redirect to change lists page instead

	def generate_ticket(self, request):
		if request.method == "GET":
			return generate_ticket_page(self, request)
		elif request.method == "POST":
			return generate_ticket_spreadsheet(self, request)


@admin.register(TicketPlay)
class TicketPlayAdmin(admin.ModelAdmin):
	class SpreadPickInline(admin.TabularInline):
		model = SpreadPick

	class UnderOverPickInline(admin.TabularInline):
		model = UnderOverPick

	list_display = ("id", "purchaser_name", "email", "date", "paid", "won")
	list_filter = ["paid", "won"]
	inlines = [SpreadPickInline, UnderOverPickInline]
	actions = [
		"set_paid",
		"set_unpaid",
		"set_won",
		"unset_won",
	]

	# @admin.action(description='Set selected plays as paid')
	def set_paid(self, request, queryset):
		queryset.update(paid=True)

	# @admin.action(description='Set selected plays as unpaid')
	def set_unpaid(self, request, queryset):
		queryset.update(paid=False)

	# @admin.action(description='Set selected plays as won')
	def set_won(self, request, queryset):
		queryset.update(won=True)

		for play in queryset:
			email_message = f"Dear {play.purchaser_name},\n"
			email_message += "\nYou've placed a winning ticket and won! Here are your picks for reference.\n"
			for spread in play.spread_picks.all():
				email_message += f"\n{spread}"
			for under_over in play.under_over_picks.all():
				email_message += f"\n{under_over}"
			email_message += (
				"\n\nWe will be in contact with you shortly to give you your payout.\n"
			)
			email_message += (
				"If you have any questions or concerns please call 1-888-664-2636.\n"
			)
			email_message += f"\nSincerely,\n{settings.SITE_NAME}\n"

			try:
				send_mail(
					subject="You have won your bets!",
					message=email_message,
					from_email=settings.SALES_EMAIL,
					recipient_list=[
						play.email,
					],
					fail_silently=False,
					auth_user=settings.SALES_EMAIL_USER,
					auth_password=settings.SALES_EMAIL_PASSWORD,
				)
			except SMTPException:
				print(
					f"Warning: unable to send ticket win email to {play.email} (Play ID: {play.id})"
				)

	# @admin.action(description='Set selected plays as not won')
	def unset_won(self, request, queryset):
		queryset.update(won=False)
