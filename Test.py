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
    # greenLower = (30,60,30)
    # greenUpper = (64, 255, 255)

    # blueLower = (90,140,50)
    # blueUpper = (110, 255, 255)
    # blueLower = (60,30,30)
    # blueUpper = (150,120,150)
    # blueLower = (90,140,50)
    # blueUpper = (220,255,255)



    # blueLower = (80,80,70) #(80,8,130)
    # blueUpper = (235,200,230) #(170,80,240)

    # blueLower = (80,50,120) #pink
    # blueUpper = (170,100,210)

    blueLower = (50,50,66) #green
    blueUpper = (110,135,170)

    # red1Lower = (-10,80,110) #red1
    # red1Upper = (19,160,200)

    # red2Lower = (165,60,110) #red2
    # red2Upper = (190,100,170)

    # blueLower = (30,30,130) #yellow
    # blueUpper = (48,150,220)

    # hsv1 = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # blueLower = cv2.cvtColor(hsv1,cv2.COLOR_BGR2HSV)
    # blueUpper = cv2.cvtColor(hsv1,cv2.COLOR_BGR2HSV)

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
        # blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        # print '1', frame[300,300]
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        print hsv[300,300]
        cv2.circle(frame, (300,300), 10, (0,0,0), thickness=-1)
        # construct a mask for the color "blue", then remove any imperfections
        mask_blue = cv2.inRange(hsv, blueLower, blueUpper)
        mask_blue = cv2.erode(mask_blue, None, iterations=3)
        mask_blue = cv2.dilate(mask_blue, None, iterations=2)
        mask = mask_blue
        # blurred = cv2.blur(mask,(10,10))

        edges = cv2.Canny(mask,100,200, apertureSize = 3)

        ##edges detecting, accuracy, angle, minlinelength, maxlinegap
        minlinelength = 60
        maxlinegap = 10
        linevote = 65
        # linevote = 50
        # lines = cv2.HoughLines(edges, 1.5, np.pi/180, linevote)

        # if lines is not None:
        #     for rho,theta in lines[0]:
        #         a = np.cos(theta)
        #         b = np.sin(theta)
        #         x0 = a*rho
        #         y0 = b*rho
        #         x1 = int(x0 + 1000*(-b))
        #         y1 = int(y0 + 1000*(a))
        #         x2 = int(x0 - 1000*(-b))
        #         y2 = int(y0 - 1000*(a))

        #         cv2.line(frame,(x1,y1),(x2,y2),(0,0,255),2)

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

            cntAreas.sort(key = lambda tup:tup[0])

            index = 0
            for x,y in cntAreas:
                maxcnts.append(y)

                index += 1
                if(index == 4):
                    break

                # cnt = max(cnts, key=cv2.contourArea)
                # epsilon = 0.02*cv2.arcLength(cnt,False)
                # approx = cv2.approxPolyDP(cnt,epsilon,False)
                # points = np.array(approx)

            # if len(approx) < 7:
            #     # print approx
            #     point_list = []
            #     for i in range(len(approx)-1):
            #         if cartesian_distance(approx[i],approx[i+1]) > 100:
            #             point_list.append(approx[i][0])
            #     for x in point_list:
            #         print x,
            #     print ""

            #     cv2.polylines(frame,np.int32([points]), True, (0,0,0),3)
                # cv2.drawContours(frame, [cnt], -1, (0,0,0),3)
            for i in range(4):
                M = cv2.moments(maxcnts[i])
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                centers.append(center)
        
            cv2.polylines(frame,np.int32([centers]), True, (0,0,0),3)
        # update the points queue
        # pts.appendleft(center)
        # # loop over the set of tracked points
        # for i in xrange(1, len(pts)):
        #     # if either of the tracked points are None, ignore them
        #     if pts[i - 1] is None or pts[i] is None:
        #         continue
        #     # otherwise, compute the thickness of the line and
        #     # draw the connecting lines
        #     thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
        #     cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)
     
        # show the frame to our screen
        
        # cv2.imshow('Blur', blurred)
        cv2.imshow("Mask", mask)
        # cv2.imshow('edges', edges)
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF
     
        # if the 'q' key is pressed, stop the loop
        if key == ord("q"):
            break
     
    # cleanup the camera and close any open windows
    camera.release()
    cv2.destroyAllWindows()

def cartesian_distance(pt1, pt2):
    # print pt1
    # print pt2
    y1 = pt1[0][1]
    x1 = pt1[0][0]
    y2 = pt2[0][1]
    x2 = pt2[0][0]
    return math.sqrt((x1-x2)**2 + (y1-y2)**2)

if __name__ == '__main__':
    program()