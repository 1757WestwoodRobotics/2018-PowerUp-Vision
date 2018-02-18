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
        if (list_out[index].aspect_ratio() < 0.5):
            list_out.pop(index)
        elif (list_out[index].aspect_ratio() >1.5):
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

def search_for_boxes(picture_in, acceleration, animate):

    picture_out=copy.copy(picture_in)

    original_rows, original_cols, layers = picture_in.shape

    # remove pixels that aren't
    chatter_size=10
    # fill out pixels that are in clusters
    engorge_size=10

    #if this is too slow, make the picture smaller
    if (acceleration>1.0):
        scaling_factor=1.0/numpy.sqrt(acceleration)
        working_picture=cv2.resize(picture_in, (0,0), fx=scaling_factor, fy=scaling_factor)
        chatter_size=int(chatter_size*scaling_factor)
        if (chatter_size<2):
            chatter_size=2
        engorge_size=int(engorge_size*scaling_factor)
        if (engorge_size<2):
            engorge_size=2
    else:
        working_picture=copy.copy(picture_in)

    #hsv = cv2.cvtColor(picture, cv2.COLOR_BGR2HSV)

    working_picture=cv2.bilateralFilter(working_picture,10,150,150)
    #hsv=cv2.bilateralFilter(hsv,10,150,150)
    #show_picture("original",picture,2000)
    #show_picture("hsv",hsv,2000)

    working_rows, working_cols, layers = working_picture.shape

    #create an intial mask where evertying is false
    mask=numpy.zeros((working_rows,working_cols),numpy.uint8)

    #check each pixel and determine if it's color profile is that of a box
    for row in range (0, working_rows-1, 1):
        for col in range (0, working_cols-1, 1):
            color=working_picture[row,col]

            # if the value of the 1st component is within the expected range
            # then check the other two color components
            if ((color[0]>10) and (color[0]<80)):
                # given the value of the first color component, calculate what
                # the other two should be if this is a box
                tar2 = -.00229 * (color[0] ** 2) + 1.83 * color[0] + 34.2
                tar3 = -.00517 * (color[0] ** 2) + 2.2 * color[0] + 25.7
                if (abs(color[1] - tar2) < 40) and (abs(color[2] - tar3) < 40):
                    mask[row, col] = 255


    #show_picture("first",picture,5000)

    #low=  numpy.array([255, 255,255])
    #high= numpy.array([255, 255,255])
    #mask = cv2.inRange(picture, low, high)

    mask=remove_chatter(mask,chatter_size)
    mask=remove_spurious_falses(mask,engorge_size)

    #show_picture("post chatter",mask,5000)

    object_list = find_objects(mask, 3, animate)

    # remove items from the list that are probably just noise or not boxes
    object_list=check_box_object_list(object_list)

    object_list = sort_object_info_list(object_list, 0)

    for i in object_list:
        x, y = i.normalized_center()
        alt, azimuth = altAzi(x,y,22.5,23)
        area= i.relative_area()
        aspect_ratio = i.aspect_ratio()
        distance=distance_to_box_meters(i)
        #  report_box_info_to_jetson(i)

        #draw a circle around the center of the object
        abs_col=int(i.relative_center_col()*original_cols)
        abs_row=int(i.relative_center_row()*original_rows)
        abs_width=int(i.relative_width()*original_cols)
        abs_height=int(i.relative_height()*original_rows)
        if (abs_width>abs_height):
            radius=int(abs_width/2)
        else:
            radius=int(abs_height/2)
        cv2.circle(picture_out, (abs_col, abs_row), radius, (0, 0, 255), 1)

        height=int(i.relative_height()*original_rows)
        min_row=int(i.relative_center_row()*original_rows-height/2)
        max_row=int(i.relative_center_row()*original_rows+height/2)
        width=int(i.relative_width()*original_cols)
        min_col=int(i.relative_center_col()*original_cols-width/2)
        max_col=int(i.relative_center_col()*original_cols+width/2)
        cv2.rectangle(picture_out, (min_col, min_row), (max_col, max_row), (0, 0, 255), 2)

        # I have no idea why this doesn't work
        #min_row=int(i.relative_min_row()*original_rows)
        #min_col=int(i.relative_min_col()*original_cols)
        #max_row=int(i.relative_max_row()*original_rows)
        #max_col=int(i.relative_max_col()*original_cols)
        #cv2.rectangle(picture_out, (min_col, min_row), (max_col, max_row), (0, 0, 255), 2)
        #cv2.rectangle(picture_out, (100, 200), (200, 400), (0, 0, 255), 2)

        print ("Alt: ", round(alt,2), "Azimuth: ", round(azimuth,2), "Relative Area: ", round(area,4), "Aspect Ratio: ", round(aspect_ratio,2), "Perimeter: ", i.perimeter, "Distance, m: ", round(distance,3))


    return picture_out




###################################################################################################

picture = take_picture(True, 1)
searched=search_for_boxes(picture,0, True)
show_picture("processed",searched,10000)
