import unittest
import tab


class TestBlankBars(unittest.TestCase):
    def setUp(self):
        self.bar = tab.Bar()
        self.staff = tab.Staff()
        self.tabs = tab.Tab()

    def test_bar(self):
#        print('Bar:\n' + str(self.bar))
        self.assertEqual(str(self.bar), f"|{' ' * 32}|\n" * 6)

    def test_null_staff(self):
        self.assertEqual(str(self.staff), '\n')

    def test_blank_staff(self):
        """ Test 1-8 empty bars on a single, long staffline. """
        LINE = f"|{'-' * 32}"
        for i in range(1, 9):
            with self.subTest(i=i):
                STAFF = (LINE  * i + '|\n') * 6
                self.staff.add_bar(self.bar)
                self.assertEquals(str(self.staff), STAFF)

    def test_blank_tab(self):
        """ Assumes a 2 bar limit for page width.
        Will want to allow more flexibility. """
        self.maxDiff = None  # Display full-length failure info
        LINE = f"|{'-' * 32}"
        ONE_BAR = (LINE + '|\n') * 6 + '\n'
        TWO_BAR = (LINE * 2 + '|\n') * 6 + '\n'
        for i in range(1, 9):
            with self.subTest(i=i):
                TAB = TWO_BAR * (i // 2) + ONE_BAR * (i % 2)
                self.tabs.add_bar(self.bar)
                self.assertEqual(str(self.tabs), TAB)


if __name__ == '__main__':
    unittest.main()
