import cv2
import numpy as np
import glob
from matplotlib import pyplot as plt


cap = cv2.VideoCapture(0)

images = glob.glob('*.jpg')

#for fname in images:
while(True):

    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_blue = np.array([90,140,50])
    upper_blue = np.array([110,255,255])

    lower_green = np.array([30, 60, 50])
    #lower_green = np.array([30, 60, 30])
    upper_green = np.array([75,255,255])
    #lower_green = np.array([30, 50, 30])
    #upper_green = np.array([64,255,255])




    #Create a binary image, where anything blue appears white and everything else is black
    mask_green = cv2.inRange(hsv, lower_green, upper_green)
    mask_green = cv2.inRange(hsv, lower_blue, upper_blue)
        #Get rid of background noise using erosion and fill in the holes using dilation and erode the final image on last time
    cv2.imshow('mask_original',mask_green)
    element = cv2.getStructuringElement(cv2.MORPH_RECT,(5,5)) 
    mask_green = cv2.erode(mask_green, None, iterations =2)
    mask_green = cv2.dilate(mask_green,None,iterations=2)
    """
    mask_green = cv2.dilate(mask_green, None, iterations=1)
    mask_green = cv2.erode(mask_green, None, iterations =1)
    mask_green = cv2.dilate(mask_green, None, iterations=1)
    mask_green = cv2.erode(mask_green, None, iterations =1)
"""
    """
    element = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
    #mask_green = cv2.erode(mask_green,element, iterations=1)
    mask_green = cv2.dilate(mask_green,element,iterations=1)
    element = cv2.getStructuringElement(cv2.MORPH_RECT,(5,5))   
    mask_green = cv2.erode(mask_green,element, iterations =2)

    element = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
    mask_green = cv2.erode(mask_green,element, iterations =2)
    element = cv2.getStructuringElement(cv2.MORPH_RECT,(5,5))
    mask_green = cv2.dilate(mask_green,element,iterations=2)
"""
        
    #mask = mask_blue
    #mask = mask_blue + mask_pink
    mask = mask_green
    edges = cv2.Canny(mask,100,200, 3, 3)
    minlinelength = 50
    maxlinegap = 10
    linevote = 55
    lines = cv2.HoughLines(edges, 1.5, np.pi/180, linevote, maxlinegap)
    
    if lines is not None:
        """
        for x1,y1,x2,y2 in lines[0]:
            cv2.line(frame,(x1,y1),(x2,y2),(0,255,0),2)
        """
        reference_points = []
        points = []
        test_points = []
        for rho,theta in lines[0]:
            #print rho
            a = np.cos(theta)
            b = np.sin(theta)
            #print theta
            x0 = a*rho
            y0 = b*rho
            x1 = int(x0 + 1000*(-b))
            y1 = int(y0 + 1000*(a))
            x2 = int(x0 - 1000*(-b))
            y2 = int(y0 - 1000*(a))
            reference_points.append([x0, y0])
            points.append([x1, y1, x2, y2])
            test_points.append([x0, y0, x1, y1, x2, y2])
        threshold = 30
        group1 = []
        group1_index = []
        group2 = []
        group2_index = []
        group3 = []
        group3_index = []
        group4 = []
        group4_index = []
        test_points.sort(key = lambda x: x[0])
        for i, point in enumerate(test_points):
            if len(group1) == 0:
                group1.append(test_points[i])
                group1_index.append(i)
            else:
                if abs(group1[0][0] - test_points[i][0]) < threshold and abs(group1[0][1] - test_points[i][1]) < threshold:
                    group1.append(test_points[i])
                    group1_index.append(i)

            if i not in group1_index:
                if len(group2) == 0:
                    group2.append(test_points[i])
                    group2_index.append(i)
                else:
                    if abs(group2[0][0] - test_points[i][0]) < threshold and abs(group2[0][1] - test_points[i][1]) < threshold:
                        group2.append(test_points[i])
                        group2_index.append(i)

            if i not in group2_index and i not in group1_index:
                if len(group3) == 0:
                    group3.append(test_points[i])
                    group3_index.append(i)
                else:
                    if abs(group3[0][0] - test_points[i][0]) < threshold and abs(group3[0][1] - test_points[i][1]) < threshold:
                        group3.append(test_points[i])
                        group3_index.append(i)
            if i not in group2_index and i not in group1_index and i not in group3_index:
                if len(group4) == 0:
                    group4.append(test_points[i])
                    group4_index.append(i)
                else:
                    if abs(group4[0][0] - test_points[i][0]) < threshold and abs(group4[0][1] - test_points[i][1]) < threshold:
                        group4.append(test_points[i])
                        group4_index.append(i)



        sum1 = [0, 0, 0, 0]
        point1 = [0, 0, 0, 0]
        for test_point in group1:
            sum1[0] += test_point[2]
            sum1[1] += test_point[3]
            sum1[2] += test_point[4]
            sum1[3] += test_point[5]
        for i in range(len(sum1)):
            point1[i] = sum1[i]/len(group1)

        sum2 = [0, 0, 0, 0]
        point2 = [0, 0, 0, 0]
        for test_point in group2:
            sum2[0] += test_point[2]
            sum2[1] += test_point[3]
            sum2[2] += test_point[4]
            sum2[3] += test_point[5]
        for i in range(len(sum2)):
            if len(group2) != 0:
                point2[i] = sum2[i]/len(group2)

        sum3 = [0, 0, 0, 0]
        point3 = [0, 0, 0, 0]
        for test_point in group3:
            sum3[0] += test_point[2]
            sum3[1] += test_point[3]
            sum3[2] += test_point[4]
            sum3[3] += test_point[5]
        for i in range(len(sum3)):
            if len(group3) != 0:
                point3[i] = sum3[i]/len(group3)

        sum4 = [0, 0, 0, 0]
        point4 = [0, 0, 0, 0]
        for test_point in group4:
            sum4[0] += test_point[2]
            sum4[1] += test_point[3]
            sum4[2] += test_point[4]
            sum4[3] += test_point[5]
        for i in range(len(sum4)):
            if len(group4) != 0:
                point4[i] = sum4[i]/len(group4)

        cv2.line(frame,(point1[0],point1[1]),(point1[2],point1[3]),(0,0,255),2)
        cv2.line(frame,(point2[0],point2[1]),(point2[2],point2[3]),(0,255,0),2)
        cv2.line(frame,(point3[0],point3[1]),(point3[2],point3[3]),(255,0,0),2)
        cv2.line(frame,(point4[0],point4[1]),(point4[2],point4[3]),(255,255,255),2)
        """    #cv2.line(frame,(test_point[2],test_point[3]),(test_point[4],test_point[5]),(0,0,255),2)
        for test_point in group2:
            cv2.line(frame,(test_point[2],test_point[3]),(test_point[4],test_point[5]),(0,255,0),2)
        for test_point in group3:
            cv2.line(frame,(test_point[2],test_point[3]),(test_point[4],test_point[5]),(255,0,0),2)
        for test_point in group4:
            cv2.line(frame,(test_point[2],test_point[3]),(test_point[4],test_point[5]),(255,255,255),2)

        for point in reference_points:
            cv2.circle(frame, (point[0], point[1]), 5, (0,255,0))
        """
        #for point in test_points:
        #    cv2.line(frame,(point[2],point[3]),(point[4],point[5]),(0,0,255),2)
        

    cv2.imshow('mask filter',mask)
    cv2.imshow('frame + HoughLines', frame)
    cv2.imshow('edges', edges)


    k = cv2.waitKey(5) & 0xFF
        #If escape is pressed close all windows
    if k == 27:
        break
cap.release()
cv2.destroyAllWindows()