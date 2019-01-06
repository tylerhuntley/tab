import unittest, music


class TestNotes(unittest.TestCase):
    def setUp(self):
        self.e1 = music.Note(-8)
        self.e2 = music.Note('E3')

    def test_names(self):
        self.assertEqual(self.e1.name, 'E3')
        self.assertEqual(self.e2.name, 'E3')

    def test_values(self):
        self.assertEqual(self.e1.value, -8)
        self.assertEqual(self.e2.value, -8)

    def test_frets(self):
        self.assertEqual(self.e1.shapes, [(0, 0)])
        self.assertEqual(self.e2.shapes, [(0, 0)])

    def test_fret_limit(self):
        a6 = music.Note('A6')
        self.assertEqual(a6.shapes, [(5,17)])
        e6 = music.Note('E6')
        self.assertEqual(e6.shapes, [(4,17), (5,12)])


class TestChordShapes(unittest.TestCase):
    def setUp(self):
        self.e = music.Chord([-8, -1, 4, 8, 11, 16])
        self.a = music.Chord([-8, -3, 4, 9, 13, 16])
        self.d = music.Chord([-3, 2, 9, 14, 18])
        self.g = music.Chord([-5, -1, 2, 7, 11, 19])
        self.c = music.Chord([-8, 0, 4, 7, 12, 16])
        self.b = music.Chord([-6, -1, 6, 11, 15, 18])
        self.f = music.Chord([-7, 0, 5, 9, 12, 17])
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
        C7 = music.Chord(['C4', 'E4', 'A#4', 'C5'])
        C7_shape = [(1,3), (2,2), (3,3), (4,1)]
        Bdim = music.Chord(['B3', 'F4', 'G#4', 'D5'])
        Bdim_shape = [(1,2), (2,3), (3,1), (4,3)]
        Dmaj7 = music.Chord(['D4', 'A4', 'C#5', 'F#5'])
        Dmaj7_shape = [(2,0), (3,2), (4,2), (5,2)]
#        cV_Dmaj7_shape = [(1,5), (2,7), (3,6), (4,7)]
        E7 = music.Chord(['B4', 'E5', 'G#5', 'D6'])
        E7_shape = [(2,9), (3,9), (4,9), (5,10)]
        cVII_A = music.Chord(['A4', 'E5', 'A5', 'C#6'])
        cVII_A_shape = [(2,7), (3,9), (4,10), (5,9)]
        cVII_G = music.Chord(['G4', 'B4', 'D5', 'G5'])
        cVII_G_shape = [(1,10), (2,9), (3,7), (4,8)]
        for chord, shape in zip((C7, Bdim, Dmaj7, E7, cVII_A, cVII_G),
            (C7_shape, Bdim_shape, Dmaj7_shape, E7_shape, cVII_A_shape, cVII_G_shape)):
            with self.subTest(i=chord):
                self.assertEqual(chord.shape, shape)

    def test_span_limit(self):
        one = music.Chord(['F3', 'A#5'])
        self.assertEqual(one.shapes, [[1, None, None, None, None, 6]])
        two = music.Chord(['F3', 'F5'])
        self.assertEqual(two.shapes, [[1, None, None, None, 6, None],
                                      [1, None, None, None, None, 1]])


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
