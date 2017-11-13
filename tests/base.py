from datetime import datetime
from unittest.mock import patch
from django.test import TestCase, RequestFactory
from django.core.urlresolvers import resolve

class ZincBindTest(TestCase):

    def setUp(self):
        self.date = datetime.now().date()
        self.factory = RequestFactory()


    def check_url_returns_view(self, url, view):
        resolver = resolve(url)
        self.assertEqual(resolver.func, view)


    def get_request(self, path, method="get", data=None):
        data = data if data else {}
        if  method == "post":
            request = self.factory.post(path, data=data)
        request = self.factory.get(path, data=data)
        return request


    def check_view_uses_template(self, view, request, template, *args):
        render_patcher = patch("zincbind.views.render")
        mock_render = render_patcher.start()
        try:
            response = view(request, *args)
            self.assertTrue(mock_render.called)
            self.assertEqual(mock_render.call_args_list[0][0][1], template)
        finally:
            render_patcher.stop()


    def check_view_has_context(self, view, request, context, *args):
        render_patcher = patch("zincbind.views.render")
        mock_render = render_patcher.start()
        try:
            response = view(request, *args)
            self.assertTrue(mock_render.called)
            if len(mock_render.call_args_list[0][0]) <= 2:
                self.fail("No context sent")
            sent_context = mock_render.call_args_list[0][0][2]
            for key in context:
                self.assertEqual(sent_context[key], context[key])
        finally:
            render_patcher.stop()


    def check_view_redirects(self, view, request, url, *args):
        response = view(request, *args)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, url)
