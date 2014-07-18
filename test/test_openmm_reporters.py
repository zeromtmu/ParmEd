"""
This module tests the various reporters included in the chemistry package
"""

try:
    import simtk.openmm as mm
    from simtk.openmm import app
    import simtk.unit as u
    from chemistry.amber.openmmreporters import (NetCDFReporter, MdcrdReporter,
                    ProgressReporter, RestartReporter, AmberStateDataReporter,
                    EnergyMinimizerReporter)
    from chemistry.amber.openmmloader import OpenMMAmberParm as AmberParm
    has_openmm = True
except ImportError:
    from chemistry.amber.readparm import AmberParm
    has_openmm = False

from chemistry.amber import HAS_NETCDF
from chemistry.amber.asciicrd import AmberMdcrd, AmberAsciiRestart
from chemistry.amber.netcdffiles import NetCDFTraj, NetCDFRestart
import os
import utils
import unittest

get_fn = utils.get_fn

amber_gas = AmberParm(get_fn('ash.parm7'), get_fn('ash.rst7'))
amber_solv = AmberParm(get_fn('solv.prmtop'), get_fn('solv.rst7'))

class TestStateDataReporter(unittest.TestCase):

    def setUp(self):
        if not os.path.isdir(get_fn('writes')):
            os.makedirs(get_fn('writes'))

    def tearDown(self):
        for f in os.listdir(get_fn('writes')):
            os.unlink(get_fn(f, written=True))

    def testStateDataReporter(self):
        """ Test AmberStateDataReporter with various options """
        system = amber_gas.createSystem()
        integrator = mm.LangevinIntegrator(300*u.kelvin, 5.0/u.picoseconds,
                                           1.0*u.femtoseconds)
        sim = app.Simulation(amber_gas.topology, system, integrator)
        sim.context.setPositions(amber_gas.positions)
        f = open(get_fn('akma5.dat', written=True), 'w')
        sim.reporters.extend([
            AmberStateDataReporter(get_fn('akma1.dat', written=True), 10),
            AmberStateDataReporter(get_fn('akma2.dat', written=True), 10,
                                   time=False, potentialEnergy=False,
                                   kineticEnergy=False, totalEnergy=False,
                                   temperature=False),
            AmberStateDataReporter(get_fn('akma3.dat', written=True), 10,
                                   volume=True, density=True),
            AmberStateDataReporter(get_fn('akma4.dat', written=True), 10,
                                   separator='\t'),
            AmberStateDataReporter(get_fn('units.dat', written=True), 10,
                                   volume=True, density=True,
                                   energyUnit=u.kilojoules_per_mole,
                                   temperatureUnit=u.kelvin,
                                   volumeUnit=u.milliliters,
                                   densityUnit=u.kilograms/u.item/u.meter**3,
                                   timeUnit=u.femtoseconds),
            AmberStateDataReporter(f, 10)
        ])
        sim.step(500)
        f.close()

        # Now open all of the reporters and check that the information in there
        # is what we expect it to be
        akma1 = open(get_fn('akma1.dat', written=True), 'r')
        akma2 = open(get_fn('akma2.dat', written=True), 'r')
        akma3 = open(get_fn('akma3.dat', written=True), 'r')
        akma4 = open(get_fn('akma4.dat', written=True), 'r')
        akma5 = open(get_fn('akma5.dat', written=True), 'r')
        units = open(get_fn('units.dat', written=True), 'r')
        # AKMA 1 first
        header = akma1.readline().strip()[1:].split(',')
        self.assertEqual(len(header), 6)
        for i, label in enumerate(('Step', 'Time', 'Potential Energy',
                                   'Kinetic Energy', 'Total Energy',
                                   'Temperature')):
            self.assertTrue(label in header[i])
        for i, line in enumerate(akma1):
            words = line.replace('\n', '').split(',')
            self.assertEqual(i*10+10, int(words[0])) # step
        akma1.close()
        # AKMA 2
        header = akma2.readline().strip()[1:].split(',')
        self.assertEqual(len(header), 1)
        self.assertTrue('Step' in header[0])
        for i, line in enumerate(akma2):
            self.assertEqual(int(line.replace('\n', '').split(',')[0]), 10*i+10)
        akma2.close()
        # AKMA 3 -- save energies so we can compare to the file with different
        # units
        header = akma3.readline().strip()[1:].split(',')
        self.assertEqual(len(header), 8)
        for i, label in enumerate(('Step', 'Time', 'Potential Energy',
                                   'Kinetic Energy', 'Total Energy',
                                   'Temperature', 'Box Volume', 'Density')):
            self.assertTrue(label in header[i])
        akma_energies = [[0.0 for i in range(8)] for j in range(50)]
        for i, line in enumerate(akma3):
            words = line.replace('\n', '').split(',')
            akma_energies[i][0] = int(words[0])
            for j in range(1, 8):
                akma_energies[i][j] = float(words[j])
        akma3.close()
        # AKMA 4 -- tab delimiter
        header = akma4.readline().strip()[1:].split('\t')
        self.assertEqual(len(header), 6)
        for i, label in enumerate(('Step', 'Time', 'Potential Energy',
                                   'Kinetic Energy', 'Total Energy',
                                   'Temperature')):
            self.assertTrue(label in header[i])
        for i, line in enumerate(akma4):
            words = line.replace('\n', '').split('\t')
            self.assertEqual(i*10+10, int(words[0])) # step
        akma4.close()
        # AKMA 5 -- write to open file handle
        header = akma5.readline().strip()[1:].split(',')
        self.assertEqual(len(header), 6)
        for i, label in enumerate(('Step', 'Time', 'Potential Energy',
                                   'Kinetic Energy', 'Total Energy',
                                   'Temperature')):
            self.assertTrue(label in header[i])
        for i, line in enumerate(akma5):
            words = line.replace('\n', '').split(',')
            self.assertEqual(i*10+10, int(words[0])) # step
        akma5.close()
        # UNITS -- compare other units
        ene = u.kilojoule_per_mole.conversion_factor_to(u.kilocalorie_per_mole)
        time = u.femtoseconds.conversion_factor_to(u.picoseconds)
        volume = u.milliliters.conversion_factor_to(u.angstroms**3)
        density = 1/(u.grams/u.milliliter).conversion_factor_to(
                        u.kilograms/u.meter**3)
        conversions = [1, time, ene, ene, ene, 1, volume, density]
        headers = units.readline().strip()[1:].split(',')
        self.assertEqual(len(headers), 8)
        for i, line in enumerate(units):
            words = line.replace('\n', '').split(',')
            self.assertEqual(int(words[0]), akma_energies[i][0])
            for j in range(1, 8):
                self.assertAlmostEqual(float(words[j])*conversions[j],
                                       akma_energies[i][j],
                                       places=5)
        units.close()

    def testProgressReporter(self):
        """ Test ProgressReporter with various options """
        system = amber_gas.createSystem()
        integrator = mm.LangevinIntegrator(300*u.kelvin, 5.0/u.picoseconds,
                                           1.0*u.femtoseconds)
        sim = app.Simulation(amber_gas.topology, system, integrator)
        sim.context.setPositions(amber_gas.positions)
        sim.reporters.append(
            ProgressReporter(get_fn('progress_reporter.dat', written=True), 10,
                             500, step=True, time=True, potentialEnergy=True,
                             kineticEnergy=True, totalEnergy=True,
                             temperature=True, volume=True, density=True,
                             systemMass=None,
                             energyUnit=u.kilocalories_per_mole,
                             volumeUnit=u.angstroms**3)
        )
        sim.step(500)
        self.assertEqual(len(os.listdir(get_fn('writes'))), 1)
        text = open(get_fn('progress_reporter.dat', written=True), 'r').read()
        self.assertTrue('Estimated time to completion' in text)
        self.assertTrue('Total Energy' in text)
        self.assertTrue('Potential Energy' in text)
        self.assertTrue('Kinetic Energy' in text)
        self.assertTrue('Temperature' in text)

