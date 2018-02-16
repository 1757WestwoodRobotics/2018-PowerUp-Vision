from cv2 import *
import time
import os

test=0

#stream = VideoCapture("gst-launch-1.0 v4l2src ! video/x-raw-yuv,width=640,height=480,framerate=15/1 ! aspectratiocrop aspect-ratio=4/3 ! ffmpegcolorspace ! videoconvert ! video/x-raw, format=(string)BGR ! appsink")

stream = VideoCapture("gst-launch-1.0 v4l2src ! image/jpeg,width=640,height=480 ! appsink name=appsink")

#stream = VideoCapture(0)

if (stream.isOpened() == False):
	print("Error with stream!")

# Define the codec and create VideoWriter object.The output is stored in 'outpy.avi' file.
# Define the fps to be equal to 10. Also frame size is passed.

# out = VideoWriter(epochtime + '.jpg', VideoWriter_fourcc('M','J','P','G'), 30, (640,720))

while(stream.isOpened()):
	ret, frame = stream.read()

	if (ret == True):
		#imshow("Frame", frame)
		#res = resize(frame, None, fx=.5, fy=2/3, interpolation = INTER_CUBIC)
		imwrite('./out2/' + str(test) + '.jpg', frame)
		# if (waitKey(25) == 'q'):
		#	break
		test += 1
	else:
		break


'''
ret, pic = stream.read()

if useless=="True":
    imshow("taking pic", pic)
'''

stream.release()
