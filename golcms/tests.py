# Create your tests here.
from django.contrib.auth import get_user_model
from wagtail.models import Page
from wagtail.test.utils import WagtailPageTests


class WagtailHomePageTests(WagtailPageTests):
    def test_can_create_home_page(self):
        root = Page.get_first_root_node()
        # Use a unique slug to avoid conflicts
        unique_slug = "home-test"
        home = Page(title="Home", slug=unique_slug)
        root.add_child(instance=home)
        self.assertTrue(Page.objects.filter(slug=unique_slug).exists())

    def test_wagtail_permissions(self):
        User = get_user_model()
        user = User.objects.create_user(username="editor", password="testpass")
        # Assign wagtailadmin.access_admin permission
        from django.contrib.auth.models import Permission

        perm = Permission.objects.get(
            codename="access_admin", content_type__app_label="wagtailadmin"
        )
        user.user_permissions.add(perm)
        user.refresh_from_db()
        self.assertTrue(user.has_perm("wagtailadmin.access_admin"))
