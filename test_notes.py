import unittest
import itertools as it
from notes import Note, Chord, Finger, Hand


class TestNotes(unittest.TestCase):
    def setUp(self):
        self.e1 = Note(-8)
        self.e2 = Note('E3')

    def test_names(self):
        self.assertEqual(self.e1.name, 'E3')
        self.assertEqual(self.e2.name, 'E3')

    def test_values(self):
        self.assertEqual(self.e1.value, -8)
        self.assertEqual(self.e2.value, -8)

    def test_frets(self):
        self.assertEqual(self.e1.frets, [(0, 0)])
        self.assertEqual(self.e2.frets, [(0, 0)])


class TestChordShapes(unittest.TestCase):
    def setUp(self):
        self.e = Chord([-8, -1, 4, 8, 11, 16])
        self.a = Chord([-8, -3, 4, 9, 13, 16])
        self.d = Chord([-3, 2, 9, 14, 18])
        self.g = Chord([-5, -1, 2, 7, 11, 19])
        self.c = Chord([-8, 0, 4, 7, 12, 16])
        self.b = Chord([-6, -1, 6, 11, 15, 18])
        self.f = Chord([-7, 0, 5, 9, 12, 17])
        self.chords = [self.e, self.a, self.d, self.g, self.c, self.b, self.f]
        self.shapes = [open_e, open_a, open_d, open_g, open_c, barre_b, barre_f]

    def test_shape_presence(self):
        for chord, shape in zip(self.chords, self.shapes):
            with self.subTest(i=chord):
                self.assertIn(shape, chord.shapes)

    def test_shape_selection(self):
        for chord, shape in zip(self.chords, self.shapes):
            with self.subTest(i=chord):
                self.assertEqual(shape, chord.shape)

    def test_4_note_chord_shapes(self):
        C7 = Chord(['C4', 'E4', 'A#4', 'C5'])
        C7_shape = [(1,3), (2,2), (3,3), (4,1)]
        Bdim = Chord(['B3', 'F4', 'G#4', 'D5'])
        Bdim_shape = [(1,2), (2,3), (3,1), (4,3)]
        Dmaj7 = Chord(['D4', 'A4', 'C#5', 'F#5'])
        Dmaj7_shape = [(2,0), (3,2), (4,2), (5,2)]
#        cV_Dmaj7_shape = [(1,5), (2,7), (3,6), (4,7)]
        E7 = Chord(['B4', 'E5', 'G#5', 'D6'])
        E7_shape = [(2,9), (3,9), (4,9), (5,10)]
        cVII_A = Chord(['A4', 'E5', 'A5', 'C#6'])
        cVII_A_shape = [(2,7), (3,9), (4,10), (5,9)]
        cVII_G = Chord(['G4', 'B4', 'D5', 'G5'])
        cVII_G_shape = [(1,10), (2,9), (3,7), (4,8)]
        for chord, shape in zip((C7, Bdim, Dmaj7, E7, cVII_A, cVII_G),
            (C7_shape, Bdim_shape, Dmaj7_shape, E7_shape, cVII_A_shape, cVII_G_shape)):
            with self.subTest(i=chord):
                self.assertEqual(chord.shape, shape)


class TestFingers(unittest.TestCase):
    def test_null_finger(self):
        self.assertEqual(Finger().position, None)
        self.assertEqual(Finger().string, None)
        self.assertEqual(Finger().fret, None)
        self.assertEqual(Finger().down, False)

    def test_init_position(self):
        for string, fret in it.product(range(6), range(12)):
            with self.subTest(i=(string, fret)):
                f = Finger(string, fret)
                if fret == 0:  # Fret 0 is open, thus no position
                    self.assertEqual(f.string, None)
                    self.assertEqual(f.fret, None)
                else:
                    self.assertEqual(f.string, string)
                    self.assertEqual(f.fret, fret)

    def test_finger_moves(self):
        for string, fret in it.product(range(6), range(12)):
            f = Finger(0, 1)
            with self.subTest(i=(string, fret)):
                if fret == 0:  # Moving to 0 means lifing the finger
                    self.assertEqual(f.move((string, fret)), 0)
                    self.assertEqual(f.string, None)
                    self.assertEqual(f.fret, None)
                else:
                    self.assertEqual(f.move((string, fret)), string+fret-1)
                    self.assertEqual(f.string, string)
                    self.assertEqual(f.fret, fret)


