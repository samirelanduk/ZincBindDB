from datetime import datetime
from unittest.mock import Mock, MagicMock, patch
from django.core.urlresolvers import resolve
from django.shortcuts import render
from django.contrib.auth.models import User
from django.test import TransactionTestCase, RequestFactory
from zincsites.models import *

class ZincDbTest(TransactionTestCase):

    def setUp(self):
        self.user = User.objects.create_user(
         username="testuser",
         password="testpassword"
        )
        self.client.login(username="testuser", password="testpassword")
        self.date = datetime(2010, 1, 1).date()



class UrlTest(ZincDbTest):

    def check_url_returns_view(self, url, view):
        resolver = resolve(url)
        self.assertEqual(resolver.func, view)



class ViewTest(ZincDbTest):

    def setUp(self):
        ZincDbTest.setUp(self)
        self.factory = RequestFactory()


    def get_user_request(self, path, method="get", data=None):
        request = self.factory.get(path)
        if method=="post":
            data = data if data else {}
            request = self.factory.post(path, data=data)
        request.user = self.user
        return request


    def check_view_uses_template(self, view, request, template, *args):
        render_patcher = patch("django.shortcuts.render")
        mock_render = render_patcher.start()
        try:
            response = view(request, *args)
            self.assertTrue(mock_render.called)
            self.assertEqual(mock_render.call_args_list[0][0][1], template)
        finally:
            render_patcher.stop()


    def check_view_redirects(self, view, request, url):
        response = view(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, url)


    def check_view_has_context(self, view, request, context, *args):
        render_patcher = patch("django.shortcuts.render")
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



class ModelTest(ZincDbTest):
    pass



class FactoryTest(ZincDbTest):

    def setUp(self):
        ZincDbTest.setUp(self)
        self.pdb = Mock()
        self.pdb.code.return_value = "1ABC"
        self.pdb.deposition_date.return_value = self.date
        self.pdb.title.return_value = "PDB TITLE."
        self.zinc = Mock()
        self.zinc.molecule_id.return_value = "B505"
        self.res1 = Mock()
        self.res2 = Mock()
        self.res1.residue_id.return_value = "B10"
        self.res1.name.return_value = "VAL"
        chain = Mock(name="chain")
        chain.chain_id.return_value = "C"
        residues_list = Mock(name="res_list")
        residues_list.index = MagicMock()
        residues_list.index.return_value = 20
        chain.residues = MagicMock()
        chain.residues.return_value = residues_list
        self.res1.chain = MagicMock()
        self.res1.chain.return_value = chain
        self.atom1, self.atom2 = Mock(), Mock()
        self.atom1.atom_id.return_value = 1
        self.atom1.x.return_value = 15
        self.atom1.y.return_value = 16
        self.atom1.z.return_value = 17
        self.atom1.element.return_value = "N"
        self.atom1.name.return_value = "N2"
        self.atom1.charge.return_value = -1
        self.atom1.bfactor.return_value = 101
        self.atom2.atom_id.return_value = 2
        self.atom2.x.return_value = 25
        self.atom2.y.return_value = 26
        self.atom2.z.return_value = 27
        self.atom2.element.return_value = "Z"
        self.atom2.name.return_value = "Z5"
        self.atom2.charge.return_value = -2
        self.atom2.bfactor.return_value = 202
        self.res1.atoms.return_value = set([self.atom1, self.atom2])
        self.pdb_record = Mock()
        self.pdb_record.id = "1ABC"
