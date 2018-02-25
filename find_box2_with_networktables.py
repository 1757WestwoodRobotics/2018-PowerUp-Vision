import cv2
import numpy as np
from networktables import NetworkTables
#from publish_data import *


#### Camera settings on the lab PC:
#brightness 30; contrast 10; saturation 200; sharpness 50, white balance auto; exposure -7;



# uncomment when using a camera
camera = cv2.VideoCapture(1)
camera.set(cv2.CAP_PROP_SETTINGS, 1) #to fix things

#init_network_tables()


headless = False
while True:

    # use this line to load in an image
    #img = cv2.imread("/Users/Larry/Desktop/DSC00293000.JPG", 1)
    #if not headless:
    #    cv2.imshow("Raw", img)
    # use this line to capture from camera
    retval, img = camera.read()

    # threshold the image based on RGV values (BGR)
    threshold_image = cv2.inRange(img, (0, 100, 150), (100, 255, 255))
    if not headless:
        cv2.imshow("Threshold", threshold_image)

    # erode and dilate to reduce noise
    kernel = np.ones((5, 5), np.uint8)
    erode = cv2.erode(threshold_image, kernel, iterations=3)
    dilate = cv2.dilate(erode, kernel, iterations=2)
    if not headless:
        cv2.imshow("Processed", dilate)

    # find the contours - regions of white - in the image
    im2, contours, hierarchy = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    good_centers = []
    coordx = [0]
    coordy = [0]
    for contour in contours:
        # check the contour area, if it is too small, throw it out
        area = cv2.contourArea(contour)
        if area < 700:
            continue

        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

        center = (x+(w/2), y+(h/2))
        xx = center[0]
        yy = center[1]
        cv2.circle(img, (int(x+w/2), int(y+h/2)), 4, (255, 255, 0), 2)

        good_centers.append(center)
        coordx.append(xx)
        coordy.append(yy)

    # do something with the centers

    if not headless:
        cv2.imshow("Contours", img)

    centers = good_centers
    #publish_network_value('x', coordx)
    #publish_network_value('y', coordy)
    #print('center:', read_network_value('x'), read_network_value('y'))

    # add a waitkey so the rendered windows buffers
    cv2.waitKey(10)

