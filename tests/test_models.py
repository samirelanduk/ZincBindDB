from datetime import datetime
from mixer.backend.django import mixer
from django.core.exceptions import ValidationError
from unittest.mock import patch, Mock, MagicMock
from .base import ZincBindTest
from zincbind.models import Pdb, Residue, Atom, ZincSite

class PdbTests(ZincBindTest):

    def test_can_create_pdb(self):
        pdb = Pdb(
         pk="1XXY", title="The PDB Title", deposited="1990-09-28",
         resolution=4.5, organism="HOMO SAPIENS", expression="M MUS",
         classification="LYASE", technique="XRAY",
         rfactor=4.5, checked="2017-01-01"
        )
        self.assertEqual(pdb.zincsite_set.count(), 0)
        pdb.full_clean()


    def test_title_is_not_required(self):
        pdb = Pdb(
         pk="1XXY", deposited="1990-09-28",
         resolution=4.5, organism="HOMO SAPIENS", expression="M MUS",
         technique="XRAY",
         rfactor=4.5, checked="2017-01-01"
        )
        pdb.full_clean()


    def test_classification_is_not_required(self):
        pdb = Pdb(
         pk="1XXY", deposited="1990-09-28",
         resolution=4.5, organism="HOMO SAPIENS", expression="M MUS",
         technique="XRAY",
         rfactor=4.5, checked="2017-01-01"
        )
        pdb.full_clean()


    def test_date_is_not_required(self):
        pdb = Pdb(
         pk="1XXY", title="The PDB Title", deposited=None,
         resolution=4.5, organism="HOMO SAPIENS", expression="M MUS",
         classification="LYASE", technique="XRAY",
         rfactor=4.5, checked="2017-01-01"
        )
        pdb.full_clean()


    def test_resolution_is_not_required(self):
        pdb = Pdb(
         pk="1XXY", title="The PDB Title", deposited="1990-09-28",
         resolution=None, organism="HOMO SAPIENS", expression="M MUS",
         classification="LYASE", technique="XRAY",
         rfactor=4.5, checked="2017-01-01"
        )
        pdb.full_clean()


    def test_organism_is_not_required(self):
        pdb = Pdb(
         pk="1XXY", title="The PDB Title", deposited="1990-09-28",
         resolution=4.5, expression="M MUS",
         classification="LYASE", technique="XRAY",
         rfactor=4.5, checked="2017-01-01"
        )
        pdb.full_clean()


    def test_expression_is_not_required(self):
        pdb = Pdb(
         pk="1XXY", title="The PDB Title", deposited="1990-09-28",
         resolution=4.5, organism="HOMO SAPIENS",
         classification="LYASE", technique="XRAY",
         rfactor=4.5, checked="2017-01-01"
        )
        pdb.full_clean()


    def test_technique_is_not_required(self):
        pdb = Pdb(
         pk="1XXY", title="The PDB Title", deposited="1990-09-28",
         resolution=4.5, organism="HOMO SAPIENS",
         classification="LYASE", expression="M MUS",
         rfactor=4.5, checked="2017-01-01"
        )
        pdb.full_clean()


    def test_rfactor_is_not_required(self):
        pdb = Pdb(
         pk="1XXY", title="The PDB Title", deposited="1990-09-28",
         resolution=4.5, organism="HOMO SAPIENS",
         classification="LYASE", technique="XRAY", expression="M MUS",
         checked="2017-01-01"
        )
        pdb.full_clean()


    def test_checked_is_required(self):
        pdb = Pdb(
         pk="1XXY", title="The PDB Title", deposited="1990-09-28",
         resolution=4.5, organism="HOMO SAPIENS", expression="M MUS",
         classification="LYASE", technique="XRAY",
         rfactor=4.5, checked=None
        )
        with self.assertRaises(ValidationError):
            pdb.full_clean()



