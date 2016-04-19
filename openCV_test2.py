##Author: Cedric Kim, Kevin Guo
##Software design, spring 2016
##Augmented Reality
##program tracks blue squares and creates vectors

# import the necessary packages
from collections import deque
import numpy as np
import argparse
import imutils
import cv2
import math

class Contours(object):
    def __init__(self):
        """initializes variables"""
        self.contour_list = []
        self.centers = []

    def update_contours(self, contour_information):
        """creates contours sorted by area size (biggest to smallest) from contour_information"""
        ## grab all the contour information and store the actual contours into contours
        contours = contour_information[0]
        self.contour_list = []
        ## if the number of contours is atleast 4,
        if len(contours) >= 4:
            for contour in contours:
                ## store the area of the contours and the contours in the same list
                self.contour_list.append((cv2.contourArea(contour),contour))
        ## sort the contours by area
        self.contour_list.sort(key = lambda x: x[0], reverse=True)

class Centers(object):
    def __init__(self):
        """initializes variables"""
        self.corners = []
        self.main_corner = (0,0)
        self.main_corner_index = -1
        self.vectors = []

    def update_centers(self, contour_list, mask_black):
        """takes in a list of contours and a masked black frame to creates a tuple of (x,y) coordinates for the center of each contour"""
        ## if there are contours in the list,
        if len(contour_list) > 0:
            self.corners = []
            for i in range(4):
                ## create a moment (used to find center of contour)
                M = cv2.moments(contour_list[i][1])
                if M["m00"] != 0 and M["m00"] != 0:
                    ## creates a (x, y) tuple for the contour
                    center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                    ## add the center to a list
                    self.corners.append(center)
            for i, center in enumerate(self.corners):
                ## if the center is within the window range,
                if center[0] < 600 and center[1] < 450:
                    ## grab the color at the center of the black mask,
                    color = mask_black[center[1], center[0]]
                    ## if the color at the center is black
                    if color == 255:
                        ## store that information
                        self.main_corner_index = i
                        self.main_corner = center

    def update_vectors(self):
        """creates vectors (x,y) reference tuples from the main corner (black corner)"""
        self.vectors = []
        ## for each corner in corners,
        for i, corner in enumerate(self.corners):
            main_corner_x = self.main_corner[0]
            main_corner_y = self.main_corner[1]
            corner_x = corner[0]
            corner_y = corner[1]
            ## if the main corner isnt the current index,
            if self.main_corner_index != i:
                ## create a vector and add it to a list
                self.vectors.append((corner_x - main_corner_x, corner_y - main_corner_y))


def program():
    """runs the program"""
    ## create objects for each class
    contour = Contours()
    center = Centers()
    ## define the lower and upper boundaries of the "blue"
    ## define the lower and uppoer boundaries of the "black"
    ## ball in the HSV color space, then initialize the
    ## list of tracked points
    blueLower = np.array([90,100,50])
    blueUpper = np.array([150,255,255])

    blackLower = np.array([0,0,0])
    blackUpper = np.array([180, 255, 150])

    cap = cv2.VideoCapture(0)
    ## keep looping
    while True:
        ## grab the current frame
        ret, frame = cap.read()
    
        ## resize the frame, blur it, and convert it to the HSV
        frame = imutils.resize(frame, width=600)
        frame = cv2.flip(frame,1)
        ## color space
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        ## construct a mask for the color "blue", then remove any imperfections
        mask_blue = cv2.inRange(hsv_frame, blueLower, blueUpper)
        mask_blue = cv2.erode(mask_blue, None, iterations=1)
        mask_blue = cv2.dilate(mask_blue, None, iterations=1)
        ## create black mask for tracking corner
        mask_black = cv2.inRange(hsv_frame, blackLower, blackUpper)
        ## create edges in which to create contours
        edges = cv2.Canny(mask_blue,100,200, apertureSize = 3)

        ##creates information about the contours
        contour_information = cv2.findContours(mask_blue.copy(), cv2.RETR_CCOMP,
            cv2.CHAIN_APPROX_SIMPLE)

        ##updates each of the elements in the classes
        contour.update_contours(contour_information)
        center.update_centers(contour.contour_list, mask_black)
        center.update_vectors()

        for i, corner in enumerate(center.corners):
            ## for each corner, color each one a different color
            if i == 0:
                ##print 'green'
                cv2.circle(frame, corner, 5, (0,255,0), thickness=-1)
            elif i == 1:
                ##print 'red'
                cv2.circle(frame, corner, 5, (0,0,255), thickness=-1)
            elif i == 2:
                ##print 'yellow'
                cv2.circle(frame, corner, 5, (0,255,255), thickness=-1)
            else:
                ##print 'white'
                cv2.circle(frame, corner, 5, (255,255,255), thickness=-1)
        ##uses the vector to draw a line on the tracked square
        for i, vector in enumerate(center.vectors):
            reference_point_x = center.main_corner[0] + vector[0]
            reference_point_y = center.main_corner[1] + vector[1]
            points = np.array([center.main_corner, (reference_point_x, reference_point_y)])
            cv2.polylines(frame, np.int32([points]), True, (0,255,0), 3)

        ## shows each video analysis in different windows
        cv2.imshow("Mask", mask_blue)
        cv2.imshow("MaskBlack", mask_black)
        cv2.imshow('edges', edges)
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF
     
        # if the 'q' key is pressed, stop the loop
        if key == ord("q") or key == 27:
            break
    # cleanup the camera and close any open windows
    camera.release()
    cv2.destroyAllWindows();

if __name__ == '__main__':
    program()