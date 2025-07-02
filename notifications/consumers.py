import json

from channels.generic.http import AsyncHttpConsumer


class MessagesSSEConsumer(AsyncHttpConsumer):
	async def handle(self, body):
		user = self.scope.get("user")
		if not user.is_authenticated:
			await self.send_response(403, b"Forbidden")
			return

		await self.send_headers(
			headers=[
				(b"Cache-Control", b"no-cache"),
				(b"Content-Type", b"text/event-stream"),
				(b"Transfer-Encoding", b"chunked"),
			]
		)
		channel = f"user.messages.{user.id}"
		await self.channel_layer.group_add(channel, self.channel_name)

		try:
			while True:
				message = await self.receive_json_from_channel(channel)
				data = json.dumps(message)
				await self.send_body(
					f"event: message\ndata: {data}\n\n".encode(), more_body=True
				)
		finally:
			await self.channel_layer.group_discard(channel, self.channel_name)

	async def receive_json_from_channel(self, channel):
		event = await self.channel_layer.receive(channel)
		return event["message"]
