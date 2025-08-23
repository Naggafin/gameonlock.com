import asyncio
import json

from channels.generic.http import AsyncHttpConsumer


class MessagesSSEConsumer(AsyncHttpConsumer):
	async def handle(self, body):
		await self.send_headers(
			headers=[
				(b"Cache-Control", b"no-cache"),
				(b"Content-Type", b"text/event-stream"),
				(b"Transfer-Encoding", b"chunked"),
				(b"Connection", b"keep-alive"),
			]
		)

		self.channel = f"session.messages.{self.scope['session'].session_key}"
		await self.channel_layer.group_add(self.channel, self.channel_name)

		try:
			while True:
				await asyncio.sleep(25)
				await self.send_body(b": keep-alive\n\n", more_body=True)
		except asyncio.CancelledError:
			pass
		finally:
			await self.channel_layer.group_discard(self.channel, self.channel_name)

	async def message(self, event):
		"""
		Handler for 'type': 'message' events.
		Called automatically by group_send.
		"""
		data = json.dumps(event["message"])
		await self.send_body(
			f"event: message\ndata: {data}\n\n".encode(),
			more_body=True,
		)
