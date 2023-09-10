"""gameonlock URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
\thttps://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
\t1. Add an import:  from my_app import views
\t2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
\t1. Add an import:  from other_app.views import Home
\t2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
\t1. Import the include() function: from django.urls import include, path
\t2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, re_path, include

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail.images.views.serve import ServeView
from wagtail.contrib.sitemaps.views import sitemap

from . import views

urlpatterns = [
	path('cs50/', views.cs50), # TODO: Delete later
	path('admin/', admin.site.urls),
	path('ticket/', include('sportsbetting.urls')),
	#path('shop/', include('ecommerce_app.urls')),
	path('cms/', include(wagtailadmin_urls)),
	path('documents/', include(wagtaildocs_urls)),
	path('robots.txt', views.robots),
	re_path(r'^images/([^/]*)/(\d*)/([^/]*)/[^/]*$', ServeView.as_view(), name='wagtailimages_serve'),
	re_path(r'^sitemap\.xml$', sitemap),
	re_path(r'', include(wagtail_urls)),
]

if settings.DEBUG:
	from django.conf.urls.static import static
	from django.contrib.staticfiles.urls import staticfiles_urlpatterns
	import debug_toolbar
	
	# Serve static and media files from development server
	urlpatterns += staticfiles_urlpatterns()
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
	urlpatterns = [
		path('__debug__/', include(debug_toolbar.urls)),
		path('404/', views.page_not_found, kwargs={'exception': Exception("Page not Found")}),
		path('500/', views.server_error),
	] + urlpatterns