import unittest
import numpy as np
import detect
import music

NUM_STAFFS = {'line': 1, 'kumbayah': 2, 'ignite': 3, 'star': 3,
              'sleeves': 4, 'romance': 6, 'rosita': 7, 'blank': 12}
NUM_LINES = {name: NUM_STAFFS[name] * 5 for name in NUM_STAFFS}
EXCLUDE = {'blank'}


class TestStaffs(unittest.TestCase):
    @unittest.expectedFailure
    def test_line_counts(self):
        for name, test in tests.items():
            with self.subTest(i=name):
                self.assertEqual(len(test.main.lines), NUM_LINES[name])

    def test_staff_counts(self):
        for name, test in tests.items():
            self.assertEqual(len(test.main.staff_lines), NUM_STAFFS[name])

    def test_staff_continuity(self):
        ''' Bottom of each staff box must align with the top of the next'''
        for name, test in tests.items():
            for a, b in zip(test.main.large_boxes[:-1], test.main.large_boxes[1:]):
                self.assertEqual(a[3], b[1])


class TestNotes(unittest.TestCase):
    def setUp(self):
        class Dummy(detect.NoteDetector):
            def __init__(self):
                self.note_size = 1
        self.d = Dummy()

    def test_null_chord_groups(self):
        arr = np.zeros([1,6])
        self.assertEqual(self.d.group_chords(arr), [[]])

    def test_one_note_chord_groups(self):
        arr = np.array([[0,1,0,0,1,0]])
        self.assertEqual(self.d.group_chords(arr), [[(1,0)], [(4,0)]])

    def test_two_note_chord_groups(self):
        arr = np.array([[0,1,0,0,1,0], [0,0,0,0,0,0], [0,1,0,0,1,0]])
        self.assertEqual(self.d.group_chords(arr), [[(1,0), (1,2)], [(4,0), (4,2)]])

    def test_note_naming(self):
        points = [(0,-110), (0,0), (0,20), (0,30), (0,70), (0,140)]
        key = (0, 80)
        names = self.d.name_notes(points, key)
        notes = [music.Note(i) for i in ('C7', 'F5', 'D5', 'C5', 'F4', 'F3')]
        self.assertEqual(names, notes)


if __name__ == '__main__':
    tests = {}
    for name in NUM_STAFFS:
        if name not in EXCLUDE:
            tests[name] = detect.Controller(name, TEST=True)

    unittest.main()
