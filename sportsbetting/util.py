import re
import datetime
import pytz
import pdb
import requests
from csv import DictReader, DictWriter
from smtplib import SMTPException

from django.shortcuts import render
from django.conf import settings
from django.contrib import messages
from django.contrib.admin import ModelAdmin
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest, HttpResponse, HttpResponseNotFound
from django.db import IntegrityError

from .models import Ticket, TicketPlay, Participant, Sport
	

def read_uploaded_ticket(request: HttpRequest, ticket: Ticket, end_date: datetime.date) -> None:
	if ticket._state.adding:
		messages.error(request, f"Error: read_uploaded_ticket() was passed an unsaved model instance")
		return
	
	try:
		with open(f'{settings.MEDIA_ROOT}/ticket.csv', mode='wb') as destination:
			for chunk in request.FILES.get('file').chunks():
				destination.write(chunk)
		
		with open(f'{settings.MEDIA_ROOT}/ticket.csv', mode='r') as source:
			last_greatest_date = None
			
			line = 1
			reader = DictReader(source)
			for row in reader:
				line += 1
				entry_sport = row.get('gametype') or row.get('sport')
				entry_first_team = row.get('first_team') or row.get('home_team') or row.get('unfavored')
				entry_spread = row.get('spread')
				entry_second_team = row.get('second_team') or row.get('away_team') or row.get('favored')
				entry_under = row.get('under')
				entry_over = row.get('over')
				entry_commence_time = row.get('datetime') or row.get('commence_time')
				
				if not entry_sport or not entry_first_team or not entry_second_team or not entry_commence_time:
					messages.error(request, f"Error: Missing values on line {line}")
					ticket.delete()
					return
				
				try:
					sport = Sport.objects.get(name=entry_sport)
				except ObjectDoesNotExist:
					messages.error(f"Error: Could not look up sport {entry_sport}; is it present in the database?")
					ticket.delete()
					return
				else:
					ticket.sports.add(sport)
				
				try:
					try:
						date_and_time = timezone.make_aware(datetime.datetime.fromisoformat(entry_commence_time))
					except ValueError:
						date_and_time = timezone.make_aware(datetime.datetime.strptime(entry_commence_time.replace('-', '/'), '%m/%d/%y %H:%M:%S'))
				except ValueError:
					messages.error(request, f"Error: Invalid commence_time on line {line} (got '{entry_commence_time}', but format should follow ISO format; example: '2011-11-04T00:05:23')")
					ticket.delete()
					return
				
				try:
					if not row.get('spread'):
						spread = None
					elif row.get('spread')[0].lower() == 'p':
						is_pick = True
						spread = int(row.get('spread')[1:])
					else:
						is_pick = False
						spread = int(row.get('spread'))
				except ValueError:
					messages.error(request, f"Error: Invalid spread on line {line} (got '{row.get('spread')}', but should be numeric integer only or numeric integer prefixed with 'P')")
					ticket.delete()
					return
				
				if isinstance(spread, int):
					spread_entry = ticket.spreads.create(
						sport = sport,
						first_team = entry_first_team,
						spread = spread,
						spreadIsPick = is_pick,
						second_team = entry_second_team,
						start_datetime = date_and_time,
						isPreview = False,
					)
				elif isinstance(spread, None):
					spread_entry = ticket.spreads.create(
						sport = sport,
						first_team = entry_first_team,
						second_team = entry_second_team,
						start_datetime = date_and_time,
						isPreview = True,
					)
				
				if spread_entry and (entry_under or entry_over):
					try:
						entry_under = int(entry_under)
						entry_over = int(entry_over)
						
						ticket.under_overs.create(
							linked_spread = spread_entry,
							under = entry_under,
							over = entry_over,
						)
					except ValueError:
						messages.error(request, f"Error: Invalid under/over values on line {line} of the spreadsheet")
						ticket.delete()
						return
			
				if not last_greatest_date or date_and_time.date() > last_greatest_date:
					last_greatest_date = date_and_time.date()
			
			if end_date:
				end_date = timezone.make_aware(end_date)
				if end_date < last_greatest_date:
					messages.warning(request, f"Warning: Games on ticket '{ticket.name}' conclude on '{last_greatest_date}', but the user specified end date is '{end_date}'")
			else:
				end_date = last_greatest_date
			
			if end_date >= ticket.pub_date:
				ticket.end_date = end_date
				ticket.save()
				messages.success(request, f"Success: Parsed spreadsheet and created ticket '{ticket.name}'")
				return
			else:
				messages.error(request, f"Error: All games for ticket '{ticket.name}' begin before the publish date, or the specified end date is earlier than the publish date")
				ticket.delete()
				return
	except IOError:
		messages.error(request, f"Error: Could not read ticket file on the server (are permissions configured properly on the server?)")
		ticket.delete()
		return


