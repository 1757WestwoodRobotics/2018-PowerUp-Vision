from westwood_vision_tools import *
import numpy
#from publish_data import *

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
        elif (list_out[index].relative_area()<0.00015): # require a minimum size
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

def search_for_boxes(picture_in):

    picture_out=copy.copy(picture_in)

    #if this is too slow, make the picture smaller
    #picture_out=cv2.resize(picture_out, (0,0), fx=0.5, fy=0.5)

    #hsv = cv2.cvtColor(picture, cv2.COLOR_BGR2HSV)

    picture_out=cv2.bilateralFilter(picture_out,10,150,150)
    #hsv=cv2.bilateralFilter(hsv,10,150,150)
    #show_picture("original",picture,2000)
    #show_picture("hsv",hsv,2000)

    rows, cols, layers = picture_out.shape

    #create an intial mask where evertying is false
    mask=numpy.zeros((rows,cols),numpy.uint8)

    #check each pixel and determine if it's color profile is that of a box
    for row in range (0, rows-1, 1):
        for col in range (0, cols-1, 1):
            color=picture_out[row,col]

            # if the value of the 1st component is within the expected range
            # then check the other two color components
            if ((color[0]>10) and (color[0]<80)):
                # given the value of the first color component, calculate what
                # the other two should be if this is a box
                tar2 = -.00229 * (color[0] ** 2) + 1.83 * color[0] + 34.2
                tar3 = -.00517 * (color[0] ** 2) + 2.2 * color[0] + 25.7
                if (abs(color[1] - tar2) < 25) and (abs(color[2] - tar3) < 25):
                    mask[row, col] = 255


    #show_picture("first",picture,5000)

    #low=  numpy.array([255, 255,255])
    #high= numpy.array([255, 255,255])
    #mask = cv2.inRange(picture, low, high)

    mask=remove_chatter(mask,10)
    mask=remove_spurious_falses(mask,10)

    #show_picture("post chatter",mask,5000)

    object_list = find_objects(mask, 3, True)

    # remove items from the list that are probably just noise or not boxes
    object_list=check_box_object_list(object_list)

    objects_list = sort_object_info_list(object_list, 0)


    for i in object_list:
        x, y = i.normalized_center()
        alt, azimuth = altAzi(x,y,22.5,23)
        area= i.relative_area()
        aspect_ratio = i.aspect_ratio()
        distance=distance_to_box_meters(i)
        #  report_box_info_to_jetson(i)

        abs_col=int(i.relative_center_col()*cols)
        abs_row=int(i.relative_center_row()*rows)
        if (i.relative_width()>i.relative_height()):
            radius=int(i.relative_width()*cols/2)
        else:
            radius=int(i.relative_height()*rows/2)
        cv2.circle(picture_out, (abs_col, abs_row), radius, (0, 0, 255), 1)

        height=i.relative_height()*rows
        min_row=int(i.relative_center_row()*rows-height/2)
        max_row=int(i.relative_center_row()*rows+height/2)
        width=i.relative_width()*cols
        min_col=int(i.relative_center_col()*cols-width/2)
        max_col=int(i.relative_center_col()*cols+width/2)
        cv2.rectangle(picture_out, (min_col, min_row), (max_col, max_row), (0, 0, 255), 2)

        print ("Alt: ", round(alt,2), "Azimuth: ", round(azimuth,2), "Relative Area: ", round(area,4), "Aspect Ratio: ", round(aspect_ratio,2), "Perimeter: ", i.perimeter, "Distance, m: ", round(distance,3))


    return picture_out




###################################################################################################

picture = take_picture(False, 1)
searched=search_for_boxes(picture)
show_picture("processed",searched,10000)