class ZincSiteTests(ZincBindTest):

    def setUp(self):
        ZincBindTest.setUp(self)
        self.pdb = mixer.blend(Pdb)


    def test_can_create_zinc_site(self):
        site = ZincSite(pk="1ZZZA500", x=1.5, y=-1.5, z=10.0, pdb=self.pdb)
        self.assertEqual(site.residue_set.count(), 0)
        site.full_clean()


    def test_x_is_required(self):
        site = ZincSite(pk="1ZZZA500", x=None, y=-1.5, z=10.0, pdb=self.pdb)
        with self.assertRaises(ValidationError):
            site.full_clean()
        site = ZincSite(pk="1ZZZA500", x=0, y=-1.5, z=10.0, pdb=self.pdb)
        site.full_clean()


    def test_y_is_required(self):
        site = ZincSite(pk="1ZZZA500", x=0, y=None, z=10.0, pdb=self.pdb)
        with self.assertRaises(ValidationError):
            site.full_clean()
        site = ZincSite(pk="1ZZZA500", x=1.5, y=0, z=10.0, pdb=self.pdb)
        site.full_clean()


    def test_z_is_required(self):
        site = ZincSite(pk="1ZZZA500", x=1.5, y=-1.5, z=None, pdb=self.pdb)
        with self.assertRaises(ValidationError):
            site.full_clean()
        site = ZincSite(pk="1ZZZA500", x=1.5, y=-1.5, z=0.0, pdb=self.pdb)
        site.full_clean()


    def test_pdb_is_required(self):
        site = ZincSite(pk="1ZZZA500", x=1.5, y=-1.5, z=None, pdb=None)
        with self.assertRaises(ValidationError):
            site.full_clean()


    def test_site_chain_property(self):
        site = ZincSite(pk="1ZZZA500", x=1.5, y=-1.5, z=10.0, pdb=self.pdb)
        self.assertEqual(site.chain, "A")


    def test_site_number_id_property(self):
        site = ZincSite(pk="1ZZZA500", x=1.5, y=-1.5, z=10.0, pdb=self.pdb)
        self.assertEqual(site.number_id, "500")



class ResidueTests(ZincBindTest):

    def setUp(self):
        ZincBindTest.setUp(self)
        self.site = mixer.blend(ZincSite)


    def test_can_create_residue(self):
        residue = Residue(
         pk="1XYZA10", residue_id="A10", name="VAL", chain="A", number=10,
         site=self.site
        )
        self.assertEqual(residue.atom_set.count(), 0)
        residue.full_clean()


    def test_residueid_is_required(self):
        residue = Residue(
         pk="1XYZA10", residue_id=None, name="VAL", chain="A", number=10,
         site=self.site
        )
        with self.assertRaises(ValidationError):
            residue.full_clean()
        residue = Residue(
         pk="1XYZA10", residue_id="", name="VAL", chain="A", number=10,
         site=self.site
        )
        with self.assertRaises(ValidationError):
            residue.full_clean()


    def test_name_is_required(self):
        residue = Residue(
         pk="1XYZA10", residue_id="A10", name=None, chain="A", number=10,
         site=self.site
        )
        with self.assertRaises(ValidationError):
            residue.full_clean()
        residue = Residue(
         pk="1XYZA10", residue_id="A10", name="", chain="A", number=10,
         site=self.site
        )
        with self.assertRaises(ValidationError):
            residue.full_clean()


    def test_chain_is_not_required(self):
        residue = Residue(
         pk="1XYZA10", residue_id="A10", name="VAL", chain=None, number=10,
         site=self.site
        )
        residue.full_clean()


    def test_number_is_required(self):
        residue = Residue(
         pk="1XYZA10", residue_id="A10", name="VAL", chain="A", number=None,
         site=self.site
        )
        with self.assertRaises(ValidationError):
            residue.full_clean()
        residue = Residue(
         pk="1XYZA10", residue_id="A10", name="VAL", chain="A", number=0,
         site=self.site
        )
        residue.full_clean()


    def test_site_is_required(self):
        residue = Residue(
         pk="1XYZA10", residue_id="A10", name="VAL", chain="A", number=10,
         site=None
        )
        with self.assertRaises(ValidationError):
            residue.full_clean()


    def test_residue_number_id_property(self):
        residue = Residue(
         pk="1XYZA10", residue_id="A10", name="VAL", chain="A", number=10,
         site=self.site
        )
        self.assertEqual(residue.number_id, "10")


    def test_residue_full_name_property(self):
        residue = Residue(
         pk="1XYZA10", residue_id="A10", name="VAL", chain="A", number=10,
         site=self.site
        )
        self.assertEqual(residue.full_name, "Valine")
        residue = Residue(
         pk="1XYZA10", residue_id="A10", name="HOH", chain="A", number=10,
         site=self.site
        )
        self.assertEqual(residue.full_name, "Water")
        residue = Residue(
         pk="1XYZA10", residue_id="A10", name="XXX", chain="A", number=10,
         site=self.site
        )
        self.assertEqual(residue.full_name, "XXX")



