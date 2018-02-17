# file last changed on 10February2018
import numpy
import cv2
import time
import copy


#######################################################################################################################

def show_picture(title, picture, time_msec):

    cv2.imshow(title, picture)
    cv2.waitKey(time_msec)


#######################################################################################################################

#Takes original picture, in color. Two input parameters are
# 'show', a boolean that determines whether the image will be shown,
# and 'device_number', an integer that determines which device to use to take the picture.

def take_picture(show, device_number):

    cap = cv2.VideoCapture(device_number)
    ret, picture = cap.read()

    if (show==True):
        cv2.imshow("take picture", picture)
        cv2.waitKey(3000)
        cap.release()

    return picture

#######################################################################################################################


#Given a row and column input, and a list of row/column pairs, this returns the index of the element in the list
# which is closest to the input row/column.

def closest(row, col, coordinates_list):

    close_index=-1
    closest_so_far=999999999999999999999999

    for list_index in range (0,len(coordinates_list),1):
        check_row=coordinates_list[list_index][0]
        check_col=coordinates_list[list_index][1]
        distance = numpy.sqrt((check_row-row)**2 + (check_col-col)**2)
        if distance<closest_so_far:
            closest_so_far=distance
            close_index=list_index

    return close_index

#######################################################################################################################

#Given a picture reduced to true/false values (0=false,  not zero=true), and a row/col coordinate that describes a coordinate
# in said picture, and a search radius in pixels, this returns a list of all the row/col pairs
# within that radius that are true. It does not return the original input pixel.

def in_range(picture, row, col, radius):

    rows, cols = picture.shape
    coords_to_check=[]
    pixels_found_list=[]

    for check_row in range(row-radius, row+radius, 1):
        for check_col in range(col-radius, col+radius, 1):
            # makes sure pixel is within bounds of picture
            if ((check_row >= 0) and (check_col>=0) and (check_row<rows) and (check_col<cols)):
                 distance = numpy.sqrt((row-check_row)**2 + (col-check_col)**2)
                 if distance<=radius+0.5:
                     coords_to_check.append(copy.copy([check_row, check_col]))

    for list_index in range(0, len(coords_to_check), 1):
        check_row = coords_to_check[list_index][0]
        check_col = coords_to_check[list_index][1]

        if (picture[check_row, check_col]!=0) and not(check_row==row and check_col==col):
            pixels_found_list.append(copy.copy([check_row, check_col]))

    return pixels_found_list

#######################################################################################################################


#Given a picture reduced to true/false values (0=false, not 0 =true), and a row/col coordinate that describes a coordinate
# in said picture, and a search radius in pixels, this sets all pixels within the radius of the original coordinate to
# false.

def obliterate(picture, row, col, radius):

    rows, cols = picture.shape

    return_picture = copy.copy(picture)

#creates a list of all the coordinates to check
    for check_row in range(row-radius, row+radius, 1):
        for check_col in range(col - radius, col + radius, 1):
             #makes sure pixel is within bounds of picture
             if ((check_row<rows) and (check_col<cols)) and (check_row>=0 and check_col>=0):
                 distance = numpy.sqrt((check_row-row)**2 + (check_col-col)**2)
                 if distance<=radius:
                     return_picture[check_row, check_col]=0

    return return_picture

#######################################################################################################################

#Given a picture reduced to true/false values (0=false, not 0 =true), this sets all pixels otherwise surrounded by true
# pixels to false. Does not check the edges because that fringe problem is
# probably not worth spending a bunch of time and cpu to fix.

def hollow_out(picture):

    working=copy.copy(picture)

    rows, cols = working.shape

    for row in range(1, rows - 2, 1):
        for col in range(1, cols - 2, 1):
            if (picture[row,col]==255):
                if(picture[row,col-1]==255):
                    if(picture[row,col+1]==255):
                        if(picture[row-1,col]==255):
                            if(picture[row-1,col-1]==255):
                                if(picture[row-1,col+1]==255):
                                    if(picture[row+1,col]==255):
                                        if(picture[row+1,col-1]==255):
                                            if(picture[row+1,col+1]==255):
                                                working[row,col]=0



    return working

#######################################################################################################################


