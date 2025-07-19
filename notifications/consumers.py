import asyncio
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
				(b"Connection", b"keep-alive"),
			]
		)

		channel = f"user.messages.{user.id}"
		await self.channel_layer.group_add(channel, self.channel_name)

		try:
			while True:
				# Wait for either a message or a timeout for heartbeat
				try:
					message = await asyncio.wait_for(
						self.channel_layer.receive(channel),
						timeout=25,  # Timeout for sending heartbeat
					)
					data = json.dumps(message["message"])
					await self.send_body(
						f"event: message\ndata: {data}\n\n".encode(), more_body=True
					)
				except asyncio.TimeoutError:
					# Heartbeat comment (ignored by browser, keeps connection open)
					await self.send_body(b": keep-alive\n\n", more_body=True)
				except asyncio.CancelledError:
					break
		finally:
			await self.channel_layer.group_discard(channel, self.channel_name)

	async def receive_json_from_channel(self, channel):
		event = await self.channel_layer.receive(channel)
		return event["message"]
