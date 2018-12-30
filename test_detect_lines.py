import unittest
from detect_lines import StaffLines

# KEY = {'line': 5, 'kumbayah': 10, 'star': 15, 'sleeves': 20, 'rosita': 35}
# Doubled key values for edged images
NUM_STAFF_LINES = {'blank': 120, 'line': 10, 'kumbayah': 20, 'star': 30, 'sleeves': 40, 'rosita': 70}
NUM_STAFFS = {'blank': 12, 'line': 1, 'kumbayah': 2, 'star': 3, 'sleeves': 4, 'rosita': 7}
EXCLUDE = {'rosita'}

class TestStaffLines(unittest.TestCase):
    def setUp(self):
        self.files = []
        for i in NUM_STAFF_LINES:
            if i not in EXCLUDE:
                self.files.append(test_files[i])

    def test_counts(self):
        for file in self.files:
            with self.subTest(i=file.name):
                counts = {len(i) for i in file.line_data.values()}
                self.assertIn(NUM_STAFF_LINES[file.name], counts)

    def test_common_param(self):
        sets = []
        # Gather sets of all params that detect the proper number of lines
        for file in self.files:
            temp = set(file.get_params(NUM_STAFF_LINES[file.name]))
            sets.append(temp)
            print(f'{file.name}: {len(temp)}\n')
        params = set.intersection(*sets)
        print(f'Common: {len(params)}\n{params}')
        # Verify at least one set detects the right lines in ALL images
        self.assertGreaterEqual(len(params), 1)


class TestStaffs(unittest.TestCase):
    def setUp(self):
        self.files = []
        for i in NUM_STAFFS:
            if i not in EXCLUDE:
                self.files.append(test_files[i])

    def test_staff_counts(self):
        for file in self.files:
            self.assertEqual(len(file.staff_views), NUM_STAFFS[file.name])
            for view in file.staff_views:
                # Empty views are surely wrong, but how to test CORRECTNESS?
                self.assertGreater(view.size, 0)

    def test_staff_continuity(self):
        ''' Bottom of each staff box must align with the top of the next'''
        for file in self.files:
            for a, b in zip(file.staff_boxes[:-1], file.staff_boxes[1:]):
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
    test_files = {}
    for name in NUM_STAFF_LINES:
        if name not in EXCLUDE:
            test_files[name] = StaffLines(name)

    unittest.main()