class AtomTests(ZincBindTest):

    def setUp(self):
        ZincBindTest.setUp(self)
        self.residue = mixer.blend(Residue)


    def test_can_create_atom(self):
        atom = Atom(
         pk="1XYZ555", atom_id=555, name="CA", x=1.5, y=-1.5, z=0.0,
         element="C", charge=-1, bfactor=13.4, alpha=True, beta=False,
         liganding=True, residue=self.residue
        )
        atom.full_clean()


    def test_atomid_is_required(self):
        atom = Atom(
         pk="1XYZ555", atom_id=None, name="CA", x=1.5, y=-1.5, z=0.0,
         element="C", charge=-1, bfactor=13.4, alpha=True, beta=False,
         liganding=True, residue=self.residue
        )
        with self.assertRaises(ValidationError):
            atom.full_clean()
        atom = Atom(
         pk="1XYZ555", atom_id=0, name="CA", x=1.5, y=-1.5, z=0.0,
         element="C", charge=-1, bfactor=13.4, alpha=True, beta=False,
         liganding=True, residue=self.residue
        )
        atom.full_clean()


    def test_name_is_required(self):
        atom = Atom(
         pk="1XYZ555", atom_id=555, name=None, x=1.5, y=-1.5, z=0.0,
         element="C", charge=-1, bfactor=13.4, alpha=True, beta=False,
         liganding=True, residue=self.residue
        )
        with self.assertRaises(ValidationError):
            atom.full_clean()
        atom = Atom(
         pk="1XYZ555", atom_id=555, name="", x=1.5, y=-1.5, z=0.0,
         element="C", charge=-1, bfactor=13.4, alpha=True, beta=False,
         liganding=True, residue=self.residue
        )
        with self.assertRaises(ValidationError):
            atom.full_clean()


    def test_x_is_required(self):
        atom = Atom(
         pk="1XYZ555", atom_id=555, name="CA", x=None, y=-1.5, z=0.0,
         element="C", charge=-1, bfactor=13.4, alpha=True, beta=False,
         liganding=True, residue=self.residue
        )
        with self.assertRaises(ValidationError):
            atom.full_clean()
        atom = Atom(
         pk="1XYZ555", atom_id=555, name="CA", x=0, y=-1.5, z=0.0,
         element="C", charge=-1, bfactor=13.4, alpha=True, beta=False,
         liganding=True, residue=self.residue
        )
        atom.full_clean()


    def test_y_is_required(self):
        atom = Atom(
         pk="1XYZ555", atom_id=555, name="CA", x=1.5, y=None, z=0.0,
         element="C", charge=-1, bfactor=13.4, alpha=True, beta=False,
         liganding=True, residue=self.residue
        )
        with self.assertRaises(ValidationError):
            atom.full_clean()
        atom = Atom(
         pk="1XYZ555", atom_id=555, name="CA", x=1.5, y=0, z=0.0,
         element="C", charge=-1, bfactor=13.4, alpha=True, beta=False,
         liganding=True, residue=self.residue
        )
        atom.full_clean()


    def test_z_is_required(self):
        atom = Atom(
         pk="1XYZ555", atom_id=555, name="CA", x=1.5, y=-1.5, z=None,
         element="C", charge=-1, bfactor=13.4, alpha=True, beta=False,
         liganding=True, residue=self.residue
        )
        with self.assertRaises(ValidationError):
            atom.full_clean()
        atom = Atom(
         pk="1XYZ555", atom_id=555, name="CA", x=1.5, y=-1.5, z=0,
         element="C", charge=-1, bfactor=13.4, alpha=True, beta=False,
         liganding=True, residue=self.residue
        )
        atom.full_clean()


    def test_element_is_required(self):
        atom = Atom(
         pk="1XYZ555", atom_id=555, name="CA", x=1.5, y=-1.5, z=0.0,
         element=None, charge=-1, bfactor=13.4, alpha=True, beta=False,
         liganding=True, residue=self.residue
        )
        with self.assertRaises(ValidationError):
            atom.full_clean()
        atom = Atom(
         pk="1XYZ555", atom_id=555, name="CA", x=1.5, y=-1.5, z=0.0,
         element="", charge=-1, bfactor=13.4, alpha=True, beta=False,
         liganding=True, residue=self.residue
        )
        with self.assertRaises(ValidationError):
            atom.full_clean()


    def test_charge_is_required(self):
        atom = Atom(
         pk="1XYZ555", atom_id=555, name="CA", x=1.5, y=-1.5, z=0.0,
         element="C", charge=None, bfactor=13.4, alpha=True, beta=False,
         liganding=True, residue=self.residue
        )
        with self.assertRaises(ValidationError):
            atom.full_clean()
        atom = Atom(
         pk="1XYZ555", atom_id=555, name="CA", x=1.5, y=-1.5, z=0.0,
         element="C", charge=0, bfactor=13.4, alpha=True, beta=False,
         liganding=True, residue=self.residue
        )
        atom.full_clean()


    def test_bfactor_is_required(self):
        atom = Atom(
         pk="1XYZ555", atom_id=555, name="CA", x=1.5, y=-1.5, z=0.0,
         element="C", charge=-1, bfactor=None, alpha=True, beta=False,
         liganding=True, residue=self.residue
        )
        with self.assertRaises(ValidationError):
            atom.full_clean()
        atom = Atom(
         pk="1XYZ555", atom_id=555, name="CA", x=1.5, y=-1.5, z=0.0,
         element="C", charge=-1, bfactor=0, alpha=True, beta=False,
         liganding=True, residue=self.residue
        )
        atom.full_clean()


    def test_alpha_is_required(self):
        atom = Atom(
         pk="1XYZ555", atom_id=555, name="CA", x=1.5, y=-1.5, z=0.0,
         element="C", charge=-1, bfactor=None, beta=False,
         liganding=True, residue=self.residue
        )
        with self.assertRaises(ValidationError):
            atom.full_clean()


    def test_beta_is_required(self):
        atom = Atom(
         pk="1XYZ555", atom_id=555, name="CA", x=1.5, y=-1.5, z=0.0,
         element="C", charge=-1, bfactor=None, alpha=False,
         liganding=True, residue=self.residue
        )
        with self.assertRaises(ValidationError):
            atom.full_clean()


    def test_liganding_is_required(self):
        atom = Atom(
         pk="1XYZ555", atom_id=555, name="CA", x=1.5, y=-1.5, z=0.0,
         element="C", charge=-1, bfactor=None, beta=False,
         alpha=True, residue=self.residue
        )
        with self.assertRaises(ValidationError):
            atom.full_clean()


    def test_residue_is_required(self):
        atom = Atom(
         pk="1XYZ555", atom_id=555, name="CA", x=1.5, y=-1.5, z=0.0,
         element="C", charge=-1, bfactor=13.4, alpha=True, beta=False,
         liganding=True, residue=None
        )
        with self.assertRaises(ValidationError):
            atom.full_clean()