class TestTrajRestartReporter(unittest.TestCase):

    def setUp(self):
        if not os.path.isdir(get_fn('writes')):
            os.makedirs(get_fn('writes'))

    def tearDown(self):
        for f in os.listdir(get_fn('writes')):
            os.unlink(get_fn(f, written=True))

    def testReporters(self):
        """ Test NetCDF and ASCII restart and trajectory reporters (no PBC) """
        system = amber_gas.createSystem()
        integrator = mm.LangevinIntegrator(300*u.kelvin, 5.0/u.picoseconds,
                                           1.0*u.femtoseconds)
        sim = app.Simulation(amber_gas.topology, system, integrator)
        sim.context.setPositions(amber_gas.positions)
        sim.reporters.extend([
                NetCDFReporter(get_fn('traj1.nc', written=True), 10),
                NetCDFReporter(get_fn('traj2.nc', written=True), 10, vels=True),
                NetCDFReporter(get_fn('traj3.nc', written=True), 10, frcs=True),
                NetCDFReporter(get_fn('traj4.nc', written=True), 10, vels=True,
                               frcs=True),
                NetCDFReporter(get_fn('traj5.nc', written=True), 10, crds=False,
                               vels=True),
                NetCDFReporter(get_fn('traj6.nc', written=True), 10, crds=False,
                               frcs=True),
                NetCDFReporter(get_fn('traj7.nc', written=True), 10, crds=False,
                               vels=True, frcs=True),
                MdcrdReporter(get_fn('traj1.mdcrd', written=True), 10),
                MdcrdReporter(get_fn('traj2.mdcrd', written=True), 10,
                              crds=False, vels=True),
                MdcrdReporter(get_fn('traj3.mdcrd', written=True), 10,
                              crds=False, frcs=True),
                RestartReporter(get_fn('restart.ncrst', written=True), 10,
                                write_multiple=True, netcdf=True),
                RestartReporter(get_fn('restart.rst7', written=True), 10)
        ])
        sim.step(500)
        for reporter in sim.reporters: reporter.finalize()

        self.assertEqual(len(os.listdir(get_fn('writes'))), 61)
        ntraj = [NetCDFTraj.open_old(get_fn('traj1.nc', written=True)),
                 NetCDFTraj.open_old(get_fn('traj2.nc', written=True)),
                 NetCDFTraj.open_old(get_fn('traj3.nc', written=True)),
                 NetCDFTraj.open_old(get_fn('traj4.nc', written=True)),
                 NetCDFTraj.open_old(get_fn('traj5.nc', written=True)),
                 NetCDFTraj.open_old(get_fn('traj6.nc', written=True)),
                 NetCDFTraj.open_old(get_fn('traj7.nc', written=True))]
        atraj = [AmberMdcrd(get_fn('traj1.mdcrd', written=True),
                            amber_gas.ptr('natom'), hasbox=False, mode='r'),
                 AmberMdcrd(get_fn('traj2.mdcrd', written=True),
                            amber_gas.ptr('natom'), hasbox=False, mode='r'),
                 AmberMdcrd(get_fn('traj3.mdcrd', written=True),
                            amber_gas.ptr('natom'), hasbox=False, mode='r')]
        for traj in ntraj:
            self.assertEqual(traj.frame, 50)
            self.assertEqual(traj.Conventions, 'AMBER')
            self.assertEqual(traj.ConventionVersion, '1.0')
            self.assertEqual(traj.application, 'AmberTools')
            self.assertEqual(traj.program, 'ParmEd')
            self.assertFalse(traj.hasbox)
        self.assertTrue(ntraj[0].hascrds)
        self.assertFalse(ntraj[0].hasvels)
        self.assertFalse(ntraj[0].hasfrcs)
        self.assertTrue(ntraj[1].hascrds)
        self.assertTrue(ntraj[1].hasvels)
        self.assertFalse(ntraj[1].hasfrcs)
        self.assertTrue(ntraj[2].hascrds)
        self.assertFalse(ntraj[2].hasvels)
        self.assertTrue(ntraj[2].hasfrcs)
        self.assertTrue(ntraj[3].hascrds)
        self.assertTrue(ntraj[3].hasvels)
        self.assertTrue(ntraj[3].hasfrcs)
        self.assertFalse(ntraj[4].hascrds)
        self.assertTrue(ntraj[4].hasvels)
        self.assertFalse(ntraj[4].hasfrcs)
        self.assertFalse(ntraj[5].hascrds)
        self.assertFalse(ntraj[5].hasvels)
        self.assertTrue(ntraj[5].hasfrcs)
        self.assertFalse(ntraj[6].hascrds)
        self.assertTrue(ntraj[6].hasvels)
        self.assertTrue(ntraj[6].hasfrcs)
        for i in (0, 2, 3, 4, 5, 6): ntraj[i].close() # still need the 2nd
        for traj in atraj: traj.close()
        # Now test the NetCDF restart files
        fn = get_fn('restart.ncrst.%d', written=True)
        for i, j in enumerate(range(10, 501, 10)):
            ncrst = NetCDFRestart.open_old(fn % j)
            self.assertEqual(ncrst.coordinates.shape, (75,))
            self.assertEqual(ncrst.velocities.shape, (75,))
            flatcrdr = ncrst.coordinates
            flatvelr = ncrst.velocities
            flatcrdt = ntraj[1].coordinates(i)
            flatvelt = ntraj[1].velocities(i)
            for x1, x2 in zip(flatcrdr, flatcrdt):
                self.assertAlmostEqual(x1, x2, places=6)
            for v1, v2 in zip(flatvelr, flatvelt):
                # Lose a place of precision due to scaling/rescaling
                self.assertAlmostEqual(v1, v2, places=5)
        # Now test the ASCII restart file
        f = AmberAsciiRestart(get_fn('restart.rst7', written=True), 'r')
        # Compare to ncrst and make sure it's the same data
        for x1, x2 in zip(flatcrdr, f.coordinates):
            self.assertAlmostEqual(x1, x2, places=4) # limited ASCII precision
        for v1, v2 in zip(flatvelr, f.velocities):
            self.assertAlmostEqual(v1, v2, places=4) # limited ASCII precision

    def testReportersPBC(self):
        """ Test NetCDF and ASCII restart and trajectory reporters (w/ PBC) """
        system = amber_solv.createSystem(nonbondedMethod=app.PME,
                                         nonbondedCutoff=8*u.angstroms)
        integrator = mm.LangevinIntegrator(300*u.kelvin, 5.0/u.picoseconds,
                                           1.0*u.femtoseconds)
        sim = app.Simulation(amber_solv.topology, system, integrator)
        sim.context.setPositions(amber_solv.positions)
        sim.reporters.extend([
                NetCDFReporter(get_fn('traj.nc', written=True), 1,
                               vels=True, frcs=True),
                MdcrdReporter(get_fn('traj.mdcrd', written=True), 1),
                RestartReporter(get_fn('restart.ncrst', written=True), 1,
                                netcdf=True),
                RestartReporter(get_fn('restart.rst7', written=True), 1)
        ])
        sim.step(5)
        for reporter in sim.reporters: reporter.finalize()
        ntraj = NetCDFTraj.open_old(get_fn('traj.nc', written=True))
        atraj = AmberMdcrd(get_fn('traj.mdcrd', written=True),
                           amber_solv.ptr('natom'), True, mode='r')
        nrst = NetCDFRestart.open_old(get_fn('restart.ncrst', written=True))
        arst = AmberAsciiRestart(get_fn('restart.rst7', written=True), 'r')
        self.assertEqual(ntraj.frame, 5)
        self.assertEqual(atraj.frame, 5)
        self.assertTrue(ntraj.hasvels)
        self.assertTrue(ntraj.hasfrcs)
        for i in range(ntraj.frame):
            self.assertAlmostEqual
            for x1, x2 in zip(ntraj.box(i), atraj.box(i)):
                self.assertAlmostEqual(x1, x2, places=3)
        self.assertEqual(len(nrst.box), 6)
        self.assertEqual(len(arst.box), 6)

if not has_openmm:
    del TestStateDataReporter, TestTrajRestartReporter
elif not HAS_NETCDF:
    del TestTrajReporter.TestNetCDFReporter