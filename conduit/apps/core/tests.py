from django.test import TestCase
from django.core.management import call_command
from django.core.management.base import SystemCheckError
from io import StringIO

from django.urls import URLPattern, URLResolver

from conduit import settings


def list_urls(lis, acc=None):
    if acc is None:
        acc = []
    if not lis:
        return
    l = lis[0]
    if isinstance(l, URLPattern):
        yield acc + [str(l.pattern)]
    elif isinstance(l, URLResolver):
        yield from list_urls(l.url_patterns, acc + [str(l.pattern)])
    yield from list_urls(lis[1:], acc)


class SystemHealthTests(TestCase):
    def test_system_check_errors(self):
        """
        Test that the system has no errors during startup checks.
        Particularly checking CORS configuration and other critical settings.
        """
        stdout = StringIO()
        stderr = StringIO()
        try:
            # Run system checks
            call_command('check', stdout=stdout, stderr=stderr)
        except SystemCheckError:
            self.fail(
                f"System checks failed!\nOutput: {stdout.getvalue()}\nErrors: {stderr.getvalue()}"
            )

    def test_all_urls(self):
        urlconf = __import__(settings.ROOT_URLCONF, {}, {}, [''])
        actual_urls = [''.join(p) for p in list_urls(urlconf.urlpatterns)]
        print(actual_urls)

        expected_urls = [
            'admin/',
            'admin/login/',
            'admin/logout/',
            'admin/password_change/',
            'admin/password_change/done/',
            'admin/autocomplete/',
            'admin/jsi18n/',
            'admin/r/<path:content_type_id>/<path:object_id>/',
            'admin/auth/group/',
            'admin/auth/group/add/',
            'admin/auth/group/<path:object_id>/history/',
            'admin/auth/group/<path:object_id>/delete/',
            'admin/auth/group/<path:object_id>/change/',
            'admin/auth/group/<path:object_id>/',
            'admin/^(?P<app_label>auth)/$',
            'admin/(?P<url>.*)$',
            'api/^articles$',
            'api/^articles\\.(?P<format>[a-z0-9]+)/?$',
            'api/^articles/(?P<slug>[^/.]+)$',
            'api/^articles/(?P<slug>[^/.]+)\\.(?P<format>[a-z0-9]+)/?$',
            'api/',
            'api/<drf_format_suffix:format>',
            'api/articles/feed',
            'api/articles/<slug:article_slug>/favorite',
            'api/articles/<slug:article_slug>/comments',
            'api/articles/<slug:article_slug>/comments/<int:comment_pk>',
            'api/tags',
            'api/user/',
            'api/users/',
            'api/users/login/',
            'api/profiles/<str:username>',
            'api/profiles/<str:username>/follow'
        ]

        # Optional: sort both lists for easier comparison
        self.assertEqual(sorted(actual_urls), sorted(expected_urls))
