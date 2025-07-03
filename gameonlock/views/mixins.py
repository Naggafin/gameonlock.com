from django.utils.translation import gettext_lazy as _
from view_breadcrumbs import BaseBreadcrumbMixin


class GameonlockMixin(BaseBreadcrumbMixin):
	home_label = '<i class="icon fa-solid fa-house"></i> %s' % _("Home")

	@property
	def crumbs(self):
		return []

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["title"] = self.title
		return context
