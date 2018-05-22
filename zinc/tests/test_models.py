from datetime import date
from mixer.backend.django import mixer
from unittest.mock import patch, Mock, MagicMock
from testarsenal import DjangoTest
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.utils import IntegrityError
from zinc.models import *

class PdbTests(DjangoTest):

    def setUp(self):
        self.kwargs = {
         "id": "1XXY", "title": "The PDB Title", "deposited": date(1990, 9, 28),
         "resolution": 4.5, "organism": "HOMO SAPIENS", "expression": "M MUS",
         "classification": "LYASE", "technique": "XRAY", "skeleton": False,
         "rfactor": 4.5
        }


    def test_can_create_pdb(self):
        pdb = Pdb(**self.kwargs)
        pdb.full_clean(), pdb.save()


    def test_db_fields_required(self):
        for field in ["id", "title"]:
            kwargs = self.kwargs.copy()
            del kwargs[field]
            with self.assertRaises(ValidationError):
                Pdb(**kwargs).full_clean()


    def test_none_fields(self):
        for field in self.kwargs:
            if field not in ["id", "title"]:
                self.kwargs[field] = None
                pdb = Pdb(**self.kwargs)
                pdb.full_clean()


    @patch("zinc.utilities.model_is_skeleton")
    def test_can_create_from_atomium_pdb(self, mock_is):
        mock_is.return_value = True
        atomium_pdb = Mock(
         code="1AAA", title="T", classification="C", deposition_date=date(1, 1, 1),
         organism="O", expression_system="E", technique="T", rfactor=1, resolution=2
        )
        pdb = Pdb.create_from_atomium(atomium_pdb)
        self.assertEqual(pdb.id, atomium_pdb.code)
        self.assertEqual(pdb.title, atomium_pdb.title)
        self.assertEqual(pdb.deposited, atomium_pdb.deposition_date)
        self.assertEqual(pdb.resolution, atomium_pdb.resolution)
        self.assertEqual(pdb.organism, atomium_pdb.organism)
        self.assertEqual(pdb.expression, atomium_pdb.expression_system)
        self.assertEqual(pdb.classification, atomium_pdb.classification)
        self.assertEqual(pdb.technique, atomium_pdb.technique)
        self.assertEqual(pdb.skeleton, True)
        self.assertEqual(pdb.rfactor, atomium_pdb.rfactor)
        mock_is.assert_called_with(atomium_pdb.model)
        atomium_pdb.code = "2AAA"
        mock_is.return_value = False
        self.assertEqual(Pdb.create_from_atomium(atomium_pdb).skeleton, False)


    def test_can_search_pdbs_by_id(self):
        pdbs = [mixer.blend(Pdb, id=code) for code in ["1A23", "2B46", "3C72"]]
        self.assertEqual(list(Pdb.search("2B46")), [pdbs[1]])
        self.assertEqual(list(Pdb.search("1a23")), [pdbs[0]])


    def test_can_search_pdbs_by_title(self):
        pdbs = [mixer.blend(Pdb, title=d) for d in ["ABCD", "EFGH", "CDEF"]]
        self.assertEqual(list(Pdb.search("CD")), [pdbs[0], pdbs[2]])
        self.assertEqual(list(Pdb.search("fg")), [pdbs[1]])



class ZincSiteTests(DjangoTest):

    def setUp(self):
        self.pdb = mixer.blend(Pdb)
        self.kwargs = {
         "id": "1XXY457-458", "pdb": self.pdb
        }


    def test_can_create_zinc_site(self):
        site = ZincSite(**self.kwargs)
        site.full_clean(), site.save()


    def test_db_fields_required(self):
        for field in self.kwargs:
            kwargs = self.kwargs.copy()
            del kwargs[field]
            with self.assertRaises(ValidationError):
                ZincSite(**kwargs).full_clean()



