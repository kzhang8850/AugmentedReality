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
        self.final_corners = []

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
    def reorganize_centers(self):
        self.final_corners = []
        self.final_corners.append(self.main_corner)
        corners = []
        for i, corner in enumerate(self.corners):
            if not(self.main_corner[0] == corner[0] and self.main_corner[1] == corner[1]):
                corners.append(corner)

        corner_4 = return_point_4(self.main_corner, corners[0], corners[1], corners[2])
        quadrant = return_closest_quadrant(self.main_corner, corners[0], corners[1], corners[2])
        potential_points = []

        for corner in corners:
            if not (corner[0] == corner_4[0] and corner[1] == corner_4[1]):
                check_quadrant = quadrant + 1
                if check_quadrant == 5:
                    check_quadrant = 1
                if check_quadrant == return_quadrant((corner[0] - self.main_corner[0], corner[1] - self.main_corner[1])):
                    potential_points.append(corner)
        corner_2 = (0,0)
        corner_3 = (0,0)
        if len(potential_points) > 0:
            corner_2 = return_point_2(quadrant, self.main_corner, potential_points)

        for corner in corners:
            if not (corner[0] == corner_4[0] and corner[1] == corner_4[1]):
                if not (corner[0] == corner_2[0] and corner[1] == corner_2[1]):
                    corner_3 = corner
        self.final_corners.append(corner_2)
        self.final_corners.append(corner_3)
        self.final_corners.append(corner_4)

def return_point_2(quadrant, main_corner, potential_points):
    if len(potential_points) == 1:
        return potential_points[0]
    else:
        if quadrant == 1:
            reference_point = (main_corner[0], main_corner[1] - 10)
        elif quadrant == 2:
            reference_point = (main_corner[0] - 10, main_corner[1])
        elif quadrant == 3:
            reference_point = (main_corner[0], main_corner[1] + 10)
        else:
            reference_point = (main_corner[0] + 10, main_corner[1])
        angle_1 = get_angle(main_corner, reference_point, potential_points[0])
        angle_2 = get_angle(main_corner, reference_point, potential_points[1])
        if angle_1 < angle_2:
            return potential_points[0]
        else:
            return potential_points[1]

def return_closest_quadrant(main_corner, point_1, point_2, point_3):
    reference_point_1 = (point_1[0] - main_corner[0], point_1[1] - main_corner[1])
    reference_point_2 = (point_2[0] - main_corner[0], point_2[1] - main_corner[1])
    reference_point_3 = (point_3[0] - main_corner[0], point_3[1] - main_corner[1])
    quadrants = []
    quadrants.append(return_quadrant(reference_point_1))
    quadrants.append(return_quadrant(reference_point_2))
    quadrants.append(return_quadrant(reference_point_3))
    empty_quadrants = []
    for i in range(1, 5):
        if i not in quadrants:
            empty_quadrants.append(i)
    if len(empty_quadrants) == 1:
        return empty_quadrants[0]
    if len(empty_quadrants) == 2 and empty_quadrants[0] == 1 and empty_quadrants[1] == 4:
        return 1
    elif len(empty_quadrants) == 3 and empty_quadrants[1] == 1 and empty_quadrants[2] == 4:
        return 1
    else:
        if len(empty_quadrants) == 2:
            return empty_quadrants[1]
        else:
            return empty_quadrants[2]

def return_quadrant(point):
    if is_positive(point[0]) and not is_positive(point[1]):
        return 1
    elif not is_positive(point[0]) and not is_positive(point[1]):
        return 2
    elif not is_positive(point[0]) and is_positive(point[1]):
        return 3
    else:
        return 4

def return_point_4(main_corner, point_1, point_2, point_3):
    angle_1 = get_angle(main_corner, point_1, point_2)
    angle_2 = get_angle(main_corner, point_1, point_3)
    angle_3 = get_angle(main_corner, point_2, point_3)
    #print "1:", angle_1, "   2:", angle_2, "  3:", angle_3
    if(angle_1 > angle_2 and angle_1 > angle_3):
        return point_3
    elif(angle_2 > angle_3):
        return point_2
    else:
        return point_1

def get_distance(point1, point2):
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

def get_angle(main_corner, point_1, point_2):
    c = get_distance(point_1, point_2)
    b = get_distance(main_corner, point_2)
    a = get_distance(main_corner, point_1)
    return math.fabs(math.acos((c**2 - a**2 - b**2)/(-2*a*b)))

def is_positive(x):
    return (x >= 0)

