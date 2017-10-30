from datetime import datetime, timedelta
from selenium import webdriver
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from zincbind.models import Pdb, Residue, ZincSite, Atom

class FunctionalTest(StaticLiveServerTestCase):

    def setUp(self):
        pdb_codes = [
         "{}AA{}".format(n, chr(c + 65)) for n in range(1, 3) for c in range(0, 4)
        ]
        for index, code in enumerate(pdb_codes):
            if index not in [1, 3, 6]:
                Pdb.objects.create(pk=code, checked=datetime.now())
            else:
                day = datetime(2012, 1, 1) + timedelta(days=index)
                Pdb.objects.create(
                 id=code, checked=datetime.now(),
                 title="PDB {}".format(index + 1), deposited=day,
                 resolution=5-(index / 10)
                )

        site1 = ZincSite.objects.create(id=pdb_codes[1] + "A100", x=1.5, y=2.5, z=2.5)
        for r in range(11, 14):
            residue = Residue.objects.create(
             id=pdb_codes[1] + "A" + str(r), residue_id="A" + str(r),
             name="VAL" if r % 2 else "CYS", number=r,
             pdb=Pdb.objects.get(pk=pdb_codes[1])
            )
            for a in range(1, 5):
                Atom.objects.create(
                 id=pdb_codes[1] + str(a + r * 10), x=a, y=a, z=a, charge=0, bfactor=1.5,
                 name=str(a), element="C", atom_id=a + r * 10, residue=residue,
                )
            site1.residues.add(residue)

        site2 = ZincSite.objects.create(id=pdb_codes[3] + "A200", x=6.5, y=8.5, z=9.5)
        for r in range(11, 14):
            residue = Residue.objects.create(
             id=pdb_codes[3] + "A" + str(r), residue_id="A" + str(r),
             name="VAL" if r % 2 else "CYS", number=r,
             pdb=Pdb.objects.get(pk=pdb_codes[3])
            )
            for a in range(1, 5):
                Atom.objects.create(
                 id=pdb_codes[3] + str(a + r * 10), x=a, y=a, z=a, charge=0, bfactor=1.5,
                 name=str(a), element="C", atom_id=a + r * 10, residue=residue,
                )
            site2.residues.add(residue)
        site3 = ZincSite.objects.create(id=pdb_codes[3] + "B200", x=16.5, y=18.5, z=19.5)
        for r in range(11, 14):
            residue = Residue.objects.create(
             id=pdb_codes[3] + "B" + str(r), residue_id="B" + str(r),
             name="VAL" if r % 2 else "CYS", number=r,
             pdb=Pdb.objects.get(pk=pdb_codes[3])
            )
            for a in range(1, 5):
                Atom.objects.create(
                 id=pdb_codes[3] + str(a + r * 100), x=a, y=a, z=a, charge=0, bfactor=1.5,
                 name=str(a), element="C", atom_id=a + r * 100, residue=residue,
                )
            site2.residues.add(residue)

        site4 = ZincSite.objects.create(id=pdb_codes[3] + "E500", x=-6.5, y=-8.5, z=-1.5)
        for r in range(11, 14):
            residue = Residue.objects.create(
             id=pdb_codes[6] + "E" + str(r), residue_id="E" + str(r),
             name="VAL" if r % 2 else "CYS", number=r,
             pdb=Pdb.objects.get(pk=pdb_codes[3])
            )
            for a in range(1, 5):
                Atom.objects.create(
                 id=pdb_codes[6] + str(a + r * 100), x=a, y=a, z=a, charge=0, bfactor=1.5,
                 name=str(a), element="C", atom_id=a + r * 100, residue=residue,
                )
            site2.residues.add(residue)



        '''for index, code in enumerate(pdb_codes):
            if index > 23:
                Pdb.objects.create(pk=code, checked=datetime.now())
            else:
                day = datetime(2012, 1, 1) + timedelta(days=index)
                Pdb.objects.create(
                 pk=code, checked=datetime.now(),
                 title="PDB {}".format(index + 1), deposited=day,
                 resolution=5-(index / 10)
                )
        for index, pdb in enumerate(Pdb.objects.exclude(title=None)):
            site = ZincSite.objects.create(
             pk=pdb.id + "A{}0".format((index + 1) * 10),
             x = index, y=-index, z=100-index
            )
            residue1 = Residue.objects.create(
             pk=pdbid + "A" + index + 10, residue_id="A" + index + 10,
             name="VAL" if index % 2 else "CYS"
            )'''