class ChainTests(DjangoTest):

    def setUp(self):
        self.pdb = mixer.blend(Pdb)
        self.kwargs = {
         "id": "1XXYB", "sequence": "MLLYTCDDWATTY", "pdb": self.pdb,
         "chain_pdb_identifier": "A"
        }


    def test_can_create_chain(self):
        chain = Chain(**self.kwargs)
        chain.full_clean(), chain.save()


    def test_db_fields_required(self):
        for field in self.kwargs:
            kwargs = self.kwargs.copy()
            del kwargs[field]
            with self.assertRaises(ValidationError):
                Chain(**kwargs).full_clean()


    def test_can_create_from_atomium_chain(self):
        atomium_chain = Mock(id="B")
        residues = [Mock(code="T"), Mock(code="M"), Mock(code="V")]
        atomium_chain.residues.return_value = residues
        pdb = mixer.blend(Pdb, id="1AAA")
        chain = Chain.create_from_atomium(atomium_chain, pdb)
        self.assertEqual(chain.id, "1AAAB")
        self.assertEqual(chain.chain_pdb_identifier, "B")
        self.assertEqual(chain.sequence, "TMV")
        self.assertEqual(chain.pdb, pdb)


    def test_chain_sorting(self):
        chains = [Chain.objects.create(id=id, pdb=self.pdb, sequence="")
         for id in ["A001C", "A001A", "A001B", "A001D"]]
        self.assertEqual(
         list(Chain.objects.all()), [chains[1], chains[2], chains[0], chains[3]]
        )



class ResidueTests(DjangoTest):

    def setUp(self):
        self.site = mixer.blend(ZincSite)
        self.chain = mixer.blend(Chain)
        self.kwargs = {
         "id": "1XXYA25", "site": self.site, "chain": self.chain, "name": "VAL",
         "residue_pdb_identifier": 23, "insertion_pdb_identifier": "A"
        }


    def test_can_create_residue(self):
        res = Residue(**self.kwargs)
        res.full_clean(), res.save()


    def test_db_fields_required(self):
        for field in self.kwargs:
            if field not in ["site"]:
                kwargs = self.kwargs.copy()
                del kwargs[field]
                with self.assertRaises(ValidationError):
                    Residue(**kwargs).full_clean()


    def test_optional_db_fields(self):
        for field in self.kwargs:
            if field in ["site"]:
                self.kwargs[field] = None
                res = Residue(**self.kwargs)
                res.full_clean()


    @patch("zinc.models.Atom.create_from_atomium")
    def test_can_create_from_atomium_residue(self, mock_create):
        atomium_residue = Mock(id="A-10B")
        atomium_residue.name = "TYR"
        pdb = mixer.blend(Pdb, id="A100")
        site = mixer.blend(ZincSite, id="A10023-45", pdb=pdb)
        chain = mixer.blend(Chain, id="A100C", chain_pdb_identifier="A")
        atoms = [Mock(), Mock(), Mock()]
        atomium_residue.atoms.return_value = atoms
        res = Residue.create_from_atomium(atomium_residue, chain, site)
        self.assertEqual(res.id, "A10023-45A-10BTYR")
        self.assertEqual(res.residue_pdb_identifier, -10)
        self.assertEqual(res.insertion_pdb_identifier, "B")
        self.assertEqual(res.site, site)
        self.assertEqual(res.chain, chain)
        self.assertEqual(res.name, "TYR")
        for atom in atoms:
            mock_create.assert_any_call(atom, res)


    @patch("zinc.models.Atom.create_from_atomium")
    def test_can_create_from_atomium_residue_for_metal(self, mock_create):
        atomium_residue = Mock(id="A-10B")
        atomium_residue.name = "TYR"
        pdb = mixer.blend(Pdb, id="A100")
        chain = mixer.blend(Chain, id="A100C", chain_pdb_identifier="A")
        atoms = [Mock(), Mock(), Mock()]
        atomium_residue.atoms.return_value = atoms
        res = Residue.create_from_atomium(atomium_residue, chain)
        self.assertEqual(res.id, "A100CA-10BTYR")
        self.assertEqual(res.residue_pdb_identifier, -10)
        self.assertEqual(res.insertion_pdb_identifier, "B")
        self.assertEqual(res.site, None)
        self.assertEqual(res.chain, chain)
        self.assertEqual(res.name, "TYR")
        self.assertFalse(mock_create.called)


    def test_residue_sorting(self):
        for number in [8, 23, 4, 42, 16, 15]:
            self.kwargs["residue_pdb_identifier"] = number
            self.kwargs["id"] = str(number)
            Residue.objects.create(**self.kwargs)
        self.assertEqual(
         [r.residue_pdb_identifier for r in Residue.objects.all()],
         [4, 8, 15, 16, 23, 42]
        )



