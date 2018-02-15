from cv2 import *
import time
import os

epochtime = str(time.time())
test=0

stream = VideoCapture("gst-launch-1.0 nvcamerasrc ! video/x-raw(memory:NVMM), width=(int)1280, height=(int)720, format=(string)I420, framerate=(fraction)24/1 ! nvvidconv flip-method=4 ! video/x-raw, format=(string)I420 ! videoconvert ! video/x-raw, format=(string)BGR ! appsink")

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
		res = resize(frame, None, fx=.5, fy=2/3, interpolation = INTER_CUBIC)
		imwrite('./out/' + str(test) + '.jpg', res)
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
out.release()
