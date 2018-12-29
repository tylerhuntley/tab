import unittest
from detect_lines import StaffLines

# KEY = {'line': 5, 'kumbayah': 10, 'star': 15, 'sleeves': 20, 'rosita': 35}
# Doubled key values for edged images
KEY = {'line': 10, 'kumbayah': 20, 'star': 30, 'sleeves': 40, 'rosita': 70}
EXCLUDE = {}

class TestLines(unittest.TestCase):
    def setUp(self):
        self.tests = {}
        for i in KEY:
            if i not in EXCLUDE:
                self.tests[i] = StaffLines(i)

    def test_counts(self):
        for k, v in self.tests.items():
            with self.subTest(i=k):
                counts = {len(i) for i in v.line_data.values()}
                self.assertIn(KEY[k], counts)

    def test_common_param(self):
        sets = []
        # Gather sets of all params that detect the proper number of lines
        for k, v in self.tests.items():
            temp = set(v.get_params(KEY[k]))
            sets.append(temp)
            print(f'{k}: {len(temp)}\n')
        params = set.intersection(*sets)
        print(f'Common: {len(params)}\n{params}')
        self.assertGreaterEqual(len(params), 1)


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
    unittest.main()
