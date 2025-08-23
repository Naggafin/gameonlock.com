from .utils import send_pending_messages


class SSEMessageMiddleware:
	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		response = self.get_response(request)
		send_pending_messages(request)
		return response
