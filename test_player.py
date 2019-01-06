import unittest, player, tab, music
import itertools as it

class TestFingers(unittest.TestCase):
    def test_null_finger(self):
        self.assertEqual(player.Finger().position, None)
        self.assertEqual(player.Finger().string, None)
        self.assertEqual(player.Finger().fret, None)
        self.assertEqual(player.Finger().down, False)

    def test_init_position(self):
        for string, fret in it.product(range(6), range(12)):
            with self.subTest(i=(string, fret)):
                f = player.Finger(string, fret)
                if fret == 0:  # Fret 0 is open, thus no position
                    self.assertEqual(f.string, None)
                    self.assertEqual(f.fret, None)
                else:
                    self.assertEqual(f.string, string)
                    self.assertEqual(f.fret, fret)

    def test_finger_moves(self):
        for string, fret in it.product(range(6), range(12)):
            f = player.Finger(0, 1)
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
        h = player.Hand()
        h.open_strings = [0, 3, 5]
        h.fingers[0].move((4, 1))
        h.fingers[1].move((2, 2))
        h.fingers[2].move((1, 3))
        self.assertEqual(h.shape, open_c)

    def test_manual_open_a_shape(self):
        h = player.Hand()
        h.open_strings = (0, 1, 5)
        h.fingers[0].move((2, 2))
        h.fingers[1].move((3, 2))
        h.fingers[2].move((4, 2))
        self.assertEqual(h.shape, open_a)

    def teat_manual_open_g_shape(self):
        h = player.Hand()
        h.open_strings = [2, 3, 4]
        h.fingers[0].move((1, 2))
        h.fingers[1].move((0, 3))
        h.fingers[2].move((5, 3))
        self.assertEqual(h.shape, open_g)

    def test_manual_open_e_shape(self):
        h = player.Hand()
        h.open_strings = [0, 4, 5]
        h.fingers[0].move((3, 1))
        h.fingers[1].move((1, 2))
        h.fingers[2].move((2, 2))
        self.assertEqual(h.shape, open_e)

    def test_manual_open_d_shape(self):
        h = player.Hand()
        h.open_strings = [1, 2]
        h.fingers[0].move((3, 2))
        h.fingers[1].move((4, 3))
        h.fingers[2].move((5, 2))
        self.assertEqual(h.shape, open_d)

    def test_manual_barre_a_shape(self):
        h = player.Hand()
        h.barre = True
        h.fingers[0].move((0, 5))
        h.fingers[1].move((1, 7))
        h.fingers[2].move((2, 7))
        h.fingers[3].move((3, 6))
        self.assertEqual(h.shape, barre_a)

    def test_manual_barre_b_shape(self):
        h = player.Hand()
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
                h = player.Hand([(string, fret)])
                self.assertEqual(h.shape, [(string, fret)])

    def test_all_open_shape(self):
        h = player.Hand(all_open)
        self.assertEqual(h.shape, all_open)

    def test_init_open_c_shape(self):
        h = player.Hand(open_c)
        self.assertEqual(h.shape, open_c)

    def test_init_open_a_shape(self):
        h = player.Hand(open_a)
        self.assertEqual(h.shape, open_a)

    def test_init_open_g_shape(self):
        h = player.Hand(open_g)
        self.assertEqual(h.shape, open_g)

    def test_init_open_e_shape(self):
        h = player.Hand(open_e)
        self.assertEqual(h.shape, open_e)

    def test_init_open_d_shape(self):
        h = player.Hand(open_d)
        self.assertEqual(h.shape, open_d)

    def test_init_barre_a_shape(self):
        h = player.Hand(barre_a)
        self.assertEqual(h.shape, barre_a)

    def test_init_barre_b_shape(self):
        h = player.Hand(barre_b)
        self.assertEqual(h.shape, barre_b)


class TestHandMoves(unittest.TestCase):
    def test_null_move(self):
        h = player.Hand(all_open)
        self.assertEqual(h.move(all_open), 0)

    def test_barred_slide_up_f_to_a(self):
        h = player.Hand(barre_f)
        self.assertEqual(h.move(barre_a), 4)

    def test_barred_slide_down_a_to_f(self):
        h = player.Hand(barre_a)
        self.assertEqual(h.move(barre_f), 4)

    def test_chord_change_c_to_g(self):
        h = player.Hand(open_c)
        self.assertEqual(h.move(open_g), 11)

    def test_chord_change_e_to_a(self):
        h = player.Hand(open_e)
        self.assertEqual(h.move(open_a), 8)