class object_info_class(object):
        def __init__(self):
            self.source_dimensions=[0,0]
            # the center of the object in row, col coordinates
            self.center_RC = [0.0,0.0]
            self.perimeter = 0
            self.max_row = [0,0]
            self.max_col = [0,0]
            self.min_row = [0,0]
            self.min_col = [0,0]

        # this returns the center coordinates of the object normalized to the dimensions of the image
        # in cartesian coordinates.  The center of the image is 0,0.  The upper right hand corner is 1,1
        # the lower left hand corner is -1, -1
        def normalized_center(self):
            norm_x=float(self.center_RC[1]-(1.0*self.source_dimensions[1]/2))
            norm_x=float(norm_x/(1.0*self.source_dimensions[1]/2))

            norm_y=float((1.0*self.source_dimensions[0]/2) - self.center_RC[0])
            norm_y=float(norm_y/(1.0*self.source_dimensions[0]/2))

            return norm_x, norm_y

        def relative_area(self):
            return float((self.max_row[0]-self.min_row[0]+1)*(self.max_col[1]-self.min_col[1]+1)/(1.0*self.source_dimensions[0]*self.source_dimensions[1]))

        def aspect_ratio(self):
            return float(self.max_row[0]-self.min_row[0]+1)/(self.max_col[1]-self.min_col[1]+1)

#######################################################################################################################

# Given a true/false bitmap and a search radius, this locates discrete blobs
# by tracing their outlines with accuracy of search_radius, and
# returns a list (object_info_list) of 'object_info_class'

def find_objects(picture, search_radius, animate):
    object_info = object_info_class()
    object_info_list = []

    # hollow out the blobs
    picture=hollow_out(picture)

    working_image=copy.copy(picture)

    rows, cols = working_image.shape

    objects_found=0

    for row in range(0, rows-1, 1):
        for col in range(0, cols-1, 1):

            if working_image[row, col] != 0:

                pixel_found=True
                object_info.max_row=[row, col]
                object_info.min_row=[row, col]
                object_info.max_col=[row, col]
                object_info.min_col=[row, col]

                sum_row=0
                sum_col=0
                total_pixels_found=0

                check_row=row
                check_col=col

                while(pixel_found):
                    total_pixels_found+=1
                    sum_row+=check_row
                    sum_col+=check_col

                    if check_row>object_info.max_row[0]:
                        object_info.max_row=[check_row,check_col]
                    elif check_row<object_info.min_row[0]:
                        object_info.min_row=[check_row,check_col]

                    if check_col>object_info.max_col[1]:
                        object_info.max_col=[check_row,check_col]
                    elif check_col<object_info.min_col[1]:
                        object_info.min_col=[check_row,check_col]

                    if (animate!=0):
                        working_image[check_row,check_col] = 0
                        cv2.imshow("working", working_image)
                        cv2.waitKey(1)

                    # find all the pixels within a radius
                    close_by=in_range(working_image,check_row,check_col, search_radius)

                    if (len(close_by)>0):
                        closest_index = closest(check_row,check_col,close_by)
                        check_row=close_by[closest_index][0]
                        check_col=close_by[closest_index][1]
                    else:
                        object_info.perimeter = total_pixels_found
                        object_info.center_RC = [float(1.0*sum_row/total_pixels_found), float(1.0*sum_col/total_pixels_found)]
                        object_info.source_dimensions=[rows, cols]
                        pixel_found = False
                        object_info_list.append(copy.copy(object_info))
                        objects_found+=1


    return object_info_list

#######################################################################################################################
# given a mask this removes any True that isn't surrounded by other True pixels based on the width of the box

def remove_chatter(mask_in,square_width):

    mask_out=copy.copy(mask_in)
    kernel=numpy.ones((square_width,square_width),numpy.uint8)
    mask_out=cv2.erode(mask_in,kernel,iterations=1)

    return mask_out

#######################################################################################################################
# given a mask this makes True any pixel that falls within box size of a True
# this has the effect of removing False pixels that are surrounded by True pixels

def remove_spurious_falses(mask_in,square_width):

    mask_out=copy.copy(mask_in)
    kernel=numpy.ones((square_width,square_width),numpy.uint8)
    mask_out=cv2.dilate(mask_in,kernel,iterations=1)

    return mask_out

#######################################################################################################################
#Given t/f bitmap, every pixel that isn't surrounded completely by otherwise true pixels is set to false.

def clean_edge(picture):

    working=copy.copy(picture)

    rows, cols = working.shape

    for row in range(1, rows - 1, 1):
        for col in range(1, cols - 1, 1):
            if (picture[row-1,col-1]==0):
                working[row,col]=0
            elif (picture[row-1, col] == 0):
                working[row, col] = 0
            elif (picture[row-1, col+1] == 0):
                working[row, col] = 0
            elif (picture[row, col-1] == 0):
                working[row, col] = 0
            elif (picture[row, col] == 0):
                working[row, col] = 0
            elif (picture[row, col + 1] == 0):
                working[row, col] = 0
            elif (picture[row+1, col-1] == 0):
                working[row, col] = 0
            elif (picture[row+1, col] == 0):
                working[row, col] = 0
            elif (picture[row+1, col+1] == 0):
                working[row, col] = 0



    return working

#######################################################################################################################

