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
            self.assertEqual(len(test.staff_views), NUM_STAFFS[test.name])
            for view in test.staff_views:
                # Empty views are surely wrong, but how to test CORRECTNESS?
                self.assertGreater(view.size, 0)

    def test_staff_continuity(self):
        ''' Bottom of each staff box must align with the top of the next'''
        for test in tests:
            for a, b in zip(test.staff_boxes[:-1], test.staff_boxes[1:]):
                self.assertEqual(a[3], b[1])


@unittest.expectedFailure
class TestBars(unittest.TestCase):
    def setUp(self):
        self.tests = {}

    def test_star(self):
        self.assertEqual(self.tests['star'].bars, (4, 4, 3))

    def test_sleeves(self):
        self.assertEqual(self.tests['sleeves'].bars, (8, 8, 9, 8))

    def test_rosita(self):
        self.assertEqual(self.tests['rosita'].bars, (4, 6, 4, 5, 5, 5, 5))

    def test_line(self):
        self.assertEqual(self.tests['line'].bars, (5,))

    def test_kumbayah(self):
        self.assertEqual(self.tests['kumbayah'].bars, (5, 4))


if __name__ == '__main__':
    tests = []
    for name in NUM_STAFFS:
        if name not in EXCLUDE:
            tests.append(StaffDetector(name, TEST=True))

    unittest.main()
