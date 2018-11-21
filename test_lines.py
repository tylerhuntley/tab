import cv2
import numpy as np
import matplotlib.pyplot as plt
from time import time
import itertools
import pickle
import unittest


class Detector():
    key = {'line': 5, 'kumbayah': 10, 'star': 15, 'sleeves': 20, 'rosita': 35}
    exclude = {}
    image_path = 'static/'
    data_path = 'data/'

    def __init__(self, name):
        # Image info
        self.name = name
        self.image_name = f'{self.image_path}{name}.png'
        self.image = cv2.imread(self.image_name)
        self.gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        self.edges = self.detect_edges(self.gray)
        self.inverted = np.invert(self.gray)


    def load_data(self):
        self.line_data = np.load(f'{self.data_path}{self.name}')

    def save_data(self):
        with open(f'{self.data_path}{self.name}', 'wb') as f:
            pickle.dump(self.line_data, f)

    @staticmethod
    def length(line):
        (x1, y1, x2, y2) = line
        return ((x2 - x1)**2 + (y2 - y1)**2)**0.5

    @staticmethod
    def is_horizontal(line):
        (x1, y1, x2, y2) = line
        return y1 == y2

    @staticmethod
    def is_vertical(line):
        (x1, y1, x2, y2) = line
        return x1 == x2

    @staticmethod
    def detect_edges(img, sigma=0.33):
        mean = np.mean(img)
        lower = int(max(0, (1 - sigma) * mean))
        upper = int(min(255, (1 + sigma) * mean))
        return cv2.Canny(img, lower, upper)

    @staticmethod
    def detect_lines(img, param, min_length, max_gap):
        rho, theta = 1, np.pi/180
        return cv2.HoughLinesP(img, rho, theta, threshold=param,
                                minLineLength=min_length, maxLineGap=max_gap)

    @staticmethod
    def draw_lines(img, lines, color=(255, 0, 0)):
        ''' Return image with lines drawn on it in color, default red'''
        result = img.copy()
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(result, (x1, y1), (x2, y2), color, 1)
        return result

    @staticmethod
    def plot(img, gray=False):
        ''' Display image in a matplotlib plot window'''
        plt.plot()
        if gray:
            plt.imshow(img, 'gray')
        else:
            plt.imshow(img)
        plt.show()


class StaffLines(Detector):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Load data, if available
        try:
            self.load_data()
        # Generate data, if needed
        except FileNotFoundError:
            self.line_data = {}
            self.probe_range()  # Default range for baseline data
            self.save_data()


    def probe_image(self, param, max_gap):
        ''' Add a parameter set and its associated lines to image dataset '''
        min_length = int(self.image.shape[1] * 0.5)
        # Don't repeat detection with duplicate parameters
        if (param, max_gap) not in self.line_data:
            lines = self.detect_lines(self.edges, param, min_length, max_gap)
        # NoneType has no len(), so use empty tuples for 0 lines instead
        self.line_data[(param, max_gap)] = () if lines is None else lines


    def probe_range(self, params=range(0, 200, 10), gaps=range(0, 100, 5)):
        ''' Probe a range of detection parameters to help find correct lines'''
        # For timing purposes
        count = 0
        start = time()
        last = start

        # Total number of combinations to try
        cycles = len(params) * len(gaps)
        for (param, max_gap) in itertools.product(params, gaps):
            self.probe_image(param, max_gap)

            # Timing info
            count += 1
            now = time()
            print('{}, cycle {} of {}: {:.2f} us, Total: {:.2f} s'.format(
                    self.name, count, cycles, (now - last)*1000, now - start))
            last = now


    def separate_staffs(lines):
        ''' Return list of lists containing the lines of each staff entity
        Currently just counts five lines at a time, should utilize numpy'''
        staffs = []
        for i in range(0, len(lines), 5):
            staffs.append(lines[i:i + 5])
        return staffs


    def slice_staff(image, lines):
        ''' Return image subarray comprising one staff line
        lines is a list of 4-tuples of the form (x1, y1, x2, y2)
        Currently crops everything outside the stafflines themselves
        Will need to expand to account for ledger lines'''
        min_x = min(min(line[0], line[2]) for line in lines)
        max_x = max(max(line[0], line[2]) for line in lines)
        min_y = min(min(line[1], line[3]) for line in lines)
        max_y = max(max(line[1], line[3]) for line in lines)
        return image[min_y:max_y, min_x:max_x]


    def get_params(self, n):
        '''Return a list of the params that detect exactly n lines'''
        params = []
        for param, lines in self.line_data.items():
            if len(lines) == n:
                params.append(param)
        return params


    def get_closest_params(self, n):
        result = []
        # Count the number of lines detected by each set of params
        counts = [len(i) for i in self.line_data.values() if i is not None]
        counts.sort()
        # Return the n params that detect the lowest number of lines
        for k, v in self.line_data.items():
            if v is not None and len(v) in counts[:n]:
                result.append(k)
                print(f'{self.name}: {k} -> {len(v)}')
        return result


    def join_h_lines(self, lines):
        '''Accepts and returns a list of lines as 4-tuples (x1, y1, x2, y2)
        Combines all collinear horizontal lines, and discards the rest'''
        temp = {}  # Maps singular y values to 2-tuples of x values
        for line in lines:
            (x1, y1, x2, y2) = line
            if not self.is_horizontal(line):
                continue
            if y1 in temp:
                old = temp[y1]
                temp[y1] = ( min(x1, x2, *old), max(x1, x2, *old) )
            else:
                temp[y1] = (x1, x2)

        # Reformat into 4-tuples for return
        result = []
        for y, x in temp.items():
            result.append((x[0], y, x[1], y))
        return result


class TestLines(unittest.TestCase):
    def setUp(self):
        self.tests = {}
        for i in Detector.key:
            if i not in Detector.exclude:
                self.tests[i] = StaffLines(i)

    def test_counts(self):
        for k, v in self.tests.items():
            with self.subTest(i=k):
                counts = {len(i) for i in v.line_data.values()}
                self.assertIn(v.key[k], counts)

    def test_common_param(self):
        sets = []
        # Gather sets of all params that detect the proper number of lines
        for k, v in self.tests.items():
            temp = set(v.get_params(v.key[k] * 2))  # x2: one line, two edges
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
