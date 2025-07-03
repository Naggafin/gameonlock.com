from django.urls import re_path

from . import consumers

websocket_urlpatterns = []

http_urlpatterns = [
	re_path(r"^notifications/$", consumers.MessagesSSEConsumer.as_asgi()),
]
