def pytest_configure():
	from django.conf import settings

	# Remove debug_toolbar from INSTALLED_APPS and MIDDLEWARE for all tests
	if "debug_toolbar" in settings.INSTALLED_APPS:
		settings.INSTALLED_APPS = [
			a for a in settings.INSTALLED_APPS if a != "debug_toolbar"
		]
	if (
		hasattr(settings, "MIDDLEWARE")
		and "debug_toolbar.middleware.DebugToolbarMiddleware" in settings.MIDDLEWARE
	):
		settings.MIDDLEWARE = [
			m
			for m in settings.MIDDLEWARE
			if m != "debug_toolbar.middleware.DebugToolbarMiddleware"
		]
