"""
#GetReal

Viewing CAD Models in 3D space before you fabricate

Software Design Final Project Spring 2016

Kevin Zhang, Cedric Kim, Daniel Daugherty, Kevin Guo

Augmented Reality, allows one to project any CAD stl file into 3D space onto a marker, and be able to view it in Virtual Reality
"""

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import cv2
import numpy as np
from threading import Thread
from PIL import Image
from collections import deque
import argparse
import imutils
import math
from stl import mesh
import glob
import random
import os
import struct
import sys


class Contours(object):
    """
    class for detecting contours of tracker
    """


    def __init__(self):
        self.contour_list = []
        self.centers = []

    # creates contours sorted by area size (biggest to smallest) from contour_information
    def update_contours(self, contour_information):
        """
        updates the contours of the tracker, maintains orientation and location of tracker
        """

        # grab all the contour information and store the actual contours into contours
        contours = contour_information[0]
        self.contour_list = []

        # if the number of contours is atleast 4,
        if len(contours) >= 4:
            for contour in contours:
                # store the area of the contours and the contours in the same list
                self.contour_list.append((cv2.contourArea(contour),contour))

        # sort the contours by area
        self.contour_list.sort(key = lambda x: x[0], reverse=True)


class Centers(object):
    """
    class for detecting the center of each blue square on the tracker
    """



    def __init__(self):
        self.corners = []
        self.main_corner = (0,0)
        self.main_corner_index = -1
        self.vectors = []
        self.final_corners = []
        self.distances = []
        self.threshold = 5
        self.num_black_corners = 0
        self.is_tracking = True


    def update_centers(self, contour_list, mask_black):
        """
        takes in a list of contours and a masked black frame to creates a tuple of (x,y) coordinates for the center of each contour
        """

        # if there are contours in the list,
        if len(contour_list) > 0:
            self.corners = []

            for i in range(4):
                # create a moment (used to find center of contour)
                M = cv2.moments(contour_list[i][1])
                if M["m00"] != 0 and M["m00"] != 0:
                    # creates a (x, y) tuple for the contour
                    center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                    # add the center to a list
                    self.corners.append(center)
            self.num_black_corners = 0 

            for i, center in enumerate(self.corners):
                    # grab the color at the center of the black mask,
                color = mask_black[center[1], center[0]]
                    # if the color at the center is black
                if color == 255:
                    self.num_black_corners += 1

                    # store that information
                    self.main_corner_index = i
                    self.main_corner = center

            if self.num_black_corners == 1:
                self.is_tracking = True
            else:
                self.is_tracking = False

    def update_vectors(self):
        """
        creates vectors (x,y) reference tuples from the main corner (black corner)
        """


        self.vectors = []

        # for each corner in corners,
        for i, corner in enumerate(self.corners):
            main_corner_x = self.main_corner[0]
            main_corner_y = self.main_corner[1]
            corner_x = corner[0]
            corner_y = corner[1]

            # if the main corner isnt the current index,
            if self.main_corner_index != i:
                # create a vector and add it to a list
                self.vectors.append((corner_x - main_corner_x, corner_y - main_corner_y))


    def reorganize_centers(self):
        """
        reorganizes the centers so that they are in correct relation to each other       
        """

    
        # final_corners is the final list of organized corners
        self.final_corners = []
        self.final_corners.append(self.main_corner)
        corners = []

        # for each corner, only add the corner if it isnt the main corner
        if len(self.corners) == 4:
            for i, corner in enumerate(self.corners):
                if not(self.main_corner[0] == corner[0] and self.main_corner[1] == corner[1]):
                    corners.append(corner)

            # save the fourth corner
            corner_4 = return_point_4(self.main_corner, corners[0], corners[1], corners[2])

            # find the quadrant clockwise to the quadrant the corners are occupying
            quadrant = return_closest_quadrant(self.main_corner, corners[0], corners[1], corners[2])
            potential_points = []

            # for each corner (this finds potential points for corner_2)
            for corner in corners:
                # if the corner is not corner 4,
                if not (corner[0] == corner_4[0] and corner[1] == corner_4[1]):
                    check_quadrant = quadrant + 1
                    if check_quadrant == 5:
                        check_quadrant = 1
                    # if the corner is within the quadrant after check quadrant,
                    if check_quadrant == return_quadrant((corner[0] - self.main_corner[0], corner[1] - self.main_corner[1])):
                        ## add this to potential_points
                        potential_points.append(corner)

            corner_2 = (0,0)
            corner_3 = (0,0)

            # pass potential points into return_point_2
            if len(potential_points) > 0:
                corner_2 = return_point_2(quadrant, self.main_corner, potential_points)

            for corner in corners:
                if not (corner[0] == corner_4[0] and corner[1] == corner_4[1]):
                    if not (corner[0] == corner_2[0] and corner[1] == corner_2[1]):
                        corner_3 = corner

            self.final_corners.append(corner_2)
            self.final_corners.append(corner_3)
            self.final_corners.append(corner_4)


    def distance_of_corners(self, final_corners):
        """
        sets self.distances to have all the distances between each corner
        """

        self.distances = []
        for i in range(len(final_corners)):
            if i == 3:
                self.distances.append(get_distance(final_corners[i], final_corners[0]))
            else:
                self.distances.append(get_distance(final_corners[i], final_corners[i+1]))


    def bool_is_tracking(self):
        """
        determines whether the tracker is still tracking the markers based on a threshold
        """

        self.distance_of_corners(self.final_corners)
        self.distances.sort()

        test_value = (self.distances[3] + self.distances[2])/ self.distances[0]

        if test_value > self.threshold:
            self.is_tracking = False


