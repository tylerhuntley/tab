import unittest
import tab
from notes import Note


class TestBlankStaticBars(unittest.TestCase):
    def setUp(self):
        self.bar = tab.Bar()
        self.staff = tab.Staff()
        self.tabs = tab.Tab()

    def test_null_bar(self):
        self.assertEqual(str(self.bar), f"|{' ' * 32}|\n" * 6)

    def test_null_staff(self):
        self.assertEqual(str(self.staff), '\n')

    def test_blank_staff(self):
        """ Test 1-4 empty bars on a single, long staffline. """
        self.maxDiff = None
        LINE = f"|{'-' * 32}"
        for i in range(1, 5):
            with self.subTest(i=i):
                STAFF = (LINE  * i + '|\n') * 6
                self.staff.add_bar(self.bar)
                self.assertEqual(str(self.staff), STAFF)

    def test_blank_tab(self):
        """ Assumes a 2 bar limit for page width.
        Will want to allow more flexibility. """
        self.maxDiff = None  # Display full-length failure info
        LINE = f"|{'-' * 32}"
        ONE_BAR = (LINE + '|\n') * 6 + '\n'
        TWO_BAR = (LINE * 2 + '|\n') * 6 + '\n'
        for i in range(1, 5):
            with self.subTest(i=i+1):
                TAB = TWO_BAR * ((i+1) // 2) + ONE_BAR * ((i+1) % 2)
                self.tabs.add_bar(self.bar)
                self.assertEqual(str(self.tabs), TAB)


class TestDynamicBars(unittest.TestCase):
    def test_null_bar(self):
        self.bar = tab.Bar(width=tab.MIN_WIDTH)
        self.assertEqual(self.bar, f"|{' ' * tab.MIN_WIDTH}|\n" * 6)

    # The following use improper notes arguments, for testing, for now.
    def test_whole_note(self):
        self.bar = tab.Bar(notes=[(0, 1)])
        self.bar.add_note((0, 0), 1)
        if PRINT:
            print('Dynamic whole note: ')
            print(self.bar)
        self.assertEqual(len(self.bar), 8+2)

    def test_half_note(self):
        self.bar = tab.Bar(notes=[(0, 1/2)])
        for i in range(2):
            self.bar.add_note((0, 0), 1/2)
        if PRINT:
            print('Dynamic half notes: ')
            print(self.bar)
        self.assertEqual(len(self.bar), 8+2)

    def test_quarter_note(self):
        self.bar = tab.Bar(notes=[(0, 1/4)])
        for i in range(4):
            self.bar.add_note((0, 0), 1/4)
        if PRINT:
            print('Dynamic quarter notes: ')
            print(self.bar)
        self.assertEqual(len(self.bar), 16+2)

    def test_eighth_note(self):
        self.bar = tab.Bar(notes=[(0, 1/8)])
        for i in range(8):
            self.bar.add_note((0, 0), 1/8)
        if PRINT:
            print('Dynamic eighth notes: ')
            print(self.bar)
        self.assertEqual(len(self.bar), 32+2)

    def test_sixteenth_note(self):
        self.bar = tab.Bar(notes=[(0, 1/16)])
        for i in range(16):
            self.bar.add_note((0, 0), 1/16)
        if PRINT:
            print('Dynamic sixteenth notes: ')
            print(self.bar)
        self.assertEqual(len(self.bar), 64+2)


class TestStaticBars(unittest.TestCase):
    def test_length_limit(self):
        ''' Ensure notes added beyond 1 bars-length are ignored'''
        bar_0 = tab.Bar()
        bar_0.add_note((0, 0), 1)
        for line in bar_0.lines:
            self.assertEqual(len(line), 34)

        bar_1 = tab.Bar()
        bar_1.add_note((0, 0), 1)
        bar_1.add_note((0, 0), 1)
        for line in bar_1.lines:
            self.assertEqual(len(line), 34)

        bar_4 = tab.Bar()
        for i in range(5):
            bar_4.add_note((0, 0), 1/4)
        for line in bar_4.lines:
            self.assertEqual(len(line), 34)

        bar_16 = tab.Bar()
        for i in range(17):
            bar_16.add_note((0, 0), 1/16)
        for line in bar_16.lines:
            self.assertEqual(len(line), 34)


    def test_E_major_scale(self):
        ''' Add notes manually, one by one '''
        scale = tab.Bar()
        scale.add_note(Note('E3').get_low_fret(), 1/8)
        scale.add_note(Note('F#3').get_low_fret(), 1/8)
        scale.add_note(Note('G#3').get_low_fret(), 1/8)
        scale.add_note(Note('A3').get_low_fret(), 1/8)
        scale.add_note(Note('B3').get_low_fret(), 1/8)
        scale.add_note(Note('C#4').get_low_fret(), 1/8)
        scale.add_note(Note('D#4').get_low_fret(), 1/8)
        scale.add_note(Note('E4').get_low_fret(), 1/8)
        if PRINT:
            print('Static E Major:')
            print(scale)
        self.assertEqual(scale, '|--------------------------------|\n'
                                '|--------------------------------|\n'
                                '|--------------------------------|\n'
                                '|------------------------1---2---|\n'
                                '|------------0---2---4-----------|\n'
                                '|0---2---4-----------------------|\n')

    def test_A_major_scale(self):
        ''' Test add_run using Note addition '''
        root = Note('A3')
        major = (0, 2, 4, 5, 7, 9, 11, 12)
        scale = tab.Bar()
        scale.add_run([(root + i).get_low_fret() for i in major], 1/8)
        if PRINT:
            print('Static A Major:')
            print(scale)
        self.assertEqual(scale,'|--------------------------------|\n'
                               '|--------------------------------|\n'
                               '|------------------------1---2---|\n'
                               '|------------0---2---4-----------|\n'
                               '|0---2---4-----------------------|\n'
                               '|--------------------------------|\n')

    def test_D_major_scale(self):
        ''' Test add_run using list of Note names '''
        D_major = ('D4', 'E4', 'F#4', 'G4', 'A4', 'B4', 'C#5', 'D5')
        scale = tab.Bar()
        scale.add_run([Note(i).get_low_fret() for i in D_major], 1/8)
        if PRINT:
            print('Static D Major:')
            print(scale)
        self.assertEqual(scale,'|--------------------------------|\n'
                               '|--------------------0---2---3---|\n'
                               '|------------0---2---------------|\n'
                               '|0---2---4-----------------------|\n'
                               '|--------------------------------|\n'
                               '|--------------------------------|\n')


class TestTabs(unittest.TestCase):
    def SetUp(self):
        self.tabs = tab.Tab()

    def test_two_bars(self):
        self.tabs = tab.Tab()
        root = Note('A3')
        major = (0, 2, 4, 5, 7, 9, 11, 12)
        self.tabs.add_run([(root + i).get_low_fret() for i in major], 1/4)
        if PRINT:
            print('Static A major, two bars: ')
            print(self.tabs)

        self.assertEqual(str(self.tabs),
'|--------------------------------|--------------------------------|\n'
'|--------------------------------|--------------------------------|\n'
'|--------------------------------|----------------1-------2-------|\n'
'|------------------------0-------|2-------4-----------------------|\n'
'|0-------2-------4---------------|--------------------------------|\n'
'|--------------------------------|--------------------------------|\n\n')

    def test_four_bars(self):
        self.tabs = tab.Tab()
        root = Note('A3')
        major = (0, 2, 4, 5, 7, 9, 11, 12)
        self.tabs.add_run([(root + i).get_low_fret() for i in major], 1/2)
        if PRINT:
            print('Static A major, four bars: ')
            print(self.tabs)

        self.assertEqual(str(self.tabs),
'|--------------------------------|--------------------------------|\n'
'|--------------------------------|--------------------------------|\n'
'|--------------------------------|--------------------------------|\n'
'|--------------------------------|----------------0---------------|\n'
'|0---------------2---------------|4-------------------------------|\n'
'|--------------------------------|--------------------------------|\n'
'\n'
'|--------------------------------|--------------------------------|\n'
'|--------------------------------|--------------------------------|\n'
'|--------------------------------|1---------------2---------------|\n'
'|2---------------4---------------|--------------------------------|\n'
'|--------------------------------|--------------------------------|\n'
'|--------------------------------|--------------------------------|\n\n')



if __name__ == '__main__':
    PRINT = True
#    print()
    unittest.main()
