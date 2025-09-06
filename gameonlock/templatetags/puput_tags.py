from django.db.models import Count, Q
from puput.models import Category
from puput.templatetags.puput_tags import *  # noqa: F403


@register.inclusion_tag("puput/tags/categories_list.html", takes_context=True)  # noqa: F405
def categories_list(context, categories_qs=None):
	blog_page = context["blog_page"]
	if categories_qs:
		categories = categories_qs.all()
	else:
		categories = Category.objects.with_uses(blog_page).filter(parent=None)
	context["categories"] = categories.annotate(
		post_count=Count(
			"categoryentrypage__page", filter=Q(blogpage__live=True), distinct=True
		)
	)
	return context