class Camera(object):
    def __init__(self):
        self.objpoints = [] #3d point in real world space
        self.imgpoints = [] #2d points in image plane.
        self.criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        self.objp = np.zeros((2*2,3), np.float32)
        self.objp[:,:2] = np.mgrid[0:2,0:2].T.reshape(-1,2)
        self.ret = None
        self.mtx = None
        self.dist = None
        self.rvecs = None
        self.tvex = None
        self.draw_axis = False
    def grab_frame_information(self, frame, corners):
        # Arrays to store object points and image points from all the images.
        self.objpoints.append(self.objp)
        self.imgpoints.append(np.array(corners, dtype = np.float32))
        print self.objp
        print np.array(corners)
        #cv2.putText(frame, "Hi", (100,100), 
        #cv2.FONT_HERSHEY_PLAIN, 10, 255, thickness = 3)
    def calibrate_camera(self, gray):
        self.ret, self.mtx, self.dist, self.rvecs, self.tvecs = cv2.calibrateCamera(self.objpoints, self.imgpoints, gray.shape[::-1],None,None)

def draw(frame, corner, imgpts):
    #corner = tuple(corners[0].ravel())
    #print corner
    img = cv2.line(frame, corner, tuple(imgpts[0].ravel()), (255,0,0), 5)
    img = cv2.line(frame, corner, tuple(imgpts[1].ravel()), (0,255,0), 5)
    img = cv2.line(frame, corner, tuple(imgpts[2].ravel()), (0,0,255), 5)

def draw_cube(frame, corner, imgpts):
    imgpts = np.int32(imgpts).reshape(-1,2)

    # draw ground floor in green
    img = cv2.drawContours(frame, [imgpts[:4]],-1,(255),3)

    # draw pillars in blue color
    for i,j in zip(range(4),range(4,8)):
        img = cv2.line(frame, tuple(imgpts[i]), tuple(imgpts[j]),(255),3)

    # draw top layer in red color
    img = cv2.drawContours(frame, [imgpts[4:]],-1,(255),3)

def program():
    """runs the program"""
    ## create objects for each class
    contour = Contours()
    center = Centers()
    camera = Camera()
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
        gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

        ##creates information about the contours
        contour_information = cv2.findContours(mask_blue.copy(), cv2.RETR_CCOMP,
            cv2.CHAIN_APPROX_SIMPLE)

        ##updates each of the elements in the classes
        contour.update_contours(contour_information)
        center.update_centers(contour.contour_list, mask_black)
        if len(center.corners) == 4:
            center.reorganize_centers()
        center.update_vectors()

       

        # criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        # axis = np.float32([[3,0,0], [0,3,0], [0,0,-3]]).reshape(-1,3)
        key = cv2.waitKey(1) & 0xFF
        # rvecs, tvecs, inliers = cv2.solvePnPRansac(objp, corners2, mtx, dist)
        if key == ord("k"):
            camera.grab_frame_information(frame, center.final_corners)
        if key == ord("c"):
            camera.calibrate_camera(gray)
        if key == ord("d"):
            camera.draw_axis = not camera.draw_axis


        if camera.draw_axis:
            #axis = np.float32([[1,0,0], [0,1,0], [0,0,1]]).reshape(-1,3)
            axis = np.float32([[0,0,0], [0,1,0], [1,1,0], [1,0,0],
                   [0,0,1],[0,1,1],[1,1,1],[1,0,1] ])
            rvecs, tvecs, inliers = cv2.solvePnPRansac(camera.objp, np.array(center.final_corners, dtype = np.float32), camera.mtx, camera.dist)
            imgpts, jac = cv2.projectPoints(axis, rvecs, tvecs, camera.mtx, camera.dist)
            draw_cube(frame, center.main_corner, imgpts)
        else:
            for i, corner in enumerate(center.final_corners):
                ## for each corner, color each one a different color
                if i == 0:
                    ##print 'green'
                    cv2.circle(frame, corner, 20, (0,255,0), thickness=-1)
                elif i == 1:
                    ##print 'red'
                    cv2.circle(frame, corner, 15, (0,0,255), thickness=-1)
                elif i == 2:
                    ##print 'yellow'
                    cv2.circle(frame, corner, 10, (0,255,255), thickness=-1)
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
     
        # if the 'q' key is pressed, stop the loop
        if key == ord("q") or key == 27:
            break

    # cleanup the camera and close any open windows
    camera.release()
    cv2.destroyAllWindows();

if __name__ == '__main__':
    program()