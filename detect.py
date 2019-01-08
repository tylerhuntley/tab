'''
This file concerns the isolation of abstract musical information from the
standard nomenclature of printed sheet music.
'''

import cv2
import numpy as np
import matplotlib.pyplot as plt
import itertools as it
import os

CWD = os.getcwd()


class Controller():
    def __init__(self, name, TEST=False):
        self.name = name
        if TEST:
            self.image_name = os.path.join('static', f'{name}.png')
        else:
            self.image_name = f'{name}.png'
        self.main = StaffDetector(self.image_name)

        self.copy = np.copy(self.main.image)
#        self.show_lines(self.copy)
        self.show_boxes(self.copy)
        self.show_notes(self.copy)
        self.plot(self.copy)

    def show_lines(self, img, color=(255, 0, 0)):
        for line in self.main.lines:
            (x1, y1, x2, y2) = line
            cv2.line(img, (x1, y1), (x2, y2), color, 3)

    def show_boxes(self, img):
        ''' Highlight detected staffs with red borders (much cleaner)
        small_boxes: as initially detected, staff_boxes: after expansion '''
        for a, b in zip(self.main.small_boxes, self.main.large_boxes):
            box_a = (a[:2], a[2:])
            box_b = (b[:2], b[2:])
            cv2.rectangle(img, *box_b, (0, 255, 0))  # Green around large_boxes
            cv2.rectangle(img, *box_a, (255, 0, 0))  # Red around small_boxes

    def show_notes(self, img):
        for staff in self.main.staffs:
            H, W = staff.notes.shape[:2]
            radius = staff.note_size
            for y, x in it.product(range(H), range(W)):
                if staff.notes[y, x]:
                    loc = np.add((x, y), staff.origin)
                    loc = tuple(np.add(loc, (int(staff.note_size/2),)*2))
                    cv2.circle(img, loc, radius, (0, 0, 255))

    @staticmethod
    def detect_edges(img, sigma=0.33):
        mean = np.mean(img)
        lower = int(max(0, (1 - sigma) * mean))
        upper = int(min(255, (1 + sigma) * mean))
        return cv2.Canny(img, lower, upper)

    @staticmethod
    def plot(img, gray=False):
        ''' Display image in a matplotlib plot window'''
        fig = plt.figure()
        if gray:
            plt.imshow(img, 'gray')
        else:
            plt.imshow(img)
        fig.show()


class StaffDetector():
    def __init__(self, name):
        # Pre-process image
        self.name = name
        self.image = cv2.imread(name)
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

        # Store average size of staffs, for note fitting
        sizes = [abs(box[3] - box[1]) for box in self.small_boxes]
        self.staff_size = int(np.mean(sizes))

        # Move on to phase 2: note detection
        self.staffs = []
        for n, lines, box in zip(range(100), self.staff_lines, self.large_boxes):
            self.staffs.append(NoteDetector(self, n, lines, box))

    def __repr__(self):
        return f"StaffDetector('{self.name}')"

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


class NoteDetector():
    def __init__(self, parent, n, lines, box):
        self.parent = parent
        self.n = n
        self.lines = lines
        self.box = box
        self.origin = (min(box[0], box[2]), min(box[1], box[3]))  # (x, y)
        self.image = self.subarray(self.parent.image, box)
        self.gray = self.subarray(self.parent.gray, box)

        self.note_size = int(self.parent.staff_size / 4)
        q = cv2.imread('template/Q.png', cv2.IMREAD_GRAYSCALE)
        scale = self.note_size / q.shape[0]
        self.q = cv2.resize(q, None, fx=scale, fy=scale, )

        self.notes = self.find_notes()
        self.chord_groups = self.group_chords(self.notes)

    def find_notes(self):
        matches= cv2.matchTemplate(self.gray, self.q, cv2.TM_CCOEFF_NORMED)
        thresh = np.max(matches) * (1 - 1.5 * np.std(matches))
        return matches > thresh

    def group_chords(self, array):
        ''' Takes a boolean array representing presence of a note at [y, x]
        Returns a list of lists of note coordinates, [[(x,y), ...], ...],
        with each sublist group containing simultaneous notes, i.e. a chord '''
        # Extract coordinates from array
        notes = []
        for y, x in it.product(range(array.shape[0]), range(array.shape[1])):
            if array[y, x] and (x, y) not in notes:
                notes.append((x, y))
        if len(notes) == 0:
            return [[]]
        notes.sort()

        # Group points by x-proximity, indicating simultanaeity
        groups = []
        temp = [notes[0]]
        for note in notes[1:]:
            if abs(note[0] - temp[-1][0]) <= self.note_size:
                temp.append(note)
            else:
                groups.append(temp)
                temp = [note]
        groups.append(temp)
        return groups

    def subarray(self, image, corners):
        ''' Return image subarray bounded by box corners: (x0, y0, x1, y1)'''
        try: (x0, y0, x1, y1) = corners
        except ValueError: return
        return image[y0:y1, x0:x1]


if __name__ == '__main__':
    detectors = []
    for filename in os.listdir():
        if filename[-4:] == '.png':  # There is a better way to do this
            detectors.append(Controller(filename[:-4]))

    Controller.plot(detectors[0].main.staffs[0].notes)
