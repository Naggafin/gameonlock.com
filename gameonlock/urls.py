"""
URL configuration for airplane_site project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

import datetime

from allauth.account.decorators import secure_admin_login
from django.conf import settings
from django.conf.urls import handler400, handler403, handler404, handler500
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin

# urls.py
from django.urls import include, path
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from django.views.i18n import set_language
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

from . import views

admin.autodiscover()
admin.site.login = secure_admin_login(admin.site.login)

allauth_urls = [
	path(_("login/"), views.LoginView.as_view(), name="account_login"),
	path(_("signup/"), views.SignupView.as_view(), name="account_signup"),
]

internationalized_patterns = i18n_patterns(
	path(_("accounts/"), include((allauth_urls, "custom_allauth"))),
	path(_("accounts/"), include("allauth.urls")),
	# path(_('search/'), search_views.search, name='search'), # TODO: Implement Wagtail search capability
	path(_("pages/"), include(wagtail_urls)),
	path(_("sports/"), include("sportsbetting.urls")),
	# path(_("shop/"), include(apps.get_app_config("oscar").urls[0])),
	path(_("dashboard/"), views.DashboardView.as_view(), name="dashboard"),
	path(
		_("dashboard/bet-history/"),
		views.PlayHistoryView.as_view(),
		name="play_history",
	),
	path(
		_("dashboard/transaction-history/"),
		views.TransactionHistoryView.as_view(),
		name="transaction_history",
	),
	path(_("dashboard/settings/"), views.SettingsView.as_view(), name="settings"),
	path(
		_("terms/"),
		TemplateView.as_view(
			template_name="terms.html",
			extra_context={
				"title": _("Terms and Conditions"),
				"last_updated": datetime.date(year=2025, day=1, month=7),
			},
		),
		name="terms",
	),
	path(
		_("privacy/"),
		TemplateView.as_view(
			template_name="privacy.html",
			extra_context={
				"title": _("Privacy Policy"),
				"last_updated": datetime.date(year=2025, day=1, month=7),
			},
		),
		name="privacy",
	),
	path("", views.HomeView.as_view(), name="index"),
	prefix_default_language=False,
)

urlpatterns = [
	path("admin/", admin.site.urls),
	path("csp-report/", views.csp_report_view, name="csp_report"),
	path("i18n/set_language/", set_language, name="set_language"),
	path("cms/", include(wagtailadmin_urls)),
	path("documents/", include(wagtaildocs_urls)),
	path("payment/", include("golpayment.urls")),
] + internationalized_patterns


if "silk" in settings.INSTALLED_APPS:
	urlpatterns.append(path("silk/", include("silk.urls", namespace="silk")))

if settings.DEBUG:
	import debug_toolbar
	from django.conf.urls.static import static
	from django.contrib.staticfiles.urls import staticfiles_urlpatterns

	# Serve static and media files from development server
	urlpatterns += staticfiles_urlpatterns()
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
	urlpatterns = [
		path("__debug__/", include(debug_toolbar.urls)),
		path("400/", handler400, kwargs={"exception": Exception("Bad request")}),
		path("403/", handler403, kwargs={"exception": Exception("Forbidden")}),
		path("404/", handler404, kwargs={"exception": Exception("Page not found")}),
		path("500/", handler500, kwargs={"exception": Exception("Server error")}),
	] + urlpatterns