#Given a color picture, and low and high hue, saturation, and value thresholds, this returns a true/false bitmap where
# everything that falls within all 3 thresholds is true (255) and everything else is false (0).

def find_blobs(picture, low, high):
    hsv = cv2.cvtColor(picture, cv2.COLOR_BGR2HSV)
    hsv2 = cv2.bilateralFilter(hsv, 9, 150, 150)
    mask = cv2.inRange(hsv2, low, high)

    return mask

#######################################################################################################################

# Given img, row, col, this tells you the absolute x and y position of the row and col
# centered on an image with center 0, 0.

def centerCoordinates(image, row, col):
    rows, cols = image.shape
    y = 0 - (row - rows / 2)
    x = col - cols / 2
    return x,y

#######################################################################################################################

# Same as the one below, but it extracts rows and cols from an image

def normalizeCoordinatesI(image, row, col):
    rows, cols = image.shape
    normx = 1.0 * row / (cols / 2)
    normy = 1.0 * col / (rows / 2)
    return normx, normy

#######################################################################################################################

# Given the width of the image in rows and columns, and a row, column position, this returns the normalized
# x, y position of the row, column where the center of the picture is 0, 0 where x=+1 is rightmost and x=-1 is leftmost,
# y=+1 is topmost and y=-1 is bottommost.

def normalizecoordinatesRC(rows, cols, row, col):
    normx = 1.0 * col / (cols / 2)
    normy = 1.0 * row / (rows / 2)
    return normx, normy

#######################################################################################################################

#Given a normalized x y position where x=+1 is rightmost and x=-1 is leftmost,
# y=+1 is topmost and y=-1 is bottommost, horizontal angle is angle from center to rightmost viewing angle,
# this returns the altitude and azmuth of that normalized position.

def altAzi(normx, normy, horizontal_angle, vertical_angle):
    altitude = normy * vertical_angle
    azimuth = normx * horizontal_angle
    return altitude, azimuth

#######################################################################################################################

#sorts a list of text outputs based on a parameter for easy viewing. Sorts largest to smallest.
# 0 is sort by relative area
# 1 is aspect ratio
# 2 is perimeter

def sort_object_info_list(unsorted_list, sort_by):

    # start with a sorted list of the first object in the unsorted list
    sorted_list=[]
    if (len(unsorted_list)>0):
        sorted_list.append(copy.copy(unsorted_list[0]))

    for unsorted_index in range(1, len(unsorted_list), 1):

        found=False
        sorted_index=0

        while found==False:

            if sort_by==0:
                unsorted_value=unsorted_list[unsorted_index].relative_area()
                sorted_value=sorted_list[sorted_index].relative_area()
            elif sort_by == 1:
                unsorted_value = unsorted_list[unsorted_index].aspect_ratio()
                sorted_value = sorted_list[sorted_index].aspect_ratio()
            elif sort_by == 2:
                unsorted_value = unsorted_list[unsorted_index].perimeter
                sorted_value = sorted_list[sorted_index].perimeter

            if unsorted_value>sorted_value:
                found=True
                sorted_list.append(copy.copy(sorted_list[len(sorted_list)-1]))
                for end_index in range(len(sorted_list)-2, sorted_index, -1):
                    sorted_list[end_index]=copy.copy(sorted_list[end_index-1])
                sorted_list[sorted_index]=copy.copy(unsorted_list[unsorted_index])
            else:
                sorted_index+=1
                if sorted_index==len(sorted_list):
                    sorted_list.append(copy.copy(unsorted_list[unsorted_index]))
                    found=True


    return sorted_list

#######################################################################################################################

# given a picture, this allows the user to select a locations on the picture and reports the three color
# values associated with the location
# this is intended as a tool to held with object identification
# to exit the function, the user enters a negative X location


def get_pixel_values(picture):

    [rows, cols, depth] = picture.shape

    run_again=True

    while run_again:
        print("Input X, Y as 0-100%:")
        rel_col, rel_row = input()

        if (rel_col>0):
            #convert from relative position to absolute row and colmn
            rel_col=float(1.0*rel_col/100)
            abs_col=cols*rel_col
            abs_col=int(abs_col)

            rel_row=float(1.0*rel_row/100)
            rel_row=1-rel_row
            abs_row=rows*rel_row
            abs_row=int(abs_row)

            if (abs_row<rows and abs_col<cols):
                working=copy.copy(picture)
                cv2.circle(working,(abs_col,abs_row),5,(0,0,255),1)
                cv2.imshow("location", working)
                cv2.waitKey(100)
                print(picture[abs_row, abs_col])
        else:
            run_again = False


#######################################################################################################################

def euclidian_distance(one, two):

    distance=numpy.linalg.norm(one-two)

    return distance
