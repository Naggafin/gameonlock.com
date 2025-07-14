import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import re_path

from notifications.routing import http_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gameonlock.settings.production")

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
	{
		"http": AuthMiddlewareStack(
			URLRouter(
				[
					re_path(r"^sse/", URLRouter(http_urlpatterns)),
					re_path(r"", django_asgi_app),
				]
			)
		),
	}
)