class AtomTests(DjangoTest):

    def setUp(self):
        self.res = mixer.blend(Residue)
        self.kwargs = {
         "id": "1XXY401", "atom_pdb_identifier": 401, "name": "CA",
         "x": 1.4, "y": -0.4, "z": 0.0, "element": "C", "charge": 0.1,
         "bfactor": 1.2, "residue": self.res, "liganding": True
        }


    def test_can_create_atom(self):
        atom = Atom(**self.kwargs)
        atom.full_clean(), atom.save()


    def test_db_fields_required(self):
        for field in self.kwargs:
            kwargs = self.kwargs.copy()
            del kwargs[field]
            if field == "liganding":
                with self.assertRaises(IntegrityError):
                    Atom(**kwargs).save()
            else:
                with self.assertRaises(ValidationError):
                    Atom(**kwargs).full_clean()


    def test_can_create_from_atomium_atom(self):
        atomium_atom = Mock(id=102, liganding=True)
        atomium_atom.x, atomium_atom.y, atomium_atom.z = 1.1, 2.2, 3.3
        atomium_atom.charge, atomium_atom.bfactor = 0.5, 1.4
        atomium_atom.element, atomium_atom.name = "P", "PW"
        residue = mixer.blend(Residue, id="A100B10")
        atom = Atom.create_from_atomium(atomium_atom, residue)
        self.assertEqual(atom.id, "A100B10102")
        self.assertEqual(atom.x, 1.1)
        self.assertEqual(atom.y, 2.2)
        self.assertEqual(atom.z, 3.3)
        self.assertEqual(atom.charge, 0.5)
        self.assertEqual(atom.bfactor, 1.4)
        self.assertEqual(atom.element, "P")
        self.assertEqual(atom.name, "PW")
        self.assertEqual(atom.atom_pdb_identifier, 102)
        self.assertEqual(atom.residue, residue)
        self.assertEqual(atom.liganding, True)



class MetalTests(DjangoTest):

    def setUp(self):
        self.res = mixer.blend(Residue)
        self.site = mixer.blend(ZincSite)
        self.pdb = mixer.blend(Pdb)
        self.chain = mixer.blend(Chain)
        self.kwargs = {
         "id": "1XXY401", "atom_pdb_identifier": 401, "name": "CA",
         "x": 1.4, "y": -0.4, "z": 0.0, "element": "C", "charge": 0.1,
         "bfactor": 1.2, "residue": self.res, "site": self.site, "pdb": self.pdb
        }


    def test_can_create_metal(self):
        metal = Metal(**self.kwargs)
        metal.full_clean(), metal.save()


    def test_db_fields_required(self):
        for field in self.kwargs:
            kwargs = self.kwargs.copy()
            del kwargs[field]
            with self.assertRaises(ValidationError):
                Metal(**kwargs).full_clean()


    @patch("zinc.models.Residue.create_from_atomium")
    def test_can_create_from_atomium_atom(self, mock_create):
        mock_create.return_value = self.res
        self.res.id = "A100B10"
        atomium_atom = Mock(id=102)
        atomium_atom.x, atomium_atom.y, atomium_atom.z = 1.1, 2.2, 3.3
        atomium_atom.charge, atomium_atom.bfactor = 0.5, 1.4
        atomium_atom.element, atomium_atom.name = "P", "PW"
        atom = Metal.create_from_atomium(atomium_atom, self.pdb, self.site, self.chain)
        self.assertEqual(atom.id, "A100B10102")
        self.assertEqual(atom.x, 1.1)
        self.assertEqual(atom.y, 2.2)
        self.assertEqual(atom.z, 3.3)
        self.assertEqual(atom.charge, 0.5)
        self.assertEqual(atom.bfactor, 1.4)
        self.assertEqual(atom.element, "P")
        self.assertEqual(atom.name, "PW")
        self.assertEqual(atom.atom_pdb_identifier, 102)
        self.assertEqual(atom.residue, self.res)
        self.assertEqual(atom.site, self.site)
        self.assertEqual(atom.pdb, self.pdb)
        mock_create.assert_called_with(atomium_atom.molecule, self.chain)
