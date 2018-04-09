import cv2
import numpy as np
import matplotlib.pyplot as plt
from time import time
import itertools
import pickle
import unittest


def detect_edges(img, sigma=0.33):
    ''' '''
    mean = np.mean(img)
    lower = int(max(0, (1 - sigma) * mean))
    upper = int(min(255, (1 + sigma) * mean))
    return cv2.Canny(img, lower, upper)


def detect_lines(img, param, min_length, max_gap):
    ''' '''
#    rho, theta = 1, np.pi/180  # distance and angle parameters for accumulator
    lines = cv2.HoughLinesP(img, rho=1, theta=np.pi/180, threshold=param,
                            minLineLength=min_length, maxLineGap=max_gap)
    return lines


def separate_staffs(lines):
    ''' Return list of lists containing the lines of each staff entity
    Currently just counts five lines at a time, should utilize numpy'''
    staffs = []
    for i in range(0, len(lines), 5):
        staffs.append(lines[i:i + 5])
    return staffs


def slice_staff():
    ''' Return image subarray comprising one staff line'''
    pass



def draw_lines(img, lines, color=(255, 0, 0)):
    ''' Return img with lines drawn on it in color, default red'''
    result = img.copy()
    for line in lines:
        for x1, y1, x2, y2 in line:
            cv2.line(result, (x1, y1), (x2, y2), color, 1)
    return result


def plot(img, gray=False):
    ''' Display img in a matplotlib plot window'''
    plt.plot()
    if gray:
        plt.imshow(img, 'gray')
    else:
        plt.imshow(img)
    plt.show()


def length(line):
    for x1, y1, x2, y2 in line:
        return ((x2 - x1)**2 + (y2 - y1)**2)**0.5


class Detector():
    key = {'line': 5, 'kumbayah': 10, 'star': 15, 'sleeves': 20, 'rosita': 40}
    image_path = 'static/'
    data_path = 'data/'

    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Image info
        self.name = name
        self.image_name = f'{self.image_path}{name}.png'
        self.image = cv2.imread(self.image_name)
        self.gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        self.inverted = np.invert(self.gray)

        # Load data, if available
        try:
            self.load_data()
        # Generate data, if needed
        except FileNotFoundError:
            self.line_data = {}
            self.probe_image()
            self.save_data()


    def load_data(self):
        self.line_data = np.load(f'{self.data_path}{self.name}')


    def save_data(self):
        with open(f'{self.data_path}{self.name}', 'wb') as f:
            pickle.dump(self.line_data, f)


    def probe_image(self, params=range(0, 200, 10), gaps=range(0, 100, 5)):
        # For timing purposes
        count = 0
        start = time()
        last = start

        # Detect lines using different combinations of parameters
        min_length = int(self.image.shape[1] * 0.5)
        cycles = len(params) * len(gaps)
        for (param, max_gap) in itertools.product(params, gaps):
            # Don't repeat detection with duplicate parameters
            if (param, max_gap) in self.line_data:
                continue
            lines = detect_lines(self.inverted, param, min_length, max_gap)
            self.line_data[(param, max_gap)] = lines

            # Timing info
            count += 1
            now = time()
            print('{}, cycle {} of {}: {:.2f} us, Total: {:.2f} s'.format(
                    self.name, count, cycles, (now - last)*1000, now - start))
            last = now


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


class TestLines(unittest.TestCase):
    def setUp(self):
        self.tests = {}
        for i in Detector.key:
            self.tests[i] = Detector(i)

    def test_counts(self):
        for k, v in self.tests.items():
            with self.subTest(i=k):
                counts = [len(i) for i in v.line_data.values() if i is not None]
                self.assertIn(v.key[k], counts)


if __name__ == '__main__':

    unittest.main()