def return_point_2(quadrant, main_corner, potential_points):
    """
    checks the angle in order to find corner_2
    """


    # if the length is one, return it
    if len(potential_points) == 1:
        return potential_points[0]

    # create reference points in order to find the angle
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
        
        # if the angle is smaller, return that point
        if angle_1 < angle_2:
            return potential_points[0]
        else:
            return potential_points[1]


def return_closest_quadrant(main_corner, point_1, point_2, point_3):
    """
    creates empty quadrants and uses return_most_clockwise_quadrant
    """


    reference_point_1 = (point_1[0] - main_corner[0], point_1[1] - main_corner[1])
    reference_point_2 = (point_2[0] - main_corner[0], point_2[1] - main_corner[1])
    reference_point_3 = (point_3[0] - main_corner[0], point_3[1] - main_corner[1])
    quadrants = []
    quadrants.append(return_quadrant(reference_point_1))
    quadrants.append(return_quadrant(reference_point_2))
    quadrants.append(return_quadrant(reference_point_3))
    empty_quadrants = []
    
    # find quadrants the points are not in
    for i in range(1, 5):
        if i not in quadrants:
            empty_quadrants.append(i)

    return return_most_clockwise_quadrant(empty_quadrants)


def return_most_clockwise_quadrant(empty_quadrants):
    """
    returns the most clockwise quadrant the points are not in
    """


    if len(empty_quadrants) == 1:
        return empty_quadrants[0]
    elif len(empty_quadrants) == 2:
        if empty_quadrants[0] == 1 and empty_quadrants[1] == 4:
            return 1
        else:
            return empty_quadrants[1]

    elif len(empty_quadrants) == 3:
        if empty_quadrants[0] == 1 and empty_quadrants[1] == 3 and empty_quadrants[2] == 4:
            return 1
        elif empty_quadrants[0] == 1 and empty_quadrants[1] == 2 and empty_quadrants[2] == 4:
            return 2
        else:
            return empty_quadrants[2]

def return_quadrant(point):
    """
    returns the quadrant that the inputted point is in
    """

    if is_positive(point[0]) and not is_positive(point[1]):
        return 1
    elif not is_positive(point[0]) and not is_positive(point[1]):
        return 2
    elif not is_positive(point[0]) and is_positive(point[1]):
        return 3
    else:
        return 4