def parse_ticket(request: HttpRequest, ticket: Ticket, end_date: datetime.date) -> bool:
	try:
		with open(f'{settings.MEDIA_ROOT}/ticket.csv', mode='wb') as destination:
			for chunk in request.FILES.get('file').chunks():
				destination.write(chunk)
		
		with open(f'{settings.MEDIA_ROOT}/ticket.csv', mode='r') as source:
			last_greatest_date = None
			
			line = 1
			reader = DictReader(source)
			for row in reader:
				line += 1
				entry_sport = row.get('gametype') or row.get('sport')
				entry_first_team = row.get('first_team') or row.get('home_team') or row.get('unfavored')
				entry_spread = row.get('spread')
				entry_second_team = row.get('second_team') or row.get('away_team') or row.get('favored')
				entry_under = row.get('under')
				entry_over = row.get('over')
				entry_commence_time = row.get('datetime') or row.get('commence_time')
				
				if not entry_sport or not entry_first_team or not entry_second_team or not entry_commence_time:
					messages.error(request, f"Error: Missing values on line {line}")
					return False
				
				try:
					Sport.objects.get(name=entry_sport)
				except ObjectDoesNotExist:
					messages.error(f"Error: Could not look up sport {entry_sport}; is it present in the database?")
					return False
				
				try:
					try:
						date_and_time = timezone.make_aware(datetime.datetime.fromisoformat(entry_commence_time))
					except ValueError:
						date_and_time = timezone.make_aware(datetime.datetime.strptime(entry_commence_time, '%m/%d/%y %H:%M'))
				except ValueError:
					messages.error(request, f"Error: Invalid commence_time on line {line} (got '{entry_commence_time}', but format should follow ISO format; example: '2011-11-04T00:05:23')")
					return False
				
				try:
					if row.get('spread')[0].lower() == 'p':
						int(row.get('spread')[1:])
					else:
						int(row.get('spread'))
				except ValueError:
					messages.error(request, f"Error: Invalid spread on line {line} (got '{row.get('spread')}', but should be numeric integer only or numeric integer prefixed with 'P')")
					return False
				
				if entry_under or entry_over:
					try:
						int(entry_under)
						int(entry_over)
					except ValueError:
						messages.error(request, f"Error: Invalid under/over values on line {line} of the spreadsheet")
						return False
			
				if not last_greatest_date or date_and_time.date() > last_greatest_date:
					last_greatest_date = date_and_time.date()
			
			if not end_date:
				end_date = last_greatest_date
			else:
				end_date = timezone.make_aware(end_date)
			
			if end_date < ticket.pub_date:
				messages.error(request, f"Error: All games for ticket '{ticket.name}' begin before the publish date, or the specified end date is earlier than the publish date")
				return False
	except IOError:
		messages.error(request, f"Error: Could not read ticket file on the server (are permissions configured properly on the server?)")
		return False
	
	return True

