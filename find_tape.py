from westwood_vision_tools import *
import numpy



picture = take_picture(True, 1)
#hsv = cv2.cvtColor(picture, cv2.COLOR_BGR2HSV)

picture=cv2.bilateralFilter(picture,10,150,150)
#hsv=cv2.bilateralFilter(hsv,10,150,150)
#show_picture("original",picture,2000)
#show_picture("hsv",hsv,2000)


rows, cols, layers = picture.shape

#create an intial mask where evertying is false
mask=numpy.zeros((rows,cols),numpy.uint8)

for row in range (0, rows-1, 1):
    for col in range (0, cols-1, 1):
        color=picture[row,col]
        #target_ratio=[]

        #if (color[1]>20 and color[1]<60):
         #   target_ratio = numpy.array([2.56, 2.41])
        #elif (color[1]>=60 and color[1]<120):
        #    target_ratio=numpy.array([2.0, 1.8])

        #if len(target_ratio)>0:
        #    pixel_ratio=numpy.array([(float(1.0*color[1]/color[0])), float((1.0*color[2]/color[0]))])
        #    distance=euclidian_distance(target_ratio, pixel_ratio)
        #    if (abs(distance<1)):
        #        mask[row,col]=255

        ##THESE DONT REALLY WORK
        tar2 = .0033 * (color[0] **2) + 0.223 *  color[0]  + 33.2
        tar3 = .00451 * (color[0] **2) + .149 * color[0] + 43.8
        if (abs(color[1] - tar2) < 30) and (abs(color[2] - tar3) < 30):
            mask[row, col] = 255


#show_picture("first",picture,5000)

#low=  numpy.array([20, 60,60])
#high= numpy.array([70, 100,100])
low=  numpy.array([255, 255,255])
high= numpy.array([255, 255,255])
#mask = cv2.inRange(picture, low, high)

mask=remove_chatter(mask,10)
mask=remove_spurious_falses(mask,3)

#show_picture("post chatter",mask,5000)

objects_list = find_objects(mask, 5)
objects_list = sort_object_info_list(objects_list, 0)

for i in objects_list:
    #row, col = i.center
    #x, y = centerCoordinates(mask, row, col)
    x, y = i.normalized_center()
    alt, azimuth = altAzi(x,y,22.5,23)
    area= i.relative_area()
    aspect_ratio = i.aspect_ratio()
    print ("Alt: ", round(alt,2), "Azimuth: ", round(azimuth,2), "Relative Area: ", round(area,3), "Aspect Ratio: ", round(aspect_ratio,2), "Perimeter: ", i.perimeter)




