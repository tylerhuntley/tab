'''
This file concerns the isolation of abstract musical information from the
standard nomenclature of printed sheet music.
'''

import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

CWD = os.getcwd()


class Detector():
    image_path = 'static/'
    data_path = 'data/'

    @staticmethod
    def detect_edges(img, sigma=0.33):
        mean = np.mean(img)
        lower = int(max(0, (1 - sigma) * mean))
        upper = int(min(255, (1 + sigma) * mean))
        return cv2.Canny(img, lower, upper)

    def draw_lines(self, img, lines, color=(255, 0, 0)):
        ''' Draw lines on img in color, default red'''
        for line in lines:
            (x1, y1, x2, y2) = line
            cv2.line(img, (x1, y1), (x2, y2), color, 2)

    def draw_box(self, img, points, color=(255,0,0)):
        ''' Draw a rectangle on img, default color red
        points is the coordinates of opposite corners: (x0, y0, x1, y1)'''
        lines = []
        try: x0, y0, x1, y1 = points
        except ValueError: return
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
        self.edges = cv2.Sobel(self.gray, ddepth=cv2.CV_8U, dx=0, dy=1, ksize=3)

        # Detect stafflines
        self.small_boxes = []
        self.staff_lines = []
        self.lines = self.hough_lines(self.edges)
        for staff in self.group_staffs(self.lines):
            self.staff_lines.append(staff)
            box = self.get_bounding_box(staff)
            self.small_boxes.append(box)
        self.large_boxes = self.expand_boxes(self.small_boxes)

        self.show_boxes()
#        self.show_lines()

    def __repr__(self):
        return f"StaffDetector('{self.name}')"

    def show_boxes(self):
        ''' Highlight detected staffs with red borders (much cleaner)
        small_boxes: as initially detected, staff_boxes: after expansion '''
        fig = plt.figure()
        fig.suptitle(f'Staffs detected in {self.name}.png', fontsize=20)
        img = self.image.copy()
        for a, b in zip(self.small_boxes, self.large_boxes):
            self.draw_box(img, b, color=(0, 255, 0))
            self.draw_box(img, a)
        plt.imshow(img)
        fig.show()

    def show_lines(self):
        fig = plt.figure()
        fig.suptitle(f'Lines detected in {self.name}.png', fontsize=20)
        img = self.image.copy()
        self.draw_lines(img, self.lines)
        plt.imshow(img)
        fig.show()

    def hough_lines(self, image):
        ''' Detect lines in image using the probabilistic Hough transform '''
        hough = cv2.HoughLinesP(image, rho=1, theta=np.pi/360, threshold=400,
                               minLineLength=int(self.image.shape[1] * 0.6),
                               maxLineGap=int(self.image.shape[1] / 12))
        return self.filter_lines(hough)

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

    def group_staffs(self, lines):
        ''' Return list of lists containing the lines of each staff entity
        Enforces a maximum of double the median line distance within groups'''
        if len(lines) == 0: return [[]]
        lines = sorted(lines, key=lambda x: (x[1]+x[3])/2)
        # Measure line spacing (from the center) and determine threshold
        spacing = []
        for a, b in zip(lines[:-1], lines[1:]):
            spacing.append(int((b[1]+b[3])/2 - (a[1]+a[3])/2))
        thresh = 2 * np.median(spacing)
        # Start new group when spacing gets too large
        staffs = []
        temp = [lines[0]]
        for line, dist in zip(lines[1:], spacing):
            if dist < thresh:
                temp.append(line)
            else:
                staffs.append(temp[:])
                temp = [line]
        staffs.append(temp)
        return staffs

    def get_bounding_box(self, lines):
        ''' Return corner coordinates of rectangle surrounding given lines
        lines is a list of 4-tuples of the form (x1, y1, x2, y2)
        Currently ignores everything outside the stafflines themselves
        Will need to expand to account for ledger lines'''
        try:
            min_x = min(min(line[0], line[2]) for line in lines)
            max_x = max(max(line[0], line[2]) for line in lines)
            min_y = min(min(line[1], line[3]) for line in lines)
            max_y = max(max(line[1], line[3]) for line in lines)
            return (min_x, min_y, max_x, max_y)
        except ValueError:
            return ()

    def expand_boxes(self, boxes):
        ''' Stretch adajcent staff boxes together to capture ledger lines
        Return list of new expanded bounding box coordinates'''
        # Single staffs need to be expanded blindly. Can maybe improve this.
        if len(boxes) == 1:
            try:
                x1, y1, x2, y2 = boxes[0]
                return [(x1, y1 - (y2 - y1), x2, y2 + (y2 - y1))]
            except ValueError:
                return [()]
        # Multiple staffs are made contiguous, to avoid gaps in coverage
        temp = [list(i) for i in boxes]
        for top, bot in zip(temp[:-1], temp[1:]):
            mid = int((top[3] + bot[1]) / 2)  # Bring midlines together
            top[3] = mid
            bot[1] = mid
        # Move neigborless top/bottom limits equivalent symmetrical amounts
        temp[0][1] -= temp[0][3] - boxes[0][3]
        temp[-1][3] += boxes[-1][1] - temp[-1][1]
        return [tuple(i) for i in temp]

    def slice_staff(self, corners):
        ''' Return image subarray bounded by given coordinates'''
        (min_x, min_y, max_x, max_y) = corners
        return self.image[min_y:max_y, min_x:max_x]


if __name__ == '__main__':
    detectors = []
    for filename in os.listdir():
        if filename[-4:] == '.png':  # There is a better way to do this
            detectors.append(StaffDetector(filename[:-4]))
