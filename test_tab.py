import unittest
import tab
import notes


class TestBlankStaticBars(unittest.TestCase):
    def setUp(self):
        self.bar = tab.Bar(width=32)
        self.staff = tab.Staff()
        self.arr = tab.Arrangement(width=32)

    def test_null_bar(self):
        self.assertEqual(self.bar, f"|{'-' * 32}|\n" * 6)

    def test_null_staff(self):
        self.assertEqual(str(self.staff), '')

    def test_blank_staff(self):
        """ Test 1-4 empty bars on a single, long staffline. """
        self.maxDiff = None
        LINE = f"|{'-' * 32}"
        for i in range(1, 5):
            with self.subTest(i=i):
                STAFF = (LINE  * i + '|\n') * 6
                self.staff.add_bar(self.bar)
                self.assertEqual(str(self.staff), STAFF)

    def test_blank_arrangement(self):
        """ Assumes a 2 bar limit for page width.
        Will want to allow more flexibility. """
        self.maxDiff = None  # Display full-length failure info
        LINE = f"|{'-' * 32}"
        ONE_BAR = (LINE + '|\n') * 6 + '\n'
        TWO_BAR = (LINE * 2 + '|\n') * 6 + '\n'
        for i in range(1, 5):
            with self.subTest(i=i+1):
                TAB = TWO_BAR * ((i+1) // 2) + ONE_BAR * ((i+1) % 2)
                self.arr.add_bar(self.bar)
                self.assertEqual(str(self.arr), TAB)


class TestDynamicBars(unittest.TestCase):
    def test_null_bar(self):
        bar = tab.Bar()
        self.assertEqual(bar, f"|{'-' * tab.MIN_WIDTH}|\n" * 6)

    # The following use improper notes arguments, for testing, for now.
    def test_whole_note(self):
        bar = tab.Bar()
        bar.add_shape(notes.Shape((0, 0)), 1)
        try: self.assertEqual(len(bar), 8+2)
        except AssertionError as e:
            print(f'Dynamic whole notes:\n{bar}')
            raise e

    def test_half_note(self):
        bar = tab.Bar()
        for i in range(2):
            bar.add_shape(notes.Shape((0, 0)), 1/2)
        try: self.assertEqual(len(bar), 8+2)
        except AssertionError as e:
            print(f'Dynamic half notes:\n{bar}')
            raise e

    def test_quarter_note(self):
        bar = tab.Bar()
        for i in range(4):
            bar.add_shape(notes.Shape((0, 0)), 1/4)
        try: self.assertEqual(len(bar), 16+2)
        except AssertionError as e:
            print(f'Dynamic quarter notes:\n{bar}')
            raise e

    def test_eighth_note(self):
        bar = tab.Bar()
        for i in range(8):
            bar.add_shape(notes.Shape((0, 0)), 1/8)
        try: self.assertEqual(len(bar), 32+2)
        except AssertionError as e:
            print(f'Dynamic eighth notes:\n{bar}')
            raise e

    def test_sixteenth_note(self):
        bar = tab.Bar()
        for i in range(16):
            bar.add_shape(notes.Shape((0, 0)), 1/16)
        try: self.assertEqual(len(bar), 64+2)
        except AssertionError as e:
            print(f'Dynamic sixteenth notes:\n{bar}')
            raise e


#@unittest.expectedFailure
class TestStaticBars(unittest.TestCase):
    def test_length_limit(self):
        ''' Ensure notes added beyond 1 bars-length are ignored'''
        bar_0 = tab.Bar(width=32)
        bar_0.add_shape(notes.Shape((0, 0)), 1)
        for line in bar_0.lines:
            self.assertEqual(len(line), 34)

        bar_1 = tab.Bar(width=32)
        bar_1.add_shape(notes.Shape((0, 0)), 1)
        bar_1.add_shape(notes.Shape((0, 0)), 1)
        for line in bar_1.lines:
            self.assertEqual(len(line), 34)

        bar_4 = tab.Bar(width=32)
        for i in range(5):
            bar_4.add_shape(notes.Shape((0, 0)), 1/4)
        for line in bar_4.lines:
            self.assertEqual(len(line), 34)

        bar_16 = tab.Bar(width=32)
        for i in range(17):
            bar_16.add_shape(notes.Shape((0, 0)), 1/16)
        for line in bar_16.lines:
            self.assertEqual(len(line), 66)


    def test_E_major_scale(self):
        ''' Add eighth Notes manually, one by one '''
        bar = tab.Bar()
        for note in ((0,0), (0,2), (0,4), (1,0), (1,2), (1,4), (2,1), (2,2)):
            bar.add_shape(notes.Shape(note), 1/8)
        try: self.assertEqual(bar, '|--------------------------------|\n'
                                '|--------------------------------|\n'
                                '|--------------------------------|\n'
                                '|------------------------1---2---|\n'
                                '|------------0---2---4-----------|\n'
                                '|0---2---4-----------------------|\n')
        except AssertionError as e:
            print(f'Static E major, one bar:\n{bar}')
            raise e

    def test_A_major_scale(self):
        ''' Test add_run using Note addition '''
        root = notes.Note('A3')
        major = (0, 2, 4, 5, 7, 9, 11, 12)
        bar = tab.Bar()
        for i in major:
            shape = (root + i).get_low_fret()
            bar.add_shape(shape, 1/8)
        try: self.assertEqual(bar,'|--------------------------------|\n'
                               '|--------------------------------|\n'
                               '|------------------------1---2---|\n'
                               '|------------0---2---4-----------|\n'
                               '|0---2---4-----------------------|\n'
                               '|--------------------------------|\n')
        except AssertionError as e:
            print(f'Static A major, one bar:\n{bar}')
            raise e

    def test_D_major_scale(self):
        ''' Test add_run using list of Note names '''
        D_major = ('D4', 'E4', 'F#4', 'G4', 'A4', 'B4', 'C#5', 'D5')
        bar = tab.Bar()
        for note in D_major:
            shape = notes.Note(note).get_low_fret()
            bar.add_shape(shape, 1/8)
        try: self.assertEqual(bar,'|--------------------------------|\n'
                               '|--------------------0---2---3---|\n'
                               '|------------0---2---------------|\n'
                               '|0---2---4-----------------------|\n'
                               '|--------------------------------|\n'
                               '|--------------------------------|\n')
        except AssertionError as e:
            print(f'Static D major, one bar:\n{bar}')
            raise e


#@unittest.expectedFailure
class TestArrangements(unittest.TestCase):
    def test_null_arrangement(self):
        arr = tab.Arrangement()
        self.assertEqual(arr, str(tab.Bar()) + '\n')

    def test_two_bars(self):
        arr = tab.Arrangement()
        root = notes.Note('A3')
        major = (0, 2, 4, 5, 7, 9, 11, 12)
        arr.add_run([(root + i).get_low_fret() for i in major], 1/4)
        try: self.assertEqual(arr,
'|----------------|----------------|\n'
'|----------------|----------------|\n'
'|----------------|--------1---2---|\n'
'|------------0---|2---4-----------|\n'
'|0---2---4-------|----------------|\n'
'|----------------|----------------|\n\n')
        except AssertionError as e:
            print(f'Static A major, two bars:\n{arr}')
            raise e

    def test_four_bars(self):
        arr = tab.Arrangement()
        root = notes.Note('A3')
        major = (0, 2, 4, 5, 7, 9, 11, 12)
        arr.add_run([(root + i).get_low_fret() for i in major], 1/2)
        try: self.assertEqual(arr,
'|--------|--------|--------|--------|\n'
'|--------|--------|--------|--------|\n'
'|--------|--------|--------|1---2---|\n'
'|--------|----0---|2---4---|--------|\n'
'|0---2---|4-------|--------|--------|\n'
'|--------|--------|--------|--------|\n\n')
        except AssertionError as e:
            print(f'Static A major, four bars:\n{arr}')
            raise e

    def test_single_notes(self):
        arr = tab.Arrangement()
        for note in [(0,0), (0,2), (0,4), (1,0), (1,2), (1,4), (2,1), (2,2)]:
            arr.add_shape(notes.Shape(note), 1/8)
#        tabs = arr.transcribe()
        expected = ('|--------------------------------|\n'
                    '|--------------------------------|\n'
                    '|--------------------------------|\n'
                    '|------------------------1---2---|\n'
                    '|------------0---2---4-----------|\n'
                    '|0---2---4-----------------------|\n\n')
        try: self.assertEqual(arr, expected)
        except AssertionError as e:
            print(f'E major scale, one bar:\n{arr}')
            raise e

    def test_chords(self):
        arr = tab.Arrangement()
        sotw = [ ([(0,0), (1,2), (2,2)], 1/4), ([(0,3), (1,5), (2,5)], 1/4),
                ([(0,5), (1,7), (2,7)], 3/8), ([(0,0), (1,2), (2,2)], 1/4),
                ([(0,3), (1,5), (2,5)], 1/4), ([(0,7), (1,9), (2,9)], 1/8),
                ([(0,5), (1,7), (2,7)], 1/2) ]
        for note in sotw:
            frets, duration = note
            arr.add_shape(notes.Shape(frets), duration)
#        tabs = arr.transcribe()
        try: self.assertEqual(arr,
'|----------------|--------------------------------|\n'
'|----------------|--------------------------------|\n'
'|----------------|--------------------------------|\n'
'|2---5---7-----2-|----5-------9---7---------------|\n'
'|2---5---7-----2-|----5-------9---7---------------|\n'
'|0---3---5-----0-|----3-------7---5---------------|\n\n')
        except AssertionError as e:
            print(f'Smoke on the Water, two bars:\n{arr}')
            raise e

#    @unittest.expectedFailure  # TODO deal with 3/4 time incomplete bars
    def test_mixed_notes(self):
        ''' Sixth notes? Tab() will need to handle 3/4 time as well '''
        arr = tab.Arrangement()
        bb1 = [ ([(0,3), (4,0)], 1/6), ([(3,0)], 1/6), ([(1,0), (4,1)], 1/6),
              ([(3,0)], 1/6), ([(1,2), (4,3)], 1/6), ([(3,0)], 1/6) ]
        bb2 = [ ([(1,10), (4,12)], 1/4), ([(3,0)], 1/8), ([(4,12)], 1/8),
              ([(1,10)], 1/8), ([(4,12)], 1/8), ([(3,0)], 1/4) ]
        for note in bb1 + bb2:
            frets, duration = note
            arr.add_shape(notes.Shape(frets), duration)
#        tabs = arr.transcribe()
        try: self.assertEqual(arr,
'|------------------------|--------------------------------|\n'
'|0-------1-------3-------|12----------12------12----------|\n'
'|----0-------0-------0---|--------0---------------0-------|\n'
'|------------------------|--------------------------------|\n'
'|--------0-------2-------|10--------------10--------------|\n'
'|3-----------------------|--------------------------------|\n\n')
        except AssertionError as e:
            print(f'Blackbird, two bars:\n{arr}')
            raise e


if __name__ == '__main__':
#    print()
    unittest.main()
