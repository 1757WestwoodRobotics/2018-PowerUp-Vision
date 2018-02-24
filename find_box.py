from westwood_vision_tools import *
import numpy
#from publish_data import *

##################################################################################################################
# this gets rid of a "box" if it is entirely within the area of another box

def remove_box_in_a_box(list_in):

    list_out=copy.copy(list_in)

    # do one pass then reverse the list and do another
    # this addresses the a in b and b in a condition
    for thing in range (0,2,1):
        # start at the end of the list and work to the from
        last_index=len(list_out)-1

        while(last_index>0):
            check_index=0
            check_next=True
            while (check_next):

                check_object=list_out[check_index]
                last_object=list_out[last_index]

                if (check_object.relative_max_row()>last_object.relative_max_row() and
                    check_object.relative_max_col()>last_object.relative_max_col() and
                    check_object.relative_min_row()<last_object.relative_min_row() and
                    check_object.relative_min_col()<last_object.relative_min_col()):
                    list_out.pop(last_index)
                    check_next=False
                else:
                    check_index+=1

                if (check_index>=last_index):
                    check_next=False

            last_index-=1

        list_out.reverse()

    return list_out

##################################################################################################################
# given an object list of what is supposed to be boxes, this checks the list and removes objects
# from the list that are not likely to be boxes

def check_box_object_list(list_in):

    list_out=copy.copy(list_in)

    index=0
    while index<len(list_out):

        # the box is square and should have an aspect ratio near 1
        if (list_out[index].aspect_ratio > 1.3 or list_out[index].aspect_ratio < .75) and (list_out[index].relative_area()<0.003): # require a minimum size
            list_out.pop(index)
        elif (list_out[index].aspect_ratio < 1.75 or list_out[index].aspect_ratio > 2.3) and (list_out[index].relative_area()<0.006):
            list_out.pop(index)
        else:
            index+=1

    return list_out

######################################################################################################################
# this attempts to figure out the distance to the box in meters based on how much of the relative area it consumes,
# this is is very dependent on the camera being used

def distance_to_box_meters(box_object_info):

    # because several boxes could be pushed against each other, make a guess
    # that aspect ratios of 2:1, 3:1 etc. are multiple boxes in a row
    # this is very crude and assumes that the boxe aren't stacked
    aspect_ratio=box_object_info.aspect_ratio()

    if ((aspect_ratio>0) and (aspect_ratio<1)):
        aspect_ratio/=1

    if (aspect_ratio>0):
        area = box_object_info.relative_area()
        area=float(area/aspect_ratio)
        distance_meters=0.429*numpy.power(area,-0.443)
    else:
        distance_meters=-1

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

    working_picture=cv2.bilateralFilter(working_picture,10,150,150)

    working_rows, working_cols, layers = working_picture.shape

    run_fast=False

    if run_fast:
        mask = cv2.inRange(working_picture, (0, 100, 150), (100, 255, 255))
    else:
        # create an intial mask where evertying is false
        mask = numpy.zeros((working_rows, working_cols), numpy.uint8)

        #check each pixel and determine if it's color profile is that of a box
        for row in range (0, working_rows-1, 1):
            for col in range (0, working_cols-1, 1):
                color=working_picture[row,col]

                # if the value of the 1st component is within the expected range
                # then check the other two color components
                if ((color[1]>65) and (color[1]<210) and (color[2] < 180)):
                    # given the value of the first color component, calculate what
                    # the other two should be if this is a box
                    tar1 = .0055 * color[1]**2 - .641 * color[1] + 53.1
                    tar3 = .83 * color[1] + 9.11
                    if (abs(color[0] - tar1) < 21) and (abs(color[2] - tar3) < 21):
                        mask[row, col] = 255

    mask=remove_chatter(mask,chatter_size)
    mask=remove_spurious_falses(mask,engorge_size)

    if run_fast:
        object_list = find_objects_fast(mask)
    else:
        object_list = find_objects(mask, 3, animate)

    # remove items from the list that are probably just noise or not boxes
    #object_list=check_box_object_list(object_list)
    object_list=remove_box_in_a_box(object_list)

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

        # draw a box around the object
        min_row=int(i.relative_min_row()*original_rows)
        min_col=int(i.relative_min_col()*original_cols)
        max_row=int(i.relative_max_row()*original_rows)
        max_col=int(i.relative_max_col()*original_cols)
        cv2.rectangle(picture_out, (min_col, min_row), (max_col, max_row), (0, 0, 255), 2)

    #    print ("Alt: ", round(alt,2), "Azimuth: ", round(azimuth,2), "Relative Area: ", round(area,4), "Aspect Ratio: ", round(aspect_ratio,2), "Perimeter: ", i.perimeter, "Distance, m: ", round(distance,3))


    return picture_out




###################################################################################################

#picture = take_picture(False, 1)
#picture = cv2.imread("C:\Users/20jgrassi\Pictures\Camera Roll\edited.jpg")

cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_SETTINGS, 1) #to fix things
while True:

    picture = take_picture2(cap)
    #start_time = time.time()
    searched=search_for_boxes(picture,10, False)
    #stop_time=time.time()
    #print(stop_time-start_time)
    show_picture("processed",searched,10)
