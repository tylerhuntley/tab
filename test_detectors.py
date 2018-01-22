import cv2
import numpy as np
import matplotlib.pyplot as plt


def canny(img, sigma=0.33):
    mean = np.mean(img)
    lower = int(max(0, (1 - sigma) * mean))
    upper = int(min(255, (1 + sigma) * mean))
    return cv2.Canny(img, lower, upper)


def plot_edges(filein):
    img = cv2.imread(filein, 0)
    edges = cv2.Canny(img, 100, 200)
    
    plt.subplot(121),plt.imshow(img, cmap = 'gray')
    plt.title('Original Image'), plt.xticks([]), plt.yticks([])
    plt.subplot(122),plt.imshow(edges, cmap = 'gray')
    plt.title('Edge Image'), plt.xticks([]), plt.yticks([])
    
    plt.show()


def hough_lines(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)    
    lines = cv2.HoughLines(edges, 1, np.pi/180, 100)
    
    for line in lines:
        for rho, theta in line:        
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a*rho
            y0 = b*rho
            x1 = int(x0 + 1000*(-b))
            y1 = int(y0 + 1000*(a))
            x2 = int(x0 - 1000*(-b))
            y2 = int(y0 - 1000*(a))   
            cv2.line(img, (x1,y1), (x2,y2), (255,0,0), 2)
            
    return img

    
def hough_lines_P(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    minLineLength = 100
    maxLineGap = 10
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength, maxLineGap)
    
    for line in lines:
        for x1, y1, x2, y2 in line:
            cv2.line(img, (x1,y1), (x2,y2), (255, 0, 0), 1)
    
    return img


def plot_lines(filein):
    orig_img = cv2.imread(filein)
    line_img = hough_lines(orig_img.copy())
    
    # place plots side-by-side if portrait, over-under if landscape
    if orig_img.shape[0] < orig_img.shape[1]:
        orient = (2, 1)
    else:
        orient = (1, 2)
        
    plt.subplot(*orient, 1), plt.imshow(orig_img, cmap='gray')
    plt.title('Original Image'), plt.xticks([]), plt.yticks([])
    plt.subplot(*orient, 2), plt.imshow(line_img, cmap = 'gray')
    plt.title('Lined Image'), plt.xticks([]), plt.yticks([])
    
    plt.show()
    
    
def plot_lines_P(filein):
    orig_img = cv2.imread(filein)
    line_img = hough_lines_P(orig_img.copy())
    
    # place plots side-by-side if portrait, over-under if landscape
    if orig_img.shape[0] < orig_img.shape[1]:
        orient = (2, 1)
    else:
        orient = (1, 2)
        
    plt.subplot(*orient, 1), plt.imshow(orig_img, cmap='gray')
    plt.title('Original Image'), plt.xticks([]), plt.yticks([])
    plt.subplot(*orient, 2), plt.imshow(line_img, cmap = 'gray')
    plt.title('Lined Image'), plt.xticks([]), plt.yticks([])
    
    plt.show()
    

def write_lines(filein, fileout):
    line_img = hough_lines(filein)
    cv2.imwrite(fileout, line_img)


def write_lines_P(filein, fileout):
    line_img = hough_lines_P(filein)
    cv2.imwrite(fileout, line_img)
    
def circles(filein):

    img = cv2.imread(filein, 0)
    img = cv2.medianBlur(img, 5)
    cimg = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    
    circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1, minDist=10,
                                param1=100, param2=30, minRadius=5, maxRadius=50)
    
    circles = np.uint16(np.around(circles))
    for i in circles[0,:]:
        # draw the outer circle
        cv2.circle(cimg, (i[0],i[1]), i[2], (255,0,0), 2)
        # draw the center of the circle
        cv2.circle(cimg, (i[0],i[1]), 2, (255,0,0), 1)
    
    plt.plot()
    plt.imshow(cimg, cmap = 'gray')
    plt.show()
#    cv2.waitKey(0)
#    cv2.destroyAllWindows()    