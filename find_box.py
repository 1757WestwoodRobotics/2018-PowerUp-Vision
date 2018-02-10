from westwood_vision_tools import *
import numpy

picture = take_picture(True, 1)
hsv = cv2.cvtColor(picture, cv2.COLOR_BGR2HSV)

#picture=cv2.bilateralFilter(picture,10,150,150)
hsv=cv2.bilateralFilter(hsv,10,150,150)
picture=cv2.bilateralFilter(picture,10,150,150)
#show_picture("original",picture,2000)
#show_picture("hsv",hsv,2000)
#picture=hsv

rows, cols, layers = picture.shape

#create an intial mask where evertying is false
mask=numpy.zeros((rows,cols),numpy.uint8)

for row in range (0, rows-1, 1):
    for col in range (0, cols-1, 1):
        color=picture[row,col]
        target_ratio=[]

        if (color[1]>20 and color[1]<60):
            target_ratio = numpy.array([2.56, 2.41])
        elif (color[1]>=60 and color[1]<120):
            target_ratio=numpy.array([2.0, 1.8])

        if len(target_ratio)>0:
            pixel_ratio=numpy.array([(float(1.0*color[1]/color[0])), float((1.0*color[2]/color[0]))])
            distance=euclidian_distance(target_ratio, pixel_ratio)
            if (abs(distance<1)):
                mask[row,col]=255


show_picture("first",hsv,5000)
# trying to find the box
low_box=  numpy.array([20, 115,160])
high_box= numpy.array([40, 165,225])
mask_box = cv2.inRange(hsv, low_box, high_box)
show_picture("box mask", mask_box,5000)

# trying to find the zipper
#low_zip=  numpy.array([140, 170, 150])
#high_zip= numpy.array([215, 220, 195])
#mask_zip_picture = cv2.inRange(picture, low_zip, high_zip)
#show_picture("zipper mask",mask_zip_picture,5000)

#low_zip=  numpy.array([55, 20, 210])
#high_zip= numpy.array([110, 45, 240])
#mask_zip_hsv = cv2.inRange(hsv, low_zip, high_zip)

#show_picture("zipper mask hsv",mask_zip_hsv,5000)

#mask_zip=cv2.bitwise_and(mask_zip_hsv,mask_zip_picture)
#show_picture("total zipper mask",mask_zip,5000)

#mask=cv2.bitwise_or(mask_zip, mask_box)
#show_picture("total mask",mask,5000)

mask=mask_box
mask=remove_chatter(mask,3)
mask=remove_spurious_falses(mask,3)
show_picture("total mask",mask,5000)

mask=cv2.resize(mask,(0,0), fx=0.5,fy=0.5)

show_picture("small mask",mask,5000)

objects_list = find_objects(mask, 5)
objects_list = sort_object_info_list(objects_list, 0)

for i in objects_list:
    row, col = i.center_RC
 #   x, y = centerCoordinates(mask, row, col)
 #   x, y = normalizeCoordinatesI(mask, x, y)
    x,y = i.normalized_center()
    alt, azimuth = altAzi(x,y,22.5,23)
    area= i.area()
    aspect_ratio = i.aspect_ratio()
    print ("Alt: ", round(alt,2), "Azimuth: ", round(azimuth,2), "Area: ", area, "Aspect Ratio: ", round(aspect_ratio,2), "Perimeter: ", i.perimeter)

