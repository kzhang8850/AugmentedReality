# import the necessary packages
from collections import deque
import numpy as np
import argparse
import imutils
import cv2
import math

class Contours(object):
    def __init__(self, contour_information):
        pass


def program():
    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--video",
        help="path to the (optional) video file")
    ap.add_argument("-b", "--buffer", type=int, default=64,
        help="max buffer size")
    args = vars(ap.parse_args())

    # define the lower and upper boundaries of the "blue"
    # define the lower and uppoer boundaries of the "black"
    # ball in the HSV color space, then initialize the
    # list of tracked points
    blueLower = np.array([90,100,50])
    blueUpper = np.array([150,255,255])

    blackLower = np.array([0,0,0])
    blackUpper = np.array([180, 255, 150])
    pts = deque(maxlen=args["buffer"])
     
    # if a video path was not supplied, grab the reference
    # to the webcam
    if not args.get("video", False):
        camera = cv2.VideoCapture(0)
     
    # otherwise, grab a reference to the video file
    else:
        camera = cv2.VideoCapture(args["video"])

    # keep looping
    while True:
        # grab the current frame
        (grabbed, frame) = camera.read()
     
        # if we are viewing a video and we did not grab a frame,
        # then we have reached the end of the video
        if args.get("video") and not grabbed:
            break
     
        # resize the frame, blur it, and convert it to the HSV
        # color space
        frame = imutils.resize(frame, width=600)
        frame = cv2.flip(frame,1)
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # construct a mask for the color "blue", then remove any imperfections
        mask_blue = cv2.inRange(hsv_frame, blueLower, blueUpper)
        mask_blue = cv2.erode(mask_blue, None, iterations=1)
        mask_blue = cv2.dilate(mask_blue, None, iterations=1)
        #create black mask for tracking corner
        mask_black = cv2.inRange(hsv_frame, blackLower, blackUpper)
        #create edges in which to create contours
        edges = cv2.Canny(mask_blue,100,200, apertureSize = 3)

        #create contours and hierarchy
        cnts, cnt_hierarchy = cv2.findContours(mask_blue.copy(), cv2.RETR_CCOMP,
            cv2.CHAIN_APPROX_SIMPLE)

        centers = []
        maxcnts = []
        minArea = None
        cntAreas = []
        cntDict = dict()

        if cnt_hierarchy != None:
            cnt_hierarchy = cnt_hierarchy[0]

        #if there are more than 4 contours
        if len(cnts) >= 4 and len(cnt_hierarchy) >= 4:

            for i in range(len(cnts)):
                cntAreas.append((cv2.contourArea(cnts[i]),cnts[i], cnt_hierarchy[i]))
            largest_contour = 0
            largest_contour_index = -1
            for i, cnt in enumerate(cntAreas):
                if cnt[2][2] == -1:
                    if cnt[0] > largest_contour:
                        largest_contour = cv2.contourArea(cnts[i])
                        largest_contour_index = i

            cntAreas.sort(key = lambda x: x[0], reverse=True)
            
            for i in range(4):
                M = cv2.moments(cntAreas[i][1])
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                centers.append(center)
            """
            center_x = centers[4][0]
            center_y = centers[4][1]
            threshold = 50
            corner_index = -1
            for i in range(4):
                if abs(center_x - centers[i][0]) < threshold and abs(center_x - centers[i][1]) < threshold:
                    corner_index = i
            for i in range(4): 
                cv2.circle(frame, centers[i], 10, (0,255,0), thickness=-1)
                if i == corner_index:
                    cv2.circle(frame, centers[i], 5, (255,0,0), thickness=-1)
            """


            #for i in range(4):
            #    if i == largest_contour_index:
            #        cv2.circle(frame, centers[i], 5, (255,0,0), thickness=-1)
            #    else:
            #        cv2.circle(frame, centers[i], 5, (0,255,0), thickness=-1)

            #centers.sort(key = lambda x: x[0])
            main_corner_index = 0
            main_corner = (0,0)
            farther_index = 0
            index_found = False
            for i, center in enumerate(centers):
                #scaler = int(cntAreas[i][0]/500)
                #cv2.circle(frame, center, 5, (0,255,0), thickness=-1)
                #cv2.circle(frame, (center[0] + scaler, center[1] + scaler), 5, (255, 0, 0), thickness = -1)
                print "x,y:"
                print center[0] , ", ", center[1]
                x_center =  center[0]
                y_center = center[1]
                print center
                #cv2.circle(frame, (350,350), 5, (255,0,0), thickness=-1)
                #cv2.circle(frame, (300,350), 5, (255,0,0), thickness=-1)
                #print i
                if i == 0:
                    #print 'green'
                    cv2.circle(frame, center, 5, (0,255,0), thickness=-1)
                elif i == 1:
                    #print 'red'
                    cv2.circle(frame, center, 5, (0,0,255), thickness=-1)
                elif i == 2:
                    #print 'yellow'
                    cv2.circle(frame, center, 5, (0,255,255), thickness=-1)
                else:
                    #print 'white'
                    cv2.circle(frame, center, 5, (255,255,255), thickness=-1)
                if center[0] < 600 and center[1] < 450:
                    #print mask_black[center]

                    #if bottom_right_point[0] < 450 and bottom_right_point[1] < 450:
                        #cv2.circle(mask_black, (300, 300), 10, (255,255,0), thickness=-1)
                    #print hsv_frame[300, 300][1]
                    color = mask_black[center[1], center[0]]
                    #color = mask_black[350,350]
                    #print i, " = "
                    #print color
                    #print color
                    if color == 255:
                        main_corner_index = i
                        main_corner = center
                        cv2.circle(frame, center, 5, (0,0,0), thickness=-1)
                    if main_corner_index != i and not index_found:
                        farther_index = i
                        index_found = True

            vectors = []
            for i, center in enumerate(centers):
                if main_corner_index != i and farther_index != i:
                    vectors.append((-main_corner[0] + center[0], -main_corner[1] + center[1]))

            for i, vector in enumerate(vectors):
                reference_point_x = main_corner[0] + vector[0]
                reference_point_y = main_corner[1] + vector[1]
                points = np.array([main_corner, (reference_point_x, reference_point_y)])
                cv2.polylines(frame, np.int32([points]), True, (0,255,0), 3)


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


def cartesian_distance(pt1, pt2):
    y1 = pt1[0][1]
    x1 = pt1[0][0]
    y2 = pt2[0][1]
    x2 = pt2[0][0]
    return math.sqrt((x1-x2)**2 + (y1-y2)**2)

if __name__ == '__main__':
    program()
