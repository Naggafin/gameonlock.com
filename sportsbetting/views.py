import datetime
import pdb
from decimal import Decimal
from smtplib import SMTPException

from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, QuerySet
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from paypal.standard.forms import PayPalPaymentsForm

from .models import Ticket, TicketPlay, SpreadPick, UnderOverPick

# TODO:
# Implement a "success" page and notify user by email of purchase

def index(request):
	if request.method == 'POST':
		try:
			ticket = Ticket.objects.get(pk=request.POST.get('pk'), pub_date__lte=timezone.now().date(), end_date__gte=timezone.now().date())
		except ObjectDoesNotExist:
			ticket = None
			messages.error(request, "Error: The specified ticket does not exist")
		
		if ticket:
			try:
				amount = float(request.POST.get('bet_amount'))
				if amount < 5.0:
					raise ValueError
			except ValueError:
				amount = None
				messages.error(request, "Error: Invalid bet amount given")
			
			purchaser_name = request.POST.get('purchaser_name')
			if not purchaser_name:
				messages.error(request, "Error: Invalid name provided")
			
			email = request.POST.get('email')
			if not email:
				messages.error(request, "Error: Invalid email provided")
				
			if amount:
				try:
					play = TicketPlay(ticket=ticket, purchaser_name=purchaser_name, bet_amount=amount, email=email, phone=request.POST.get('phone'))
					play.save()
				except IntegrityError:
					play = None
					messages.error(request, "Error: Unable to save play instance")
				
				if play:
					for key in request.POST:
						try:
							for game in ticket.spreads.filter(isPreview=False):
								if key == f"{game.sport.name}_{game.first_team}_picked" and request.POST[key] == "True" and game.start_datetime >= timezone.now():
									play.spread_picks.create(picked=f"{game.first_team}", spread_entry=game)
									break
								elif key == f"{game.sport.name}_{game.second_team}_picked" and request.POST[key] == "True" and game.start_datetime >= timezone.now():
									play.spread_picks.create(picked=f"{game.second_team}", spread_entry=game)
									break
							for game in ticket.under_overs.filter(linked_spread__isPreview=False):
								if key == f"{game.linked_spread.sport.name}_{game.linked_spread.first_team}_under" and request.POST[key] == "True" and game.linked_spread.start_datetime >= timezone.now():
									play.under_over_picks.create(under_or_over=False, under_over_entry=game)
									break
								elif key == f"{game.linked_spread.sport.name}_{game.linked_spread.first_team}_over" and request.POST[key] == "True" and game.linked_spread.start_datetime >= timezone.now():
									play.under_over_picks.create(under_or_over=True, under_over_entry=game)
									break
						except IntegrityError:
								messages.error(request, "Error: You made the same pick twice, both choices on a wager were selected, or incorrect data was submitted")
								play.delete()
						
				if play:
					total_choices = ticket.spreads.count() + ticket.under_overs.count()
					if total_choices > 4:
						if (play.spread_picks.count() + play.under_over_picks.count()) < 4:
							messages.error(request, "Error: You must make at least 4 picks to play")
							play.delete()
					else:
						if (play.spread_picks.count() + play.under_over_picks.count()) < 1:
							messages.error(request, "Error: You must make at least one pick to play")
							play.delete()
		
				if play:
					request.session['play_pk'] = play.pk
					
					email_message  = f"Dear {play.purchaser_name},\n"
					email_message += f"\nThanks for placing your bet with {settings.SITE_NAME}! Here are your picks for reference.\n"
					for spread in play.spread_picks.all():
						email_message += f"\n{spread}"
					for under_over in play.under_over_picks.all():
						email_message += f"\n{under_over}"
					email_message += "\n\nIf you haven't already done so, make sure to pay the bet amount you specified, or your ticket won't be counted when the scores are tallied!\n"
					email_message += "If you have any questions or concerns, want to change your bets, or pay by a different method from PayPal, please call 1-888-664-2636.\n"
					email_message += f"\nSincerely,\n{settings.SITE_NAME}\n"
					
					try:
						send_mail(
							subject='Your bets have been placed!',
							message=email_message,
							from_email=settings.SALES_EMAIL,
							recipient_list=[request.POST.get('email'),],
							fail_silently=False,
							auth_user=settings.SALES_EMAIL_USER,
							auth_password=settings.SALES_EMAIL_PASSWORD,
						)
					except SMTPException as e:
						print(e)
					
					email_message = f"Play ID: {play.id}\n"
					email_message += f"Name: {play.purchaser_name}\n"
					email_message += f"Email: {play.email}\n"
					if play.phone:
						email_message += f"Phone: {play.phone}\n"
					email_message += f"Bet amt: {play.bet_amount}\n"
					email_message += f"Date: {play.date}\n"
					email_message += "Picks:\n"
					for spread in play.spread_picks.all():
						email_message += f"\t{spread}\n"
					for under_over in play.under_over_picks.all():
						email_message += f"\t{under_over}\n"
					
					try:
						send_mail(
							subject=f'New play submitted for {play.ticket.name}',
							message=email_message,
							from_email=settings.WEBADMIN_EMAIL,
							recipient_list=settings.NOTIFY_EMAILS,
							fail_silently=False,
							auth_user=settings.WEBADMIN_EMAIL_USER,
							auth_password=settings.WEBADMIN_EMAIL_PASSWORD,
						)
					except SMTPException as e:
						print(e)
					
					return redirect('sportsbetting:play')
	
	class GameSet:
		def __init__(self, date: datetime.date, games: QuerySet, ticket: Ticket):
			self.ticket = ticket.pk
			self.date = date
			self.games = games.order_by('start_datetime')
			self.time_heads = []
			self.day_heads = []
			
			for game in self.games:
				is_in = False
				for time_head in self.time_heads:
					if timezone.make_naive(game.start_datetime) == timezone.make_naive(time_head.start_datetime):
						is_in = True
						break
				
				if not is_in:
					self.time_heads.append(game)
				
				is_in = False
				for day_head in self.day_heads:
					if timezone.make_naive(game.start_datetime).date() == timezone.make_naive(day_head.start_datetime).date():
						is_in = True
						break
				
				if not is_in:
					self.day_heads.append(game)
		
	try:
		ticket = Ticket.objects.filter(pub_date__lte=datetime.date.today(), end_date__gte=datetime.date.today()).first()
		if not ticket:
			raise ObjectDoesNotExist
		
		sports = []
		for i in ticket.sports.all().order_by('name'):
			gamesets = []
			date = ticket.pub_date
			while date <= ticket.end_date:
				games = ticket.spreads.filter(start_datetime__date=date, start_datetime__gte=timezone.now(), sport=i)
				if games.exists():
					gamesets.append(GameSet(date, games, ticket))
				date += datetime.timedelta(days=1)
			
			if gamesets:
				sport = { 'name': i.name, 'gamesets': gamesets }
				sports.append(sport)
	except ObjectDoesNotExist:
		ticket = None
		sports = None
	
	context = {
		"ticket": ticket,
		"sports": sports,
	}
	
	return render(request, "sportsbetting/index.html", context)


