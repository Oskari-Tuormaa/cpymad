# standard library
import unittest
import _compat

# tested class
from cern.cpymad.madx import Madx

class TestMadx(unittest.TestCase, _compat.TestCase):

    """Test methods for the Madx class."""

    def setUp(self):
        self.mad = Madx()
        self.doc = """
            ! constants
            QP_K1 = 2;

            ! elements
            qp: quadrupole, k1:=QP_K1, l=1;
            sb: sbend, l=2, angle=3.14/4;

            ! sequences
            s1: sequence, l=4, refer=center;
            qp, at=0.5;
            qp, at=1.5;
            sb, at=3;
            endsequence;

            s2: sequence, l=3, refer=entry;
            qp1: qp, at=0, k1=3;
            qp2: qp, at=1, l=2;
            endsequence;
        """
        for line in self.doc.splitlines():
            self.mad._libmadx.input(line)

    # TODO:
    # def test_command(self):
    # def test_help(self):
    # def test_call(self):

    def _check_twiss(self, seq_name):
        beam = 'beam, ex=1, ey=2, particle=electron, sequence={0};'.format(seq_name)
        self.mad.command(beam)
        twiss = self.mad.twiss(sequence=seq_name,
                               alfx=0.5, alfy=1.5,
                               betx=2.5, bety=3.5)
        betx, bety = twiss['betx'], twiss['bety']
        alfx, alfy = twiss['alfx'], twiss['alfy']
        self.assertAlmostEqual(alfx[0], 0.5)
        self.assertAlmostEqual(alfy[0], 1.5)
        self.assertAlmostEqual(betx[0], 2.5)
        self.assertAlmostEqual(bety[0], 3.5)
        self.assertAlmostEqual(twiss.summary['ex'], 1)
        self.assertAlmostEqual(twiss.summary['ey'], 2)

    def test_twiss_1(self):
        self._check_twiss('s1')     # s1 can be computed at start
        self._check_twiss('s1')     # s1 can be computed multiple times
        self._check_twiss('s2')     # s2 can be computed after s1

    def test_twiss_2(self):
        self._check_twiss('s2')     # s2 can be computed at start
        self._check_twiss('s1')     # s1 can be computed after s2

    # def test_survey(self):
    # def test_aperture(self):
    # def test_use(self):
    # def test_match(self):
    # def test_verbose(self):

    def test_active_sequence(self):
        self.mad.command('beam, ex=1, ey=2, particle=electron, sequence=s1;')
        self.mad.active_sequence = 's1'
        self.assertEqual(self.mad.active_sequence, 's1')

    def test_get_sequence(self):
        self.assertRaises(ValueError, self.mad.get_sequence, 'sN')
        s1 = self.mad.get_sequence('s1')
        self.assertEqual(s1.name, 's1')

    def test_get_sequences(self):
        seqs = self.mad.get_sequences()
        self.assertItemsEqual([seq.name for seq in seqs],
                              ['s1', 's2'])

    def test_get_sequence_names(self):
        self.assertItemsEqual(self.mad.get_sequence_names(),
                              ['s1', 's2'])

    def test_evaluate(self):
        val = self.mad.evaluate("1/QP_K1")
        self.assertAlmostEqual(val, 0.5)

    # def test_sequence_beam(self):
    # def test_sequence_twiss(self):
    # def test_sequence_twissname(self):

    def _get_elems(self, seq_name):
        elems = self.mad.get_sequence(seq_name).get_elements()
        elem_dict = dict((el['name'], el) for el in elems)
        elem_idx = dict((el['name'], i) for i, el in enumerate(elems))
        return elem_dict, elem_idx

    def test_sequence_get_elements_s1(self):
        s1, idx = self._get_elems('s1')
        qp1 = s1['qp:1']
        qp2 = s1['qp:2']
        sb1 = s1['sb:1']
        self.assertLess(idx['qp:1'], idx['qp:2'])
        self.assertLess(idx['qp:2'], idx['sb:1'])
        self.assertAlmostEqual(qp1['at'], 0)
        self.assertAlmostEqual(qp2['at'], 1)
        self.assertAlmostEqual(sb1['at'], 2)
        self.assertAlmostEqual(qp1['l'], 1)
        self.assertAlmostEqual(qp2['l'], 1)
        self.assertAlmostEqual(sb1['l'], 2)
        self.assertAlmostEqual(float(qp1['k1']), 2)
        self.assertAlmostEqual(float(qp2['k1']), 2)
        self.assertAlmostEqual(float(sb1['angle']), 3.14/4)
        self.assertEqual(str(qp1['k1']).lower(), "qp_k1")

    def test_sequence_get_elements_s2(self):
        s2, idx = self._get_elems('s2')
        qp1 = s2['qp1:1']
        qp2 = s2['qp2:1']
        self.assertLess(idx['qp1:1'], idx['qp2:1'])
        self.assertAlmostEqual(qp1['at'], 0)
        self.assertAlmostEqual(qp2['at'], 1)
        self.assertAlmostEqual(qp1['l'], 1)
        self.assertAlmostEqual(qp2['l'], 2)
        self.assertAlmostEqual(float(qp1['k1']), 3)
        self.assertAlmostEqual(float(qp2['k1']), 2)

    # def test_sequence_get_expanded_elements(self):

if __name__ == '__main__':
    unittest.main()
