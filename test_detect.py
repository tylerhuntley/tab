import unittest
from detect import Controller

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


if __name__ == '__main__':
    tests = {}
    for name in NUM_STAFFS:
        if name not in EXCLUDE:
            tests[name] = Controller(name, TEST=True)

    unittest.main()
