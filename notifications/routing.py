from django.urls import path

from . import consumers

websocket_urlpatterns = []

http_urlpatterns = [
	path("sse/messages/", consumers.MessagesSSEConsumer.as_asgi()),
]
