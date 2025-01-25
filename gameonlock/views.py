from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render


# TODO: Delete later
def cs50(request):
	response = HttpResponse("""<p>Yep! Even though the site is live, has a domain name, and looks superduper professional (right?!), it's still my project I'm submitting for the CS50 and CS50W courses, do not be fooled! I did create all the code content, and I do have control of this website, as shown by the response from this URL route. Thanks for the amazing courses, David, Brian, and the rest of the HarvardX CS50 team!
	<br>
	<br>
	Sincerely,<br>
	Nevin Coutu (naggafin)</p>""")

	return response


def sportsbook(request):
	return render(request, "gameonlock/sportsbook_login.html")


def robots(request):
	with open(settings.BASE_DIR + "/static/robots.txt", "r") as f:
		text_robots = f.read()
		return HttpResponse(text_robots, content_type="text/plain")


def page_not_found(request, **kwargs):
	pass


def server_error(request):
	pass
