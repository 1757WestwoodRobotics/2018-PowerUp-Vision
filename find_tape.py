from westwood_vision_tools import *
import numpy
from publish_data import *


##################################################################################################################
# given an object list of what is supposed to be boxes, this checks the list and removes objects
# from the list that are not likely to be boxes

def check_tape_object_list(list_in):

    list_out=copy.copy(list_in)

    index=0
    while index<len(list_out):

        # the box is square and should have an aspect ratio near 1
        if (list_out[index].relative_area()<0.0007): # require a minimum size
            list_out.pop(index)
        else:
            index+=1

    return list_out

######################################################################################################################
# this attempts to figure out the distance to the box in meters based on how much of the relative area it consumes,
# this is is very dependent on the camera being used

def distance_to_tape_meters(box_object_info):

    area=box_object_info.relative_area()
    distance_meters=0.204*numpy.power(area,-0.5)

    return distance_meters

######################################################################################################################

def report_tape_info_to_jetson(object_info, table):

    x, y = object_info.normalized_center()
    alt, azimuth = altAzi(x, y, 22.5, 23)
    area = object_info.relative_area()
    aspect_ratio = object_info.aspect_ratio()
    distance = distance_to_tape_meters(object_info)

    publish_network_value("altitude", alt, table)
    publish_network_value("azimuth",  azimuth, table)
    publish_network_value("distance, m",  distance, table)


######################################################################################################################


def search_for_tape(picture_in, acceleration, animate, table):

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

    working_picture = cv2.bilateralFilter(working_picture, 10, 150, 150)

    # threshold the image based on RGV values (BGR)
    mask = cv2.inRange(working_picture, (20, 80, 0), (120, 200, 50))
  #  mask = remove_chatter(mask, chatter_size)
  #  mask = remove_spurious_falses(mask, engorge_size)

    object_list = find_objects(mask, 3, animate)
    object_list = check_tape_object_list(object_list)
    object_list = remove_box_in_a_box(object_list)
    object_list = sort_object_info_list(object_list, 0)

    for i in object_list:
        x, y = i.normalized_center()
        alt, azimuth = altAzi(x, y, 22.5, 23)
        area = i.relative_area()
        aspect_ratio = i.aspect_ratio()
        distance = distance_to_tape_meters(i)
        report_tape_info_to_jetson(i, table)

        # draw a circle around the center of the object
        abs_col = int(i.relative_center_col() * original_cols)
        abs_row = int(i.relative_center_row() * original_rows)
        abs_width = int(i.relative_width() * original_cols)
        abs_height = int(i.relative_height() * original_rows)
        if (abs_width > abs_height):
            radius = int(abs_width / 2)
        else:
            radius = int(abs_height / 2)

        # if the box has an actual width
        if (radius >= 1):
            cv2.circle(picture_out, (abs_col, abs_row), radius, (0, 0, 255), 1)

            # draw a box around the object
            min_row = int(i.relative_min_row() * original_rows)
            min_col = int(i.relative_min_col() * original_cols)
            max_row = int(i.relative_max_row() * original_rows)
            max_col = int(i.relative_max_col() * original_cols)
            cv2.rectangle(picture_out, (min_col, min_row), (max_col, max_row), (0, 0, 255), 2)

        print ("Alt: ", round(alt, 2), "Azimuth: ", round(azimuth, 2), "Relative Area: ", round(area, 4), "Aspect Ratio: ",round(aspect_ratio, 2), "Perimeter: ", i.perimeter, "Distance, m: ", round(distance, 3))


    return picture_out


###################################################################################################


cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_SETTINGS, 1) #to fix things
table = init_network_tables()
cap.set(cv2.CAP_PROP_BRIGHTNESS, 30)
cap.set(cv2.CAP_PROP_EXPOSURE, -10)
cap.set(cv2.CAP_PROP_CONTRAST, 9)
cap.set(cv2.CAP_PROP_SATURATION, 199)

while True:

    picture = take_picture2(cap)
    #start_time = time.time()
    searched=search_for_tape(picture,1, False, table)
    #stop_time=time.time()
    #print(stop_time-start_time)
    show_picture("processed",searched,10)