def return_point_4(main_corner, point_1, point_2, point_3):
    """
    returns the fourth corner
    """


    angle_1 = get_angle(main_corner, point_1, point_2)
    angle_2 = get_angle(main_corner, point_1, point_3)
    angle_3 = get_angle(main_corner, point_2, point_3)

    # find the angle between the corners, only one is greater that the other
    if(angle_1 > angle_2 and angle_1 > angle_3):
        return point_3
    elif(angle_2 > angle_3):
        return point_2
    else:
        return point_1

def get_distance(point_1, point_2):
    """
    the distance formula
    """

    return math.sqrt((point_1[0] - point_2[0])**2 + (point_1[1] - point_2[1])**2)

def get_angle(main_corner, point_1, point_2):
    """
    the law of cosines
    """

    c = get_distance(point_1, point_2)
    b = get_distance(main_corner, point_2)
    a = get_distance(main_corner, point_1)
    return math.fabs(math.acos((c**2 - a**2 - b**2)/(-2*a*b)))

def is_positive(x):
    """
    checks if x is positive
    """

    return (x >= 0)


class Camera(object):
    """
    class to calibrate camera for OpenCV tracking
    """


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
        self.tvecs = None
        self.draw_axis = False
        self.view_matrix = False

    def grab_frame_information(self, frame, corners):
        """
        arrays to store object points and image points from all the images.
        """

        self.objpoints.append(self.objp)
        self.imgpoints.append(np.array(corners, dtype = np.float32))

    def calibrate_camera(self, gray):
        """
        gets the information for calibrating the camera
        """
        self.ret, self.mtx, self.dist, self.rvecs, self.tvecs = cv2.calibrateCamera(self.objpoints, self.imgpoints, gray.shape[::-1],None,None)


class createpoint:
    """
    class for a 3d point
    """

    def __init__(self,p,c=(1,0,0)):
        self.point_size=0.5
        self.color=c
        self.x=p[0]
        self.y=p[1]
        self.z=p[2]
      
    def glvertex(self):
        glVertex3f(self.x,self.y,self.z)


class createtriangle:
    """
    class for a 3d face on a model
    """


    points=None
    normal=None

    def __init__(self,p1,p2,p3,n=None):

        # 3 points of the triangle
        self.points=createpoint(p1),createpoint(p2),createpoint(p3)
      
        # triangles normal
        self.normal=createpoint(self.calculate_normal(self.points[0],self.points[1],self.points[2]))#(0,1,0)#
  
    def calculate_vector(self,p1,p2):
        """
        calculate vector / edge
        """

        return -p1.x+p2.x,-p1.y+p2.y,-p1.z+p2.z
    
    def calculate_normal(self,p1,p2,p3):
        """
        calculate the cross product returns a vector  
        """

        a=self.calculate_vector(p3,p2)
        b=self.calculate_vector(p3,p1)
        return self.cross_product(a,b)
  
    def cross_product(self,p1,p2):
        """
        returns the cross_product of the triangle
        """

        return (p1[1]*p2[2]-p2[1]*p1[2]) , (p1[2]*p2[0])-(p2[2]*p1[0]) , (p1[0]*p2[1])-(p2[0]*p1[1])


