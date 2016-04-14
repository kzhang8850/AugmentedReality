# import the necessary packages
from collections import deque
import numpy as np
import argparse
import imutils
import cv2
import math

def program():
    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--video",
        help="path to the (optional) video file")
    ap.add_argument("-b", "--buffer", type=int, default=64,
        help="max buffer size")
    args = vars(ap.parse_args())

    # define the lower and upper boundaries of the "blue"
    # ball in the HSV color space, then initialize the
    # list of tracked points
    blueLower = (90,140,50) 
    blueUpper = (220,255,255)

    greenLower = (50,50,46) #50,50,66 
    greenUpper = (110,135,170)

    # yellowLower = (30,30,130) 
    # yellowUpper = (48,150,220)

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
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
     
        # construct a mask for the color "blue", then remove any imperfections
        mask_blue = cv2.inRange(hsv, blueLower, blueUpper)
        mask_blue = cv2.erode(mask_blue, None, iterations=3)
        mask_blue = cv2.dilate(mask_blue, None, iterations=2)

        mask_green = cv2.inRange(hsv, greenLower, greenUpper)
        mask_green = cv2.erode(mask_green, None, iterations=3)
        mask_green = cv2.dilate(mask_green, None, iterations=2)
        mask = mask_blue + mask_green

        edges = cv2.Canny(mask,100,200, apertureSize = 3)

        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)[-2]

        centers = []
        maxcnts = []
        minArea = None
        cntAreas = []
        cntDict = dict()

        if len(cnts) >= 4:
            for i in range(len(cnts)):
                cntAreas.append( (cv2.contourArea(cnts[i]),cnts[i]) )

            cntAreas.sort(key = lambda tup:tup[0], reverse = True)

            index = 0
            for x,y in cntAreas:
                maxcnts.append(y)

                index += 1
                if(index == 4):
                    break

            for i in range(4):
                M = cv2.moments(maxcnts[i])
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                centers.append(center)
            
            bottom_right_pt = None
            more_x = 2
            more_y = 2
            for i in range(len(centers)):
                x_counter = 0
                y_counter = 0
                for j in range(len(centers)):
                    if centers[i][0] > centers[j][0]:
                        x_counter += 1
                    if centers[i][1] > centers[j][1]:
                        y_counter += 1
                if x_counter >= more_x and y_counter >= more_y:
                    more_x = x_counter
                    more_y = y_counter
                    bottom_right_pt = centers[i]

            top_left_pt = None
            more_x = 2
            more_y = 2
            for i in range(len(centers)):
                x_counter = 0
                y_counter = 0
                for j in range(len(centers)):
                    if centers[i][0] < centers[j][0]:
                        x_counter += 1
                    if centers[i][1] < centers[j][1]:
                        y_counter += 1
                if x_counter >= more_x and y_counter >= more_y:
                    more_x = x_counter
                    more_y = y_counter
                    top_left_pt = centers[i]

            cv2.circle(frame, bottom_right_pt, 10, (0,0,0), thickness=-1)
            cv2.circle(frame, top_left_pt, 10, (0,0,0), thickness=-1)

            adj_pt_1 = None
            adj_pt_2 = None
            for point in centers:
                if point != bottom_right_pt and point != top_left_pt:
                    if adj_pt_1 == None:
                        adj_pt_1 = point
                    else:
                        adj_pt_2 = point

            # print bottom_right_pt
            # print '1', adj_pt_1
            # print top_left_pt
            # print '2', adj_pt_2
            points = np.array([bottom_right_pt, adj_pt_1, top_left_pt, adj_pt_2])

            bad_point = False
            for pt in points:
                if pt == None:
                    bad_point = True
            if not bad_point:
                cv2.polylines(frame,np.int32([points]), True, (0,0,0),3)

            # bottom_pt = None
            # min_y = 0
            # for point in centers:
            #     if point[1] > min_y:
            #         min_y = point[1]
            #         bottom_pt = point

            # cv2.circle(frame, bottom_pt, 10, (0,0,0), thickness=-1)

            # top_pt = None
            # max_y = float("inf")
            # for point in centers:
            #     if point[1] < max_y:
            #         max_y = point[1]
            #         top_pt = point
            # cv2.circle(frame, top_pt, 10, (0,0,0), thickness=-1)

            # adj_pt_1 = None
            # adj_pt_2 = None
            # for point in centers:
            #     if point != bottom_pt and point != top_pt:
            #         if adj_pt_1 == None:
            #             adj_pt_1 = point
            #         else:
            #             adj_pt_2 = point

            # print bottom_pt
            # print '1', adj_pt_1
            # print top_pt
            # print '2', adj_pt_2
            # points = np.array([bottom_pt, adj_pt_1, top_pt, adj_pt_2])
            # cv2.polylines(frame,np.int32([points]), True, (0,0,0),3)

            # print centers

        cv2.imshow("Mask", mask)
        cv2.imshow('edges', edges)
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF
     
        # if the 'q' key is pressed, stop the loop
        if key == ord("q"):
            break
    # cleanup the camera and close any open windows
    camera.release()
    cv2.destroyAllWindows()

def cartesian_distance(pt1, pt2):
    y1 = pt1[0][1]
    x1 = pt1[0][0]
    y2 = pt2[0][1]
    x2 = pt2[0][0]
    return math.sqrt((x1-x2)**2 + (y1-y2)**2)

if __name__ == '__main__':
    program()