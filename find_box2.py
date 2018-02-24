import cv2
import numpy as np

# uncomment when using a camera
#camera = cv2.VideoCapture(0)

headless = False
while True:

    # use this line to load in an image
    img = cv2.imread("/Users/Larry/Desktop/DSC00293000.JPG", 1)
    if not headless:
        cv2.imshow("Raw", img)
    # use this line to capture from camera
    # retval, img = camera.read()

    # threshold the image based on RGV values (BGR)
    threshold = cv2.inRange(img, (0, 100, 150), (100, 255, 255))
    if not headless:
        cv2.imshow("Threshold", threshold)

    # erode and dilate to reduce noise
    kernel = np.ones((5, 5), np.uint8)
    erode = cv2.erode(threshold, kernel, iterations=3)
    dilate = cv2.dilate(erode, kernel, iterations=2)
    if not headless:
        cv2.imshow("Processed", dilate)

    # find the contours - regions of white - in the image
    im2, contours, hierarchy = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    good_centers = []
    for contour in contours:
        # check the contour area, if it is too small, throw it out
        area = cv2.contourArea(contour)
        if area < 500:
            continue

        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

        center = (x+(w/2), y+(h/2))
        cv2.circle(img, (int(x+w/2), int(y+h/2)), 4, (255, 255, 0), 2)

        good_centers.append(center)

    # do something with the centers

    if not headless:
        cv2.imshow("Contours", img)

    # add a waitkey so the rendered windows buffers
    cv2.waitKey(10)


Add Comment