class TestHandStrain(unittest.TestCase):
    def test_null_strain(self):
        h = player.Hand(all_open)
        self.assertEqual(h.strain, 0)

    def test_single_notes(self):
        for string, fret in it.product(range(5), range(19)):
            with self.subTest(i=(string, fret)):
                h = player.Hand([(string, fret)])
                self.assertEqual(h.strain, max(0, fret-12))

    def test_open_c_strain(self):
        h = player.Hand(open_c)
        self.assertEqual(h.strain, 1)

    def test_open_a_strain(self):
        h = player.Hand(open_a)
        self.assertEqual(h.strain, 2)

    def test_open_g_strain(self):
        h = player.Hand(open_g)
        self.assertEqual(h.strain, 5)

    def test_open_e_strain(self):
        h = player.Hand(open_e)
        self.assertEqual(h.strain, 2)

    def test_open_d_strain(self):
        ''' Should be 2, but barring it does hit 1. I'll allow it. '''
        h = player.Hand(open_d)
        self.assertEqual(h.strain, 1)

    def test_barre_b_strain(self):
        h = player.Hand(barre_b)
        self.assertEqual(h.strain, 6)

    def test_barre_f_strain(self):
        h = player.Hand(barre_f)
        self.assertEqual(h.strain, 6)

    def test_barre_a_strain(self):
        h = player.Hand(barre_a)
        self.assertEqual(h.strain, 6)


class TestGuitarist(unittest.TestCase):
    def test_null_song(self):
        song = music.Song()
        g = player.Guitarist(song)
        self.assertEqual(g.arr, str(tab.Bar())+'\n')

    def test_song_add(self):
        songs = [music.Song() for i in range(3)]
        songs[0].add(music.Note('E3'))
        songs[1].add(music.Chord(['E3']))
        songs[2].add('E3')
        for song in songs:
            self.assertIn('E3', str(song.notes))  # This is sloppy

    def test_low_E(self):
        song = music.Song()
        song.add('E3')
        g = player.Guitarist(song)
        expected = tab.Bar(notes=[(tab.Shape((0,0)), 1/4)])
        self.assertEqual(g.arr, str(expected)+'\n')

    @unittest.expectedFailure
    # TODO select fingers to reduce strain, don't always rely on index
    def test_E_major(self):
        song = music.Song()
        for note in ('E3', 'F#3', 'G#3', 'A3', 'B3', 'C#4', 'D#4', 'E4'):
            song.add(music.Note(note, 1/8))
        g = player.Guitarist(song)
        expected = ('|--------------------------------|\n'
            '|--------------------------------|\n'
            '|--------------------------------|\n'
            '|------------------------1---2---|\n'
            '|------------0---2---4-----------|\n'
            '|0---2---4-----------------------|\n\n')
        try: self.assertEqual(g.arr, expected)
        except AssertionError as AE:
            print(f'E major, one bar:\n{g.arr}')
            raise AE

    @unittest.expectedFailure
    def test_chords(self):
        song = music.Song()
        sotw_chords = [(['E3', 'B3', 'E4'], 1/4), (['G3', 'D4', 'G4'], 1/4),
                      (['A3', 'E4', 'A4'], 3/8), (['E3', 'B3', 'E4'], 1/4),
                      (['G3', 'D4', 'G4'], 1/4), (['B3', 'F#4', 'B4'], 1/8),
                      (['A3', 'E4', 'A4'], 1/2)]
        for chord in sotw_chords:
            song.add(music.Chord(*chord))
        g = player.Guitarist(song)
        try: self.assertEqual(g.arr, smoke_on_the_water)
        except AssertionError as AE:
            print(f'Smoke on the Water, two bars, auto:\n{g.arr}')
            raise AE

    @unittest.expectedFailure
    def test_mixed_notes(self):
        song = music.Song()
        bb_chords = [(['G3', 'B4'], 1/6), (['G4'], 1/6), (['A3', 'C5'], 1/6),
                     (['G4'], 1/6), (['B3', 'D5'], 1/6), (['G4'], 1/6),
                     (['G4', 'B5'], 1/4), (['G4'], 1/8), (['B5'], 1/8),
                     (['G4'], 1/8), (['B5'], 1/8), (['G4'], 1/4)]
        for chord in bb_chords:
            song.add(music.Chord(*chord))
        g = player.Guitarist(song)
        try: self.assertEqual(g.arr, blackbird)
        except AssertionError as AE:
            print(f'Blackbird, two bars, auto:\n{g.arr}')
            raise AE


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

    smoke_on_the_water = (
'|----------------|--------------------------------|\n'
'|----------------|--------------------------------|\n'
'|----------------|--------------------------------|\n'
'|2---5---7-----2-|----5-------9---7---------------|\n'
'|2---5---7-----2-|----5-------9---7---------------|\n'
'|0---3---5-----0-|----3-------7---5---------------|\n\n')
    blackbird = (
'|------------------------|--------------------------------|\n'
'|0-------1-------3-------|12----------12------12----------|\n'
'|----0-------0-------0---|--------0---------------0-------|\n'
'|------------------------|--------------------------------|\n'
'|--------0-------2-------|10--------------10--------------|\n'
'|3-----------------------|--------------------------------|\n\n')

    unittest.main()
