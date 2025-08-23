from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.messages import get_messages


def send_pending_messages(request):
	msgs = get_messages(request)
	channel = f"session.messages.{request.session.session_key}"
	layer = get_channel_layer()
	for m in msgs:
		async_to_sync(layer.group_send)(
			channel,
			{
				"type": "message",
				"message": {
					"message": m.message,
					"level": m.level,
					"tags": m.tags,
				},
			},
		)