class loader:
    """
    class to load stl file
    """


    model=[]
      
    def get_triangles(self):
        """
        return the faces of the triangles
        """

        if self.model:
            for face in self.model:
                yield face

    def draw(self):
        """
        draw the models faces
        """


        global color
        # draws each stl triangle as an OpenGL triangle
        glBegin(GL_TRIANGLES)

        for tri in self.get_triangles():
            if color == 0:
                glColor3f(.73, .74, .8)
            elif color == 1:
                glColor3f(212.0/255,175.0/255,55.0/255)
            elif color == 2:
                glColor3f(220.0/255,20.0/255,60.0/255)
            elif color == 3:
                glColor3f(0,191.0/255,255/255)
            elif color == 4:
                glColor3f(50.0/255,205.0/255,50.0/255)
            elif color == 5:
                glColor3f(138.0/255,43.0/255,226.0/255)
            elif color == 6:
                r = random.randint(0,255)
                g = random.randint(0,255)
                b = random.randint(0,255)
                glColor3f(r/255.0, g/255.0, b/255.0)
            glNormal3f(tri.normal.x,tri.normal.y,tri.normal.z)
            glVertex3f(tri.points[0].x,tri.points[0].y,tri.points[0].z)
            glVertex3f(tri.points[1].x,tri.points[1].y,tri.points[1].z)
            glVertex3f(tri.points[2].x,tri.points[2].y,tri.points[2].z)
        glColor3f(1.0, 1.0, 1.0)
        glEnd()
   

    def load_stl(self,filename):
        """
        detects if the file is a text file or binary file
        """


        # read start of file to determine if its a binay stl file or a ascii stl file
        fp=open(filename,'rb')
        h=fp.read(80)
        type=h[6:13]
        print type
        fp.close()

        if type=='Default':
            print "reading text file"+str(filename)
            self.load_text_stl(filename)
        else:
            print "reading binary stl file "+str(filename,)
            self.load_binary_stl(filename)



    def load_text_stl(self,filename):
        """
        read text stl match keywords to grab the points to build the model
        """


        fp=open(filename,'r')

        for line in fp.readlines():
            words=line.split()
            if len(words)>0:
                if words[0]=='solid':
                    self.name=words[1]

                if words[0]=='facet':
                    center=[0.0,0.0,0.0]
                    triangle=[]
                    normal=(eval(words[2]),eval(words[3]),eval(words[4]))
                  
                if words[0]=='vertex':
                    triangle.append((eval(words[1]),eval(words[2]),eval(words[3])))
                  
                  
                if words[0]=='endloop':
                    #make sure we got the correct number of values before storing
                    if len(triangle)==3:
                        self.model.append(createtriangle(triangle[0],triangle[1],triangle[2],normal))
        fp.close()


    def load_binary_stl(self,filename):
        """
        loads binary stl file using the struct library to read in and convert binary data into a format we can use
        """


        fp=open(filename,'rb')
        h=fp.read(80)

        l=struct.unpack('I',fp.read(4))[0]
        count=0
        while True:
            try:
                p=fp.read(12)
                if len(p)==12:
                    n=struct.unpack('f',p[0:4])[0],struct.unpack('f',p[4:8])[0],struct.unpack('f',p[8:12])[0]
                  
                p=fp.read(12)
                if len(p)==12:
                    p1=struct.unpack('f',p[0:4])[0],struct.unpack('f',p[4:8])[0],struct.unpack('f',p[8:12])[0]

                p=fp.read(12)
                if len(p)==12:
                    p2=struct.unpack('f',p[0:4])[0],struct.unpack('f',p[4:8])[0],struct.unpack('f',p[8:12])[0]

                p=fp.read(12)
                if len(p)==12:
                    p3=struct.unpack('f',p[0:4])[0],struct.unpack('f',p[4:8])[0],struct.unpack('f',p[8:12])[0]

                new_tri=(n,p1,p2,p3)

                if len(new_tri)==4:
                    tri=createtriangle(p1,p2,p3,n)
                    self.model.append(tri)
                count+=1
                fp.read(2)

                if len(p)==0:
                    break
            except EOFError:
                break
        fp.close()


class Webcam:
    """
    class for streaming webcam images using OpenCV
    """

  
    def __init__(self):

        # set webcam video feed
        self.video_capture = cv2.VideoCapture(1)
        self.current_frame = self.video_capture.read()[1]
          
    def start(self):
        """
        create thread for capturing images
        """

        Thread(target=self._update_frame, args=()).start()
  
    def _update_frame(self):
        """
        callback function for updating the next frame
        """

        while(True):
            self.current_frame = self.video_capture.read()[1]
                  
    def get_current_frame(self):
        """
        get the current frame
        """

        return self.current_frame