def play(request):
	play_pk = request.session['play_pk']
	
	try:
		play = TicketPlay.objects.get(pk=play_pk)
	except ObjectDoesNotExist:
		return redirect('sportsbetting:index')
	
	paypal_dict = {
		"business": settings.PAYPAL_RECEIVER_EMAIL,
		"amount": play.bet_amount.quantize(Decimal('.01')),
		"currency_code": 'USD',
		"item_name": 'GOL Sports Ticket',
		"invoice": play_pk,
		"notify_url": request.build_absolute_uri(reverse('sportsbetting:paypal-ipn')),
		"return_url": request.build_absolute_uri(reverse('sportsbetting:payment_complete')),
		"cancel_return": request.build_absolute_uri(reverse('sportsbetting:payment_cancelled')),
		"lc": 'EN',
		"no_shipping": '1',
	}
	
	paypal_form = PayPalPaymentsForm(initial=paypal_dict)
	
	context = {
		"play": play,
		"paypal_form": paypal_form,
	}
	
	return render(request, "sportsbetting/ticket_order_page.html", context)

@csrf_exempt
def payment_complete(request):
	return render(request, "sportsbetting/payment_complete.html")

@csrf_exempt
def payment_cancelled(request):
	return render(request, "sportsbetting/payment_cancelled.html")