"""
def read_uploaded_wins(f, my_ticket):
	with open(f'{settings.MEDIA_ROOT}/wins.csv', 'wb+') as destination:
		for chunk in f.chunks():
			destination.write(chunk)
	with open(f'{settings.MEDIA_ROOT}/wins.csv', 'r+') as source:
		reader = DictReader(source)
		for row in reader:
			entry_sport = row['gametype']
			entry_game = row['game']
			entry_winner = row['winner']
			entry_score = row['score']
			if entry_sport == None or entry_sport == '' or entry_game == None or entry_game == '':
				print(row)
				print("Warning: encountered spreedsheet entry with invalid values")
				continue
			
			spread = my_ticket.spreads.get(
				Q(gametype=entry_sport),
				Q(first_team=entry_game) | Q(second_team=entry_game)
			)
			if spread == None:
				print(f"Warning: could not find game matching entry {entry_game}")
				continue
			
			if entry_winner != None and entry_winner != '':
				spread.winner = entry_winner
				spread.save()
			
			if entry_score != None and entry_score != '':
				under_over = my_ticket.under_overs.get(linked_spread=spread)
				if under_over != None:
					if int(entry_score) < under_over.under:
						under_over.under_or_over = False
						under_over.save()
					elif int(entry_score) > under_over.over:
						under_over.under_or_over = True
						under_over.save()
				else:
					print(f"Warning: could not find under/over for game {entry_game}")
	
	plays = TicketPlay.objects.filter(ticket=my_ticket)
	for play in plays:
		if play.won == False:
			total = play.spread_picks.count() + play.under_over_picks.count()
			win_count = 0
			for pick in play.spread_picks:
				if pick.picked == pick.spread_entry.winner:
					win_count += 1
			for pick in play.under_over_picks:
				if pick.under_or_over == pick.under_over_entry.under_or_over:
					win_count += 1
			
			if win_count == total:
				play.won = True
				play.save()
				
				email_message  = f"Dear {play.purchaser_name},\n"
				email_message += "\nYou've placed a winning ticket and won! Here are your picks for reference.\n"
				for spread in play.spread_picks.all():
					email_message += f"\n{spread}"
				for under_over in play.under_over_picks.all():
					email_message += f"\n{under_over}"
				email_message += "\n\nWe will be in contact with you shortly to give you your payout.\n"
				email_message += "If you have any questions or concerns please call 1-888-664-2636.\n"
				email_message += f"\nSincerely,\n{settings.SITE_NAME}\n"
				
				try:
					send_mail(
						'You have won your bets!',
						email_message,
						settings.DEFAULT_FROM_EMAIL,
						[play.email],
						fail_silently=False,
					)
				except SMTPException:
					print(f"Warning: unable to send ticket win email to {play.email} (Play ID: {play.id})")
"""

def generate_ticket_page(modeladmin: ModelAdmin, request: HttpRequest) -> HttpResponse:
	params = {
		'apiKey': settings.SPORTS['SPORTS_API_KEY'],
		'all': 'false',
	}
	
	r = requests.get(url=settings.SPORTS['SPORTS_API_PROVIDER_URL'], params=params)
	data = r.json()
	
	sports = []
	for i in data:
		found = False
		for x in sports:
			if not found and type(x) is dict and x.get('type') == i.get('group'):
				found = True
				game = {}
				game['title'] = i.get('title')
				game['key'] = i.get('key')
				x.get('games').append(game)
		if not found:
			sports.append({
				'type': i.get('group'),
				'games': [
					{
						'title': i.get('title'),
						'key': i.get('key'),
					},
				],
			})
	
	context = {
		'title': "Generate Ticket",
		'opts': modeladmin.opts,
		'has_add_permission': modeladmin.has_add_permission(request),
		'has_change_permission': modeladmin.has_change_permission(request),
		'has_delete_permission': modeladmin.has_delete_permission(request),
		'has_view_permission': modeladmin.has_view_permission(request),
		'site_title': modeladmin.admin_site.site_title,
		'site_header': modeladmin.admin_site.site_header,
		'site_url': modeladmin.admin_site.site_url,
		'has_permission': modeladmin.admin_site.has_permission(request),
		'available_apps': modeladmin.admin_site.get_app_list(request),
		'is_popup': False,
		'is_nav_sidebar_enabled': True,
		'form_url': request.path,
		'sports': sports,
	}
	
	return render(request, 'admin/sportsbetting/ticket/generate_ticket.html', context)