class TestManualHandShapes(unittest.TestCase):
    def test_manual_open_c_shape(self):
        h = Hand()
        h.open_strings = [0, 3, 5]
        h.fingers[0].move((4, 1))
        h.fingers[1].move((2, 2))
        h.fingers[2].move((1, 3))
        self.assertEqual(h.shape, open_c)

    def test_manual_open_a_shape(self):
        h = Hand()
        h.open_strings = (0, 1, 5)
        h.fingers[0].move((2, 2))
        h.fingers[1].move((3, 2))
        h.fingers[2].move((4, 2))
        self.assertEqual(h.shape, open_a)

    def teat_manual_open_g_shape(self):
        h = Hand()
        h.open_strings = [2, 3, 4]
        h.fingers[0].move((1, 2))
        h.fingers[1].move((0, 3))
        h.fingers[2].move((5, 3))
        self.assertEqual(h.shape, open_g)

    def test_manual_open_e_shape(self):
        h = Hand()
        h.open_strings = [0, 4, 5]
        h.fingers[0].move((3, 1))
        h.fingers[1].move((1, 2))
        h.fingers[2].move((2, 2))
        self.assertEqual(h.shape, open_e)

    def test_manual_open_d_shape(self):
        h = Hand()
        h.open_strings = [1, 2]
        h.fingers[0].move((3, 2))
        h.fingers[1].move((4, 3))
        h.fingers[2].move((5, 2))
        self.assertEqual(h.shape, open_d)

    def test_manual_barre_a_shape(self):
        h = Hand()
        h.barre = True
        h.fingers[0].move((0, 5))
        h.fingers[1].move((1, 7))
        h.fingers[2].move((2, 7))
        h.fingers[3].move((3, 6))
        self.assertEqual(h.shape, barre_a)

    def test_manual_barre_b_shape(self):
        h = Hand()
        h.barre = True
        h.fingers[0].move((0, 2))
        h.fingers[1].move((2, 4))
        h.fingers[2].move((3, 4))
        h.fingers[3].move((4, 4))
        self.assertEqual(h.shape, barre_b)


class TestInitHandShapes(unittest.TestCase):
    def test_single_notes(self):
        for string, fret in it.product(range(5), range(19)):
            with self.subTest(i=(string, fret)):
                h = Hand([(string, fret)])
                self.assertEqual(h.shape, [(string, fret)])

    def test_all_open_shape(self):
        h = Hand(all_open)
        self.assertEqual(h.shape, all_open)

    def test_init_open_c_shape(self):
        h = Hand(open_c)
        self.assertEqual(h.shape, open_c)

    def test_init_open_a_shape(self):
        h = Hand(open_a)
        self.assertEqual(h.shape, open_a)

    def test_init_open_g_shape(self):
        h = Hand(open_g)
        self.assertEqual(h.shape, open_g)

    def test_init_open_e_shape(self):
        h = Hand(open_e)
        self.assertEqual(h.shape, open_e)

    def test_init_open_d_shape(self):
        h = Hand(open_d)
        self.assertEqual(h.shape, open_d)

    def test_init_barre_a_shape(self):
        h = Hand(barre_a)
        self.assertEqual(h.shape, barre_a)

    def test_init_barre_b_shape(self):
        h = Hand(barre_b)
        self.assertEqual(h.shape, barre_b)


class TestHandMoves(unittest.TestCase):
    def test_null_move(self):
        h = Hand(all_open)
        self.assertEqual(h.move(all_open), 0)

    def test_barred_slide_up_f_to_a(self):
        h = Hand(barre_f)
        self.assertEqual(h.move(barre_a), 4)

    def test_barred_slide_down_a_to_f(self):
        h = Hand(barre_a)
        self.assertEqual(h.move(barre_f), 4)

    def test_chord_change_c_to_g(self):
        h = Hand(open_c)
        self.assertEqual(h.move(open_g), 11)

    def test_chord_change_e_to_a(self):
        h = Hand(open_e)
        self.assertEqual(h.move(open_a), 8)


class TestHandStrain(unittest.TestCase):
    def test_null_strain(self):
        h = Hand(all_open)
        self.assertEqual(h.strain, 0)

    def test_single_notes(self):
        for string, fret in it.product(range(5), range(19)):
            with self.subTest(i=(string, fret)):
                h = Hand([(string, fret)])
                self.assertEqual(h.strain, max(0, fret-12))

    def test_open_c_strain(self):
        h = Hand(open_c)
        self.assertEqual(h.strain, 1)

    def test_open_a_strain(self):
        h = Hand(open_a)
        self.assertEqual(h.strain, 2)

    def test_open_g_strain(self):
        h = Hand(open_g)
        self.assertEqual(h.strain, 5)

    def test_open_e_strain(self):
        h = Hand(open_e)
        self.assertEqual(h.strain, 2)

    def test_open_d_strain(self):
        ''' Should be 2, but barring it does hit 1. I'll allow it. '''
        h = Hand(open_d)
        self.assertEqual(h.strain, 1)

    def test_barre_b_strain(self):
        h = Hand(barre_b)
        self.assertEqual(h.strain, 6)

    def test_barre_f_strain(self):
        h = Hand(barre_f)
        self.assertEqual(h.strain, 6)

    def test_barre_a_strain(self):
        h = Hand(barre_a)
        self.assertEqual(h.strain, 6)


if __name__ == '__main__':
    all_open = [(0,0), (1,0), (2,0), (3,0), (4,0), (5,0)]
    open_c = [(0,0), (1,3), (2,2), (3,0), (4,1), (5,0)]
    open_a = [(0,0), (1,0), (2,2), (3,2), (4,2), (5,0)]
    open_g = [(0,3), (1,2), (2,0), (3,0), (4,0), (5,3)]
    open_e = [(0,0), (1,2), (2,2), (3,1), (4,0), (5,0)]
    open_d = [(1,0), (2,0), (3,2), (4,3), (5,2)]
    barre_b = [(0,2), (1,2), (2,4), (3,4), (4,4), (5,2)]
    barre_f = [(0,1), (1,3), (2,3), (3,2), (4,1), (5,1)]
    barre_a = [(0,5), (1,7), (2,7), (3,6), (4,5), (5,5)]

    unittest.main()
