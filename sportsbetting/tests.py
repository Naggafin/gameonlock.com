from django.test import TestCase, Client
from django.test.utils import setup_test_environment

from .models import *


setup_test_environment()

class SpprtsbettingModelTests(TestCase):
	def duplicate_ticket(self):
		pass
	
	def duplicate_spread(self):
		pass
	
	def duplicate_play_picks(self):
		pass
	

# Bets placed on past tickets
# Test paypal
# Test ticket upload
# Same-day ticket upload
# Blank spread
# Missing entries