def generate_ticket_spreadsheet(modeladmin: ModelAdmin, request: HttpRequest) -> HttpResponse:
	try:
		with open(f'{settings.MEDIA_ROOT}/generated.csv', mode='w') as f:
			#TODO: Thing this to a match/case switch upon upgrading to py 3.10
			if settings.SPORTS['PAIR_PROMINENCE'] == 'unfavored':
				fields = [ 'sport', 'unfavored', 'spread', 'favored', 'under', 'over', 'commence_time', 'api_id' ]
			elif settings.SPORTS['PAIR_PROMINENCE'] == 'favored':
				fields = [ 'sport', 'favored', 'spread', 'unfavored', 'under', 'over', 'commence_time', 'api_id' ]
			elif settings.SPORTS['PAIR_PROMINENCE'] == 'home_team':
				fields = [ 'sport', 'home_team', 'spread', 'away_team', 'under', 'over', 'commence_time', 'api_id' ]
			spreadsheet = DictWriter(f, fieldnames=fields)
			spreadsheet.writeheader()
			
			for sport in request.POST.keys():
				if sport == 'csrfmiddlewaretoken':
					continue
				
				# TODO: Find a way to make these configurable rather than hardcode them
				params = {
					'apiKey': settings.SPORTS['SPORTS_API_KEY'],
					'regions': 'us',
					'markets': 'spreads,totals',
					'oddsFormat': 'american',
				}
				
				if settings.SPORTS['UNIX_TIME']:
					params['dateFormat'] = 'unix'
				
				r = requests.get(url=settings.SPORTS['SPORTS_API_PROVIDER_URL']+f"/{request.POST.get(sport)}/odds", params=params)
				remaining = r.headers.get('X-Requests-Remaining')
				data = r.json()
				
				#TODO: Add more exceptions for cases where i might not contain a given key-value pair
				for i in data:
					spread = 0
					totals = 0
					
					#TODO: Make bookmaker selection configurable rather than first-success
					bookmakers = i.get('bookmakers')
					for bookmaker in bookmakers:
						if spread and totals:
							break
						else:
							for market in bookmaker.get('markets'):
								if market.get('key') == 'spreads':
									for outcome in market.get('outcomes'):
										if spread:
											break
										elif outcome.get('point') == None:
											continue
										elif outcome.get('name') == i.get('home_team'):
											if settings.SPORTS['ROUND_SPREADS']:
												spread = round(outcome.get('point'))
											else:
												spread = float(outcome.get('point'))
								elif market.get('key') == 'totals':
									for outcome in market.get('outcomes'):
										if totals:
											break
										elif outcome.get('point') == None:
											continue
										else:
											if settings.SPORTS['ROUND_TOTALS']:
												totals = round(outcome.get('point'))
											else:
												totals = float(outcome.get('point'))
					
					#TODO: Creation on failed lookups works for now, but really we need a predefined table of the data we're seeking
					sport = Sport.objects.get_or_create(name=i.get('sport_title'))[0]
					home_team = Participant.objects.get_or_create(type='TM', sport=sport, name=i.get('home_team').encode('ascii', 'ignore').decode())[0]
					away_team = Participant.objects.get_or_create(type='TM', sport=sport, name=i.get('away_team').encode('ascii', 'ignore').decode())[0]
					
					if settings.SPORTS['UNIX_TIME']:
						commence_time = datetime.datetime.fromtimestamp(i.get('commence_time'))
					else:
						commence_time = i.get('commence_time')[:-1]
					
					try:
						row = {
							'sport': i.get('sport_title'),
							'under': totals - settings.SPORTS['TOTALS_SPREAD'],
							'over': totals + settings.SPORTS['TOTALS_SPREAD'],
							'commence_time': commence_time,
							'api_id': i.get('id'),
						}
						
						if home_team.short:
							home_name = home_team.short
						else:
							home_name = home_team.name
						
						if away_team.short:
							away_name = away_team.short
						else:
							away_name = away_team.name
						
						if settings.SPORTS['PAIR_PROMINENCE'] == 'unfavored':
							if spread < 0:
								row['unfavored'] = home_name
								row['spread'] = spread
								row['favored'] = away_name
							else:
								row['unfavored'] = away_name
								row['spread'] = -1 * spread
								row['favored'] = home_name
						elif settings.SPORTS['PAIR_PROMINENCE'] == 'home_team':
							if spread > 0:
								row['home_team'] = home_name
								row['spread'] = spread
								row['away_team'] = away_name
							else:
								row['away_team'] = away_name
								row['spread'] = -1 * spread
								row['home_team'] = home_name
							
						spreadsheet.writerow(row)
					except ValueError:
						messages.warning(request, f"Some objects from the API provider's response couldn't be parsed (api_id: {i.get('id')})")
		
		with open(f'{settings.MEDIA_ROOT}/generated.csv', mode='r') as f: 
			response = HttpResponse(f.read(), headers={
				'Content-Type': 'text/csv',
				'Content-Disposition': 'attachment; filename="ticket.csv"',
			})
		
		messages.info(request, f"You have {remaining} sports data pulls left")
		
	except IOError:
		messages.error(request, f"Error: Could not read ticket file on the server (are permissions configured properly on the server?)")
		response = HttpResponseNotFound()

	return response
