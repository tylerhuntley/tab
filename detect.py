'''
This file concerns the isolation of abstract musical information from the
standard nomenclature of printed sheet music.
'''

import cv2
import numpy as np
import matplotlib.pyplot as plt
from time import time
import itertools
import pickle
import os

CWD = os.getcwd()


class Detector():
    image_path = 'static/'
    data_path = 'data/'

    def load_data(self):
        return np.load(os.path.join(CWD, self.data_path, self.name))

    def save_data(self):
        path = os.path.join(CWD, self.data_path)
        if not os.path.exists(path):
            os.makedirs(path)  # Ensure directory exists
        with open(os.path.join(path, self.name), 'wb') as f:
            pickle.dump(self.line_data, f)

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

    def draw_lines(self, img, lines, color=(255, 0, 0)):
        ''' Draw lines on img in color, default red'''
        for line in lines:
            (x1, y1, x2, y2) = line
            cv2.line(img, (x1, y1), (x2, y2), color, 2)

    def draw_box(self, img, points, color=(255,0,0)):
        ''' Draw a rectangle on img, default color red
        points is the coordinates of opposite corners: (x0, y0, x1, y1)'''
        lines = []
        x0, y0, x1, y1 = points
        lines.append((x0, y0, x1, y0))
        lines.append((x1, y0, x1, y1))
        lines.append((x1, y1, x0, y1))
        lines.append((x0, y1, x0, y0))
        self.draw_lines(img, lines, color)

    @staticmethod
    def plot(img, gray=False):
        ''' Display image in a matplotlib plot window'''
        plt.plot()
        if gray:
            plt.imshow(img, 'gray')
        else:
            plt.imshow(img)
        plt.show()


class StaffDetector(Detector):
    def __init__(self, name, TEST=False):
        # Pre-process image
        self.name = name
        if TEST:
            self.image_name = os.path.join(self.image_path, f'{name}.png')
        else:
            self.image_name = f'{name}.png'
        self.image = cv2.imread(self.image_name)
        self.gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        self.edges = self.detect_edges(self.gray)

        self.line_data ={}
        if TEST:
            # Load data, if available
            try:
                self.line_data = self.load_data()
            # Generate data, if needed
            except FileNotFoundError:
                self.line_data = {}
                self.probe_range()  # Default range for baseline data
                self.save_data()

        # This part will need to choose parameters on its own
        self.staff_boxes = []
        self.staff_views = []
        self.probe_image(190, 95)
        lines = self.line_data[(190, 95)]  # Common param taken from testing
        for staff in self.group_staffs(lines):
            box = self.get_bounding_box(staff)
            self.staff_boxes.append(box)

        self.small_boxes = self.staff_boxes[:]  # For debug purposes
        self.expand_staff_boxes()
        for box in self.staff_boxes:
            view = self.slice_staff(box)
            self.staff_views.append(view)

#        self.staff_subplots()
        self.draw_boxes()

    def __repr__(self):
        return f"StaffDetector('{self.name}')"

    def staff_subplots(self):
        ''' Display staffs in subplots of one plt.figure (bit awkward) '''
        fig = plt.figure()
        fig.suptitle(self.name, fontsize=20)
        for i, view in enumerate(self.staff_views):
            fig.add_subplot(len(self.staff_views), 1, i+1)
            plt.title(f'Staff #{i+1}', loc='left')
            plt.axis('off')
            plt.imshow(view)
        fig.show()

    def draw_boxes(self):
        ''' Highlight detected staffs with red borders (much cleaner)
        small_boxes: as initially detected, staff_boxes: after expansion '''
        fig = plt.figure()
        fig.suptitle(f'Staffs detected in {self.name}.png', fontsize=20)
        img = self.image.copy()
        for a, b in zip(self.small_boxes, self.staff_boxes):
            self.draw_box(img, a)
            self.draw_box(img, b, color=(0, 255, 0))
        plt.imshow(img)
        fig.show()

    def probe_image(self, param, max_gap):
        ''' Add a parameter set and its associated lines to image dataset '''
        min_length = int(self.image.shape[1] * 0.5)
        # Don't repeat detection with duplicate parameters
        if (param, max_gap) not in self.line_data:
            lines = self.detect_lines(self.edges, param, min_length, max_gap)
            lines = self.filter_lines(lines)
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

    def filter_lines(self, lines):
        temp = []
        if lines is None: return ()
        for line in lines.tolist():
            x1, y1, x2, y2 = line[0]
            try:
                slope = abs((y2 - y1) / (x2 - x1))
                if slope < 0.01:
                    temp.append(line[0])
            except ZeroDivisionError:
                continue
        temp.sort(key=lambda x: x[1])
        # Remove duplicates
        for a, b in zip(temp[:-1], temp[1:]):
            if abs(a[1] - b[1]) < 5:
                temp.remove(b)
        return tuple(temp)

    def group_staffs(self, lines, count=5):
        ''' Return list of lists containing the lines of each staff entity
        Currently just counts out groups of a pre-determined size.
        Will probably want to use dynamic grouping of some kind, KNN?'''
        staffs = []
        sorted_lines = sorted(lines, key=lambda x: x[1])  # Sort by y1
        for i in range(0, len(lines), count):
            staffs.append(sorted_lines[i:i + count])
        return staffs

    def get_bounding_box(self, array_lines):
        ''' Return corner coordinates of rectangle surrounding given lines
        lines is a list of 4-tuples of the form (x1, y1, x2, y2)
        Currently ignores everything outside the stafflines themselves
        Will need to expand to account for ledger lines'''
        lines = [line for line in array_lines]  # np.arrays come nested
        min_x = min(min(line[0], line[2]) for line in lines)
        max_x = max(max(line[0], line[2]) for line in lines)
        min_y = min(min(line[1], line[3]) for line in lines)
        max_y = max(max(line[1], line[3]) for line in lines)
        return (min_x, min_y, max_x, max_y)

    def expand_staff_boxes(self):
        ''' Stretch adajcent staff boxes together to capture ledger lines '''
        # Single staffs need to be expanded blindly. Can maybe improve this.
        if len(self.staff_boxes) == 1:
            x1, y1, x2, y2 = self.staff_boxes[0]
            self.staff_boxes = [(x1, y1 - (y2 - y1), x2, y2 + (y2 - y1))]
            return

        # Multiple staffs are made contiguous, to avoid gaps in coverage
        temp = [list(i) for i in self.staff_boxes]
        for top, bot in zip(temp[:-1], temp[1:]):
            mid = int((top[3] + bot[1]) / 2)  # Bring midlines together
            top[3] = mid
            bot[1] = mid
        # Move neigborless top/bottom limits equivalent symmetrical amounts
        temp[0][1] -= temp[0][3] - self.staff_boxes[0][3]
        temp[-1][3] += self.staff_boxes[-1][1] - temp[-1][1]
        self.staff_boxes = [tuple(i) for i in temp]

    def slice_staff(self, corners):
        ''' Return image subarray bounded by given coordinates'''
        (min_x, min_y, max_x, max_y) = corners
        return self.image[min_y:max_y, min_x:max_x]

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


if __name__ == '__main__':
    detectors = []
    for filename in os.listdir():
        if filename[-4:] == '.png':  # There is a better way to do this
            detectors.append(StaffDetector(filename[:-4]))
