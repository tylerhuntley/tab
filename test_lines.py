import cv2
import numpy as np
import matplotlib.pyplot as plt
from time import time
import itertools
import pickle


def detect_edges(img, sigma=0.33):
    ''' '''
    mean = np.mean(img)
    lower = int(max(0, (1 - sigma) * mean))
    upper = int(min(255, (1 + sigma) * mean))
    return cv2.Canny(img, lower, upper)


def detect_lines(img, param, min_length, max_gap):
    ''' '''
    rho, theta = 1, np.pi/180  # distance and angle parameters for accumulator
    lines = cv2.HoughLinesP(img, rho, theta, param, min_length, max_gap)
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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)      
        
        # Image file info
        self.path = 'static/'
        self.images = ('line', 'easy', 'hard')
        self.image_names = tuple(f'{self.path}{i}.png' for i in self.images)
        
        # Load image files
        self.image_data = {}
        for image, name in zip(self.images, self.image_names):
            self.image_data[image] = cv2.imread(name)

        # Load data, if available
        try:
            self.line_data = np.load('data')
        # Generate data, if needed
        except FileNotFoundError:
            self.line_data = {}
            for image, name in zip(self.images, self.image_names):
                if not self.line_data[image]:
                    self.line_data[image] = self.probe_image(name)
            with open('data', 'wb') as f:
                pickle.dump(self.line_data, f)                


    def probe_image(self, filename):
        data = {}
        # Prepare color-inverted, grayscale array of image data
        image = cv2.imread(filename)
        if image is None:
            print(f'{filename} not found')
            return None
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        inverted = np.invert(gray)
        
        # For timing purposes
        count = 0
        start = time()
        last = start
        
        # Parameter initialization
        min_length = image.shape[1] * 0.5
        params = range(0, 200, 10)
        gaps = range(0, 100, 5)
        cycles = len(params) * len(gaps)
        
        for (param, gap) in itertools.product(params, gaps):
            lines = detect_lines(inverted, param, min_length, gap)
            data[(param, gap)] = lines
            
            # Timing info
            count += 1
            now = time()
            print('Cycle {} of {}: {:.2f} us, Total: {:.2f} s'.format(
                    count, cycles, (now - last)*1000, now - start))
            last = now
        
        return data
    

if __name__ == '__main__':
    
    d = Detector()
