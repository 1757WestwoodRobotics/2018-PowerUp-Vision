from westwood_vision_tools import *
import numpy
from publish_data import *

##################################################################################################################
# given an object list of what is supposed to be boxes, this checks the list and removes objects
# from the list that are not likely to be boxes

def check_box_object_list(list_in):

    list_out=copy.copy(list_in)

    index=0
    while index<len(list_out):

        # the box is square and should have an aspect ratio near 1
        if (list_out[index].aspect_ratio() < 0.75):
            list_out.pop(index)
        elif (list_out[index].aspect_ratio() >1.25):
            list_out.pop(index)
        elif (list_out[index].relative_area()<0.00015):
            list_out.pop(index)
        else:
            index+=1

    return list_out

######################################################################################################################
# this attempts to figure out the distance to the box in meters based on how much of the relative area it consumes,
# this is is very dependent on the camera being used

def distance_to_box_meters(box_object_info):

    area=box_object_info.relative_area()
    distance_meters=0.429*numpy.power(area,-0.443)

    return distance_meters

######################################################################################################################

def report_box_info_to_jetson(box_info):

    x, y = box_info.normalized_center()
    alt, azimuth = altAzi(x, y, 22.5, 23)
    area = box_info.relative_area()
    aspect_ratio = box_info.aspect_ratio()
    distance = distance_to_box_meters(box_info)

    publish_network_value("altitude", alt)
    publish_network_value("azimuth",  azimuth)
    publish_network_value("distance, m",  distance)


######################################################################################################################

#init_network_tables()

picture = take_picture(False, 1)
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

        tar2 = 1.45 * color[0] + 48.4
        tar3 = 1.31 * color[0] + 59.6
        if abs(color[1] - tar2) < 50 and abs(color[2] - tar3) < 50:
            mask[row, col] = 255


#show_picture("first",picture,5000)

#low=  numpy.array([255, 255,255])
#high= numpy.array([255, 255,255])
#mask = cv2.inRange(picture, low, high)

mask=remove_chatter(mask,10)
mask=remove_spurious_falses(mask,3)

#show_picture("post chatter",mask,5000)

object_list = find_objects(mask, 5, True)

# remove items from the list that are probably just noise or not boxes
object_list=check_box_object_list(object_list)


objects_list = sort_object_info_list(object_list, 0)



for i in object_list:
    #row, col = i.center
    #x, y = centerCoordinates(mask, row, col)
    x, y = i.normalized_center()
    alt, azimuth = altAzi(x,y,22.5,23)
    area= i.relative_area()
    aspect_ratio = i.aspect_ratio()
    distance=distance_to_box_meters(i)
    report_box_info_to_jetson(i)
    print ("Alt: ", round(alt,2), "Azimuth: ", round(azimuth,2), "Relative Area: ", round(area,4), "Aspect Ratio: ", round(aspect_ratio,2), "Perimeter: ", i.perimeter, "Distance, m: ", round(distance,3))



#