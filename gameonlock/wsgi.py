"""
WSGI config for gameonlock project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os
import sys

sys.path.append("/var/www/gameonlock.com/gameonlock")
sys.path.append("/var/www/gameonlock.com/venv/lib/python3.9/site-packages")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gameonlock.settings.production")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
