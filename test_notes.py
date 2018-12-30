import unittest
import itertools as it
from notes import Note, Chord, Finger


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


@unittest.expectedFailure
class TestOpenChords(unittest.TestCase):
    def setUp(self):
        self.e = Chord([-8, -1, 4, 8, 11, 16])
        self.a = Chord([-8, -3, 4, 9, 13, 16])
        self.d = Chord([-3, 2, 9, 14, 18])
        self.g = Chord([-5, -1, 2, 7, 11, 19])
        self.c = Chord([0, 4, 7, 12, 16])
        self.chords = [self.e, self.a, self.d, self.g, self.c]

        self.e_shape = [(0,0), (1,2), (2,2), (3,1), (4,0), (5,0)]
        self.a_shape = [(0,0), (1,0), (2,2), (3,2), (4,2), (5,0)]
        self.d_shape = [(1,0), (2,0), (3,2), (4,3), (5,2)]
        self.g_shape = [(0, 3), (1,2), (2,0), (3,0), (4,0), (5,3)]
        self.c_shape = [(1,3), (2,2), (3,0), (4,1), (5,0)]
        self.shapes = [self.e_shape, self.a_shape, self.d_shape,
                       self.g_shape, self.c_shape]

    def test_shapes(self):
        for chord, shape in zip(self.chords, self.shapes):
            with self.subTest(i=chord):
                self.assertEqual(chord.shape, shape)

class TestFingers(unittest.TestCase):
    def setUp(self):
        self.f = Finger()

    def test_null_finger(self):
        self.assertEqual(Finger().position, None)
        for string, fret in it.product(range(6), range(12)):
            self.assertEqual(Finger().move((string, fret)), 0)

    def test_properties(self):
        self.assertEqual(Finger().string, None)
        self.assertEqual(Finger().fret, None)
        for string, fret in it.product(range(6), range(12)):
            with self.subTest(i=(string, fret)):
                f = Finger(string, fret)
                self.assertEqual(f.string, string)
                self.assertEqual(f.fret, fret)

    def test_finger_moves(self):
        for string, fret in it.product(range(6), range(12)):
            f = Finger(0, 0)
            with self.subTest(i=(string, fret)):
                self.assertEqual(f.move((string, fret)), string+fret)


if __name__ == '__main__':

    unittest.main()
