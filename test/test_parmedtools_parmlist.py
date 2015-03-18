"""
Tests the ParmList class
"""
from chemistry.amber import AmberParm, ChamberParm, AmoebaParm
from chemistry.charmm import CharmmPsfFile
from ParmedTools import ParmList
import unittest
from utils import get_fn

class TestParmList(unittest.TestCase):

    def testAddAmberParm(self):
        """ Test adding AmberParm-derived instances to ParmList """
        parms = ParmList()
        amber = AmberParm(get_fn('tip4p.parm7'))
        chamber = ChamberParm(get_fn('ala_ala_ala.parm7'))
        amoeba = AmoebaParm(get_fn('nma.parm7'))
        parms.add_parm(amber)
        parms.add_parm(chamber)
        parms.add_parm(amoeba)
        self.assertEqual(len(parms), 3)
        # Test int indexing
        self.assertIs(parms[0], amber)
        self.assertIs(parms[1], chamber)
        self.assertIs(parms[2], amoeba)
        self.assertRaises(IndexError, lambda: parms[3])
        # Test name indexing
        self.assertIs(parms[get_fn('tip4p.parm7')], amber)
        self.assertIs(parms[get_fn('ala_ala_ala.parm7')], chamber)
        self.assertIs(parms[get_fn('nma.parm7')], amoeba)
        self.assertRaises(IndexError, lambda: parms['noparm'])
        # Check that the last added parm is active
        self.assertIs(parms.parm, amoeba)
        # Set a new active topology
        parms.set_new_active(0)
        self.assertIs(parms.parm, amber)
        parms.set_new_active(get_fn('ala_ala_ala.parm7'))
        self.assertIs(parms.parm, chamber)
        self.assertRaises(IndexError, lambda: parms.set_new_active(3))
        self.assertIs(parms.parm, chamber)

    def testAddAmberParmNames(self):
        """ Test adding Amber prmtop file names to ParmList """
        parms = ParmList()
        parms.add_parm(get_fn('tip4p.parm7'))
        parms.add_parm(get_fn('ala_ala_ala.parm7'))
        parms.add_parm(get_fn('nma.parm7'))
        amber, chamber, amoeba = parms
        self.assertEqual(len(parms), 3)
        # Check that they are the correct type
        self.assertIs(type(parms[0]), AmberParm)
        self.assertIs(type(parms[1]), ChamberParm)
        self.assertIs(type(parms[2]), AmoebaParm)
        self.assertRaises(IndexError, lambda: parms[3])
        # Test name indexing
        self.assertIs(parms[get_fn('tip4p.parm7')], amber)
        self.assertIs(parms[get_fn('ala_ala_ala.parm7')], chamber)
        self.assertIs(parms[get_fn('nma.parm7')], amoeba)
        self.assertRaises(IndexError, lambda: parms['noparm'])
        # Check that the last added parm is active
        self.assertIs(parms.parm, amoeba)
        # Set a new active topology
        parms.set_new_active(0)
        self.assertIs(parms.parm, amber)
        parms.set_new_active(get_fn('ala_ala_ala.parm7'))
        self.assertIs(parms.parm, chamber)
        self.assertRaises(IndexError, lambda: parms.set_new_active(3))
        self.assertIs(parms.parm, chamber)

    def testAddCharmmPsf(self):
        """ Test adding CHARMM PSF file to ParmList """
        parms = ParmList()
        ala3 = CharmmPsfFile(get_fn('ala3_solv.psf'))
        aaa = CharmmPsfFile(get_fn('ala_ala_ala.psf'))
        xaaa = CharmmPsfFile(get_fn('ala_ala_ala.psf.xplor'))
        aaaa = CharmmPsfFile(get_fn('ala_ala_ala_autopsf.psf'))
        parms.add_parm(ala3)
        parms.add_parm(aaa)
        parms.add_parm(xaaa)
        parms.add_parm(aaaa)
        # Check indexing
        self.assertIs(parms[0], ala3)
        self.assertIs(parms[1], aaa)
        self.assertIs(parms[2], xaaa)
        self.assertIs(parms[3], aaaa)
        # Test name indexing
        self.assertIs(parms[get_fn('ala3_solv.psf')], ala3)
        self.assertIs(parms[get_fn('ala_ala_ala.psf')], aaa)
        self.assertIs(parms[get_fn('ala_ala_ala.psf.xplor')], xaaa)
        self.assertIs(parms[get_fn('ala_ala_ala_autopsf.psf')], aaaa)
        # Check that the last parm added is active
        self.assertIs(parms.parm, parms[-1])
        # Set a new active topology
        parms.set_new_active(0)
        self.assertIs(parms.parm, ala3)
        parms.set_new_active(get_fn('ala_ala_ala.psf'))
        self.assertIs(parms.parm, aaa)


    def testAddCharmmPsfNames(self):
        """ Test adding CHARMM PSF file names to ParmList """
        parms = ParmList()
        parms.add_parm(get_fn('ala3_solv.psf'))
        parms.add_parm(get_fn('ala_ala_ala.psf'))
        parms.add_parm(get_fn('ala_ala_ala.psf.xplor'))
        parms.add_parm(get_fn('ala_ala_ala_autopsf.psf'))
        ala3, aaa, xaaa, aaaa = parms
        # Check proper instantiation
        for parm in parms:
            self.assertIsInstance(parm, CharmmPsfFile)
        # Check indexing
        self.assertIs(parms[0], ala3)
        self.assertIs(parms[1], aaa)
        self.assertIs(parms[2], xaaa)
        self.assertIs(parms[3], aaaa)
        # Test name indexing
        self.assertIs(parms[get_fn('ala3_solv.psf')], ala3)
        self.assertIs(parms[get_fn('ala_ala_ala.psf')], aaa)
        self.assertIs(parms[get_fn('ala_ala_ala.psf.xplor')], xaaa)
        self.assertIs(parms[get_fn('ala_ala_ala_autopsf.psf')], aaaa)
        # Check that the last parm added is active
        self.assertIs(parms.parm, parms[-1])
        # Set a new active topology
        parms.set_new_active(0)
        self.assertIs(parms.parm, ala3)
        parms.set_new_active(get_fn('ala_ala_ala.psf'))
        self.assertIs(parms.parm, aaa)