class AugmentedReality():
    """
    class for integrating OpenCV tracking with OpenGL rendering
    """

 
    # constants
    INVERSE_MATRIX = np.array([[ 1.0, 1.0, 1.0, 1.0],
                               [-1.0,-1.0,-1.0,-1.0],
                               [-1.0,-1.0,-1.0,-1.0],
                               [ 1.0, 1.0, 1.0, 1.0]])

    def __init__(self):

        # initialise webcam and start thread
        self.webcam = Webcam()
        self.webcam.start()
        self.model1=loader()

        file_name = raw_input("enter stl file name\n")
        exact_file_name = glob.glob(os.path.abspath('')+'/STL/'+ file_name+'*')
        print exact_file_name

        self.model1.load_stl(exact_file_name[0])
 
        # textures
        self.texture_background = None
        self.is_window_1 = True
 

    def _init_gl(self, Width, Height):
        """
        calibrate the webcam to detect tracker and initialize OpenGL
        """


        # global variables to handle OpenCV tracking
        global contour
        global center
        global camera

        # initialize objects to handle OpenCV tracking
        contour = Contours()
        center = Centers()
        camera = Camera()

        # varibales to handle tracking
        blueLower = np.array([90,100,10])
        blueUpper = np.array([150,255,255])
        blackLower = np.array([0,0,0])
        blackUpper = np.array([180, 255, 150])


        # calibrate webcam to detect tracker

        images = glob.glob(os.path.abspath('') + '/Pictures/*cut*.png')


        for fname in images:
            img = cv2.imread(fname)
            img = cv2.flip(img, 1)
            hsv_frame = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

            # construct a mask for the color "blue", then remove any imperfections
            mask_blue = cv2.inRange(hsv_frame, blueLower, blueUpper)
            mask_blue = cv2.erode(mask_blue, None, iterations=1)
            mask_blue = cv2.dilate(mask_blue, None, iterations=1)

            # create black mask for tracking corner
            mask_black = cv2.inRange(hsv_frame, blackLower, blackUpper)

            gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

            # creates information about the contours
            contour_information = cv2.findContours(mask_blue.copy(), cv2.RETR_CCOMP,
                cv2.CHAIN_APPROX_SIMPLE)

            # updates each of the elements in the classes
            contour.update_contours(contour_information)
            center.update_centers(contour.contour_list, mask_black)
            center.reorganize_centers()
            camera.grab_frame_information(img, center.final_corners)

        camera.calibrate_camera(gray)


        self._set_textures() 
    def _reload_stl(self):
        """
        Allows for the user to re-input a new stl on the spot
        """
        self.model1.model = []
        file_name = raw_input("enter stl file name\n")
        exact_file_name = glob.glob(os.path.abspath('')+'/STL/'+ file_name+'*')
        self.model1.load_stl(exact_file_name[0])
       
    def _set_textures(self):
        """
        makes the textures for both the background and the 3D rendered object
        """

        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClearDepth(1.0)
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(33.7, 1.3, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        
        # enable textures
        glEnable(GL_TEXTURE_2D)
        self.texture_background = glGenTextures(1) 

        # initialize OpenGL lighting functions
        glEnable(GL_LIGHTING)
        glEnable(GL_NORMALIZE)
        glShadeModel(GL_FLAT)
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClearDepth(1.0)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHT1)     
        
        # Ambient Light
        ambientColor = [0.2, 0.2, 0.2, 1.0]
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, ambientColor)

        # Light 1
        lightColor0 = [0.5, 0.5, 0.5, 1.0]
        lightPos0 = [30.0, -30.0, -30.0, 1.0]
        glLightfv(GL_LIGHT0, GL_DIFFUSE, lightColor0)
        glLightfv(GL_LIGHT0, GL_POSITION, lightPos0)

        # Light 2
        lightColor1 = [0.5, 0.5, 0.5, 1.0]
        lightPos1 = [-1.0, 0.5, 0.5, 0.0]
        glLightfv(GL_LIGHT1, GL_DIFFUSE, lightColor1)
        glLightfv(GL_LIGHT1, GL_POSITION, lightPos1)   


    def _draw_scene(self):
        """
        function continuously called by Glut to display the webcam feed and render the stl
        """


        glutSetWindow(self.window_id)

        # clear Screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
 
        # get image from webcam
        image = self.webcam.get_current_frame()
        image = cv2.flip(image,0)
        #image = cv2.flip(image,1)
 
        image_array = Image.fromarray(image)
        ix = image_array.size[0]
        iy = image_array.size[1]
        image_array = image_array.tostring("raw", "BGRX", 0, -1)

  

        # disable lighting and enable textures for background
        glDisable(GL_LIGHTING)  
        glEnable(GL_TEXTURE_2D)

        # create background texture
        glBindTexture(GL_TEXTURE_2D, self.texture_background)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexImage2D(GL_TEXTURE_2D, 0, 3, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_array)
        
        # draw background
        glBindTexture(GL_TEXTURE_2D, self.texture_background)
        glPushMatrix()
        glTranslatef(0.0,0.0,-30.0)
        self._draw_background()
        glPopMatrix()

        # enable Lighting and disable textures for stl
        glEnable(GL_LIGHTING)
        glDisable(GL_TEXTURE_2D)

        # handle glyph
        self._handle_glyph(image)

        glutSwapBuffers()

        glutSetWindow(self.window_id_2) 
        # clear Screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # get image from webcam
        image = self.webcam.get_current_frame()
        image = cv2.flip(image,0)
        #image = cv2.flip(image,1)


        # disable lighting and enable textures for background
        glDisable(GL_LIGHTING)  
        glEnable(GL_TEXTURE_2D)

        # create background texture
        glBindTexture(GL_TEXTURE_2D, self.texture_background)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexImage2D(GL_TEXTURE_2D, 0, 3, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_array)
        
        # draw background
        glBindTexture(GL_TEXTURE_2D, self.texture_background)
        glPushMatrix()
        glTranslatef(0.0,0.0,-30.0)
        self._draw_background()
        glPopMatrix()

        # enable Lighting and disable textures for stl
        glEnable(GL_LIGHTING)
        glDisable(GL_TEXTURE_2D)

        # handle glyph
        self._handle_glyph(image)
      
        # display window
        glutSwapBuffers()
 

    def _handle_glyph(self, image):
        """
        draws stl file on tracker
        """

 
        # attempt to detect tracker from OpenCV
        rvecs = None
        tvecs = None
        try:
            rvecs, tvecs = self.detect_glyph(image)
        except Exception as ex: 
            print(ex)
        
        # if there is no tracker, do not render anything
        if rvecs == None or tvecs == None: 
            return
 
        # build reference matrix from OpenCV
        rmtx = cv2.Rodrigues(rvecs)[0]
 
        view_matrix = np.array([[rmtx[0][0],rmtx[0][1],rmtx[0][2],tvecs[0]],
                                [rmtx[1][0],rmtx[1][1],rmtx[1][2],tvecs[1]],
                                [rmtx[2][0],rmtx[2][1],rmtx[2][2],tvecs[2]],
                                [0.0       ,0.0       ,0.0       ,1.0    ]])
 
        view_matrix = view_matrix * self.INVERSE_MATRIX
 
        view_matrix = np.transpose(view_matrix)
 
        # load reference matrix from OpenCV as drawing space for OpenGL
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity();
        gluPerspective(45, 1.3, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW);
        glPushMatrix()
        glLoadMatrixd(view_matrix)

        # rotates and scales the stl
        glRotatef(angle, 0, 0, 1.0)

        glScale(size, size, size)

        # draws stl
        self.model1.draw()
        glPopMatrix()

 
    def _draw_background(self):
        """
        streams webcam feed onto background of OpenGL window
        """


        # draws webcam image as a texture on an OpenGL quad
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity();
        gluPerspective(33.7, 1.3, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW);
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 1.0); glVertex3f(-12.0, -9.0, 0.0)
        glTexCoord2f(1.0, 1.0); glVertex3f( 12.0, -9.0, 0.0)
        glTexCoord2f(1.0, 0.0); glVertex3f( 12.0,  9.0, 0.0)
        glTexCoord2f(0.0, 0.0); glVertex3f(-12.0,  9.0, 0.0)
        glEnd( )


    def update(self, dt):
        """
        update function to handle the rotation of the stl file
        """


        # global variables for rotation of stl file
        global angle
        global turning
        global size
        global size_direction
        global restart

        # if the spacebar is pressed, the stl will start to rotate
        if turning:
            angle += 2.0
            if angle > 360.0:
                angle -= 360.0
        if size_direction == 1:
            size += .001
            size_direction = 0
        if size_direction == -1:
            size -= .001
            size_direction = 0
        if restart:
            self._reload_stl()
            restart = False
        # update position with global position
        glutPostRedisplay()
        glutTimerFunc(5, self.update, 0)
 

    def detect_glyph(self, image):
        """
        returns the rvecs and the tvecs of an image
        """


        # global variables for OpenCV tracking
        global camera
        global contour
        global center

        # format image for tracking
        frame = imutils.resize(image, width = 750)
        frame = cv2.flip(frame, 0)
        #frame = cv2.flip(frame, 1)

        # color space
        blueLower = np.array([90,100,10])
        blueUpper = np.array([150,255,255])
        blackLower = np.array([0,0,0])
        blackUpper = np.array([180, 255, 150])
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # construct a mask for the color "blue", then remove any imperfections
        mask_blue = cv2.inRange(hsv_frame, blueLower, blueUpper)
        mask_blue = cv2.erode(mask_blue, None, iterations=1)
        mask_blue = cv2.dilate(mask_blue, None, iterations=1)

        ## create black mask for tracking corner
        mask_black = cv2.inRange(hsv_frame, blackLower, blackUpper)

        # creates information about the contours`
        contour_information = cv2.findContours(mask_blue.copy(), cv2.RETR_CCOMP,
            cv2.CHAIN_APPROX_SIMPLE)

        # updates each of the elements in the classes
        contour.update_contours(contour_information)
        center.update_centers(contour.contour_list, mask_black)

        if len(center.corners) == 4:
            center.reorganize_centers()
        center.update_vectors()
        center.bool_is_tracking()

        # if the camera detects our tracker, it will return the rvecs and tvecs of the image
        if center.is_tracking:
            rvecs, tvecs, inliers = cv2.solvePnPRansac(camera.objp, np.array(center.final_corners, 
                dtype = np.float32), camera.mtx, camera.dist)

        # if not, return None
        else:
            rvecs = tvecs = None

        return rvecs, tvecs


    def keyboard(self,key,x,y):
        """
        handles keyboard inputs from the user
        """


        # global variable to handle rotation of stl
        global turning
        global size_direction
        global color
        global restart

        if key == chr(27):
            # if the esc key is pressed, the program will exit
            os._exit(0)
        if key == chr(32):
            # if spacebar is pressed, the stl file will start rotating
            turning = not turning
        if key == chr(107):
            size_direction = 1
        elif key == chr(109):
            size_direction = -1
        else:
            size_direction = 0
        if key == chr(49):
            color = 0
        if key == chr(50):
            color = 1
        if key == chr(51):
            color = 2
        if key == chr(52):
            color = 3
        if key == chr(53):
            color = 4    
        if key == chr(54):
            color = 5
        if key == chr(55):
            color = 6   
        if key == chr(114):
            restart = True
    
    def main(self):
        """
        setup and run OpenGL rendering with OpenCV tracking
        """


        # global variables for rotation of stl file
        global color
        global angle
        global turning
        global size
        global size_direction
        global restart

        # initialize global variables
        turning = False
        restart = False
        size_direction = 0
        size = .01
        angle = 30.0
        color = 0

        # initialize window size and Glut
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
        glutInitWindowSize(1300, 1060)
        glutInitWindowPosition(0, 0)
        self.window_id = glutCreateWindow("#GetREAL")
        self._set_textures()
        glutInitWindowSize(1300, 1060)
        glutInitWindowPosition(1200, 0)
        self.window_id_2 = glutCreateWindow("#GetREAL2")
        glutDisplayFunc(self._draw_scene)
        glutIdleFunc(self._draw_scene)
        glutKeyboardFunc(self.keyboard)
        glutTimerFunc(5, self.update, 0)
        self._init_gl(width, height)

        #glutFullScreen()

        # run Glut
        glutMainLoop()
  

if __name__ == '__main__':

    # screen aspect ratio
    width = 1280
    height = 720

    # run an instance of AugmentedReality 
    GetREAL = AugmentedReality()
    GetREAL.main()