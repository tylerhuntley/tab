import unittest
from detect import StaffDetector

NUM_STAFFS = {'line': 1, 'kumbayah': 2, 'ignite': 3, 'star': 3,
              'sleeves': 4, 'romance': 6, 'rosita': 7, 'blank': 12}
NUM_LINES = {name: NUM_STAFFS[name] * 5 for name in NUM_STAFFS}
EXCLUDE = {'rosita'}


class TestStaffs(unittest.TestCase):
    @unittest.expectedFailure
    def test_line_counts(self):
        for test in tests:
            with self.subTest(i=test.name):
                self.assertEqual(NUM_LINES[test.name], len(test.lines))

    def test_staff_counts(self):
        for test in tests:
            self.assertEqual(len(test.staff_lines), NUM_STAFFS[test.name])

    def test_staff_continuity(self):
        ''' Bottom of each staff box must align with the top of the next'''
        for test in tests:
            for a, b in zip(test.large_boxes[:-1], test.large_boxes[1:]):
                self.assertEqual(a[3], b[1])


if __name__ == '__main__':
    tests = []
    for name in NUM_STAFFS:
        if name not in EXCLUDE:
            tests.append(StaffDetector(name, TEST=True))

    unittest.main()
