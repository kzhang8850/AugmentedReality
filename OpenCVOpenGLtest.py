##Author: Cedric Kim, Kevin Guo
##Software design, spring 2016
##Augmented Reality
##program tracks blue squares and creates vectors

# import the necessary packages

#sudo pip install imutils
#sudo apt-get install Enum34
from collections import deque
import numpy
import numpy as np
import argparse
import imutils
import cv2
import math
from stl import mesh
import glob

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import os
import struct

import sys

global capture
capture = None


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
        self.distances = []
        self.threshold = 5
        self.num_black_corners = 0
        self.is_tracking = True

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
            self.num_black_corners = 0 
            for i, center in enumerate(self.corners):
                ## if the center is within the window range,
                # if center[0] < 600 and center[1] < 450:
                    ## grab the color at the center of the black mask,
                color = mask_black[center[1], center[0]]
                    ## if the color at the center is black
                if color == 255:
                    self.num_black_corners += 1
                    ## store that information
                    self.main_corner_index = i
                    self.main_corner = center
            if self.num_black_corners == 1:
                self.is_tracking = True
            else:
                self.is_tracking = False

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
        """reorganizes the centers so that they are in correct relation to each other"""
        ## final_corners is the final list of organized corners
        self.final_corners = []
        self.final_corners.append(self.main_corner)
        corners = []
        ## for each corner, only add the corner if it isnt the main corner
        if len(self.corners) == 4:
            for i, corner in enumerate(self.corners):
                if not(self.main_corner[0] == corner[0] and self.main_corner[1] == corner[1]):
                    corners.append(corner)
            ## save the fourth corner
            corner_4 = return_point_4(self.main_corner, corners[0], corners[1], corners[2])
            ## find the quadrant clockwise to the quadrant the corners are occupying
            quadrant = return_closest_quadrant(self.main_corner, corners[0], corners[1], corners[2])
            potential_points = []
            ## for each corner (this finds potential points for corner_2)
            for corner in corners:
                ## if the corner is not corner 4,
                if not (corner[0] == corner_4[0] and corner[1] == corner_4[1]):
                    check_quadrant = quadrant + 1
                    if check_quadrant == 5:
                        check_quadrant = 1
                    ## if the corner is within the quadrant after check quadrant,
                    if check_quadrant == return_quadrant((corner[0] - self.main_corner[0], corner[1] - self.main_corner[1])):
                        ## add this to potential_points
                        potential_points.append(corner)
            corner_2 = (0,0)
            corner_3 = (0,0)
            if len(potential_points) > 0:
                ## pass potential points into return_point_2
                corner_2 = return_point_2(quadrant, self.main_corner, potential_points)

            for corner in corners:
                if not (corner[0] == corner_4[0] and corner[1] == corner_4[1]):
                    if not (corner[0] == corner_2[0] and corner[1] == corner_2[1]):
                        corner_3 = corner
            self.final_corners.append(corner_2)
            self.final_corners.append(corner_3)
            self.final_corners.append(corner_4)
    def distance_of_corners(self, final_corners):
        """sets self.distances to have all the distances between each corner"""
        self.distances = []
        for i in range(len(final_corners)):
            if i == 3:
                self.distances.append(get_distance(final_corners[i], final_corners[0]))
            else:
                self.distances.append(get_distance(final_corners[i], final_corners[i+1]))
    def bool_is_tracking(self):
        self.distance_of_corners(self.final_corners)
        self.distances.sort()
        #print self.distances
        #if len(self.distances) == :
        test_value = (self.distances[3] + self.distances[2])/ self.distances[0]
        #print test_value
        if test_value > self.threshold:
            self.is_tracking = False



def return_point_2(quadrant, main_corner, potential_points):
    """checks the angle in order to find corner_2"""
    ## if the length is one, return it
    if len(potential_points) == 1:
        return potential_points[0]
    else:
        ## create reference points in order to find the angle
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
        ## if the angle is smaller, return that point
        if angle_1 < angle_2:
            return potential_points[0]
        else:
            return potential_points[1]

def return_closest_quadrant(main_corner, point_1, point_2, point_3):
    """creates empty quadrants and uses return_most_clockwise_quadrant"""
    reference_point_1 = (point_1[0] - main_corner[0], point_1[1] - main_corner[1])
    reference_point_2 = (point_2[0] - main_corner[0], point_2[1] - main_corner[1])
    reference_point_3 = (point_3[0] - main_corner[0], point_3[1] - main_corner[1])
    quadrants = []
    quadrants.append(return_quadrant(reference_point_1))
    quadrants.append(return_quadrant(reference_point_2))
    quadrants.append(return_quadrant(reference_point_3))
    empty_quadrants = []
    ## find quadrants the points are not in
    for i in range(1, 5):
        if i not in quadrants:
            empty_quadrants.append(i)
    return return_most_clockwise_quadrant(empty_quadrants)
    
def return_most_clockwise_quadrant(empty_quadrants):
    """returns the most clockwise quadrant the points are not in"""
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
    if is_positive(point[0]) and not is_positive(point[1]):
        return 1
    elif not is_positive(point[0]) and not is_positive(point[1]):
        return 2
    elif not is_positive(point[0]) and is_positive(point[1]):
        return 3
    else:
        return 4

def return_point_4(main_corner, point_1, point_2, point_3):
    """returns the fourth corner"""
    angle_1 = get_angle(main_corner, point_1, point_2)
    angle_2 = get_angle(main_corner, point_1, point_3)
    angle_3 = get_angle(main_corner, point_2, point_3)
    ## find the angle between the corners, only one is greater that the other
    ## this way we can find the corner diagonal to the main corner
    if(angle_1 > angle_2 and angle_1 > angle_3):
        return point_3
    elif(angle_2 > angle_3):
        return point_2
    else:
        return point_1

def get_distance(point_1, point_2):
    return math.sqrt((point_1[0] - point_2[0])**2 + (point_1[1] - point_2[1])**2)

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
        self.tvecs = None
        self.draw_axis = False
        self.view_matrix = False
    def grab_frame_information(self, frame, corners):
        # Arrays to store object points and image points from all the images.
        self.objpoints.append(self.objp)
        self.imgpoints.append(np.array(corners, dtype = np.float32))
        #print self.objp
        #print np.array(corners)
        #cv2.putText(frame, "Hi", (100,100), 
        #cv2.FONT_HERSHEY_PLAIN, 10, 255, thickness = 3)
    def calibrate_camera(self, gray):
        self.ret, self.mtx, self.dist, self.rvecs, self.tvecs = cv2.calibrateCamera(self.objpoints, self.imgpoints, gray.shape[::-1],None,None)
    def return_view_matrix(self, rvecs, tvecs):
        rmtx = cv2.Rodrigues(rvecs)[0]
        print rmtx
        view_matrix = np.array([[rmtx[0][0],rmtx[0][1],rmtx[0][2],-tvecs[0]],
                            [rmtx[1][0],rmtx[1][1],rmtx[1][2],-tvecs[1]],
                            [rmtx[2][0],rmtx[2][1],rmtx[2][2],-tvecs[2]],
                            [0.0       ,0.0       ,0.0       ,1.0    ]])
        # view_matrix = np.array([[rmtx[0][0],rmtx[0][1],rmtx[0][2],0],
        #                     [rmtx[1][0],rmtx[1][1],rmtx[1][2],0],
        #                     [rmtx[2][0],rmtx[2][1],rmtx[2][2],0],
        #                     [tvecs[0],tvecs[1],tvecs[2],1.0]])
        inverse_matrix = np.array([[ 1.0, 1.0, 1.0, 1.0],
                                   [-1.0,-1.0,-1.0,-1.0],
                                   [-1.0,-1.0,-1.0,-1.0],
                                   [ 1.0, 1.0, 1.0, 1.0]])
        # view_matrix = view_matrix * inverse_matrix
 
        view_matrix = np.transpose(view_matrix)
        return view_matrix
def draw_axis(frame, corner, imgpts):
    #corner = tuple(corners[0].ravel())
    #print corner
    imgpts = np.int32(imgpts).reshape(-1,2)
    #cv2.drawContours(frame, [imgpts], -1, (255), -3)
    #print imgpts
    cv2.line(frame, corner, tuple(imgpts[0].ravel()), (255,0,0), 5)
    cv2.line(frame, corner, tuple(imgpts[1].ravel()), (0,255,0), 5)
    cv2.line(frame, corner, tuple(imgpts[2].ravel()), (0,0,255), 5)

def draw_cube(frame, corner, imgpts):

    imgpts = np.int32(imgpts).reshape(-1,2)
    # draw ground floor in green
    cv2.drawContours(frame, [imgpts[:4]],-1,(255),3)

    # draw pillars in blue color
    for i,j in zip(range(4),range(4,8)):
        cv2.line(frame, tuple(imgpts[i]), tuple(imgpts[j]),(255),3)

    # draw top layer in red color

    cv2.drawContours(frame, [imgpts[4:]],-1,(255),3)

def draw_mesh(frame, imgpts):
    # for triangle in mesh_grid:
    #     print triangle
    imgpts = np.int32(imgpts).reshape(-1,2)
    for i in range(len(imgpts)):
        if (i+1)%3 == 0:
            #print int(255*(i/float(len(imgpts))))
            cv2.drawContours(frame, [imgpts[i-2:i+1]], -1, (int(255*(i/float(len(imgpts)))), int(255*(i/float(len(imgpts)))), int(255*(i/float(len(imgpts))))), -3)
    #cv2.drawContours(frame, [imgpts], -1, (255), 3)
def create_mesh_grid(mesh):
    mesh_grid = []
    scale = 25.4*2.25
    #scaled_grid = [triangle/scale for sublist in mesh for triangle in sublist]
    for triangle in mesh:
       mesh_grid.extend(triangle)
    #print mesh_grid
    scaled_grid = [x/scale for x in mesh_grid]
    scaled_grid = np.float32(scaled_grid).reshape(-1,3)
    #print scaled_grid
    return scaled_grid
    # for triangle in mesh:
    #     points = []
    #     for i, number in enumerate(triangle):
    #         points.append(number)
    #         if (i+1)%3 == 0:
    #             points.append(number)
    #             mesh_grid.append(points)
    #             points = []
    #     print triangle
    #     imgpts = np.int32(triangle).reshape(-1,2)
    #     mesh_grid.append(imgpts)
    # print mesh_grid
    # return mesh_grid

#class for a 3d point
class createpoint:
    def __init__(self,p,c=(1,0,0)):
        self.point_size=0.5
        self.color=c
        self.x=p[0]
        self.y=p[1]
        self.z=p[2]
      
    def glvertex(self):
        glVertex3f(self.x,self.y,self.z)

#class for a 3d face on a model
class createtriangle:
    points=None
    normal=None

    def __init__(self,p1,p2,p3,n=None):
        #3 points of the triangle
        self.points=createpoint(p1),createpoint(p2),createpoint(p3)
      
        #triangles normal
        self.normal=createpoint(self.calculate_normal(self.points[0],self.points[1],self.points[2]))#(0,1,0)#
  
    #calculate vector / edge
    def calculate_vector(self,p1,p2):
        return -p1.x+p2.x,-p1.y+p2.y,-p1.z+p2.z
      
    def calculate_normal(self,p1,p2,p3):
        a=self.calculate_vector(p3,p2)
        b=self.calculate_vector(p3,p1)
        #calculate the cross product returns a vector
        return self.cross_product(a,b)
  
    def cross_product(self,p1,p2):
        return (p1[1]*p2[2]-p2[1]*p1[2]) , (p1[2]*p2[0])-(p2[2]*p1[0]) , (p1[0]*p2[1])-(p2[0]*p1[1])

class loader:
    model=[]
      
    #return the faces of the triangles
    def get_triangles(self):
        if self.model:
            for face in self.model:
                yield face
                # print face

    #draw the models faces
    def draw(self):
        glBegin(GL_TRIANGLES)
        for tri in self.get_triangles():
            # print tri.points[].x
            glNormal3f(tri.normal.x,tri.normal.y,tri.normal.z)
            glVertex3f(tri.points[0].x,tri.points[0].y,tri.points[0].z)
            glVertex3f(tri.points[1].x,tri.points[1].y,tri.points[1].z)
            glVertex3f(tri.points[2].x,tri.points[2].y,tri.points[2].z)
        glEnd()
   
        # sys.exit()

    #load stl file detects if the file is a text file or binary file
    def load_stl(self,filename):
        #read start of file to determine if its a binay stl file or a ascii stl file
        fp=open(filename,'rb')
        h=fp.read(80)
        type=h[0:5]
        fp.close()

        # if type=='solid':
        #     print "reading text file"+str(filename)
        #     self.load_text_stl(filename)
        # else:
        #     print "reading binary stl file "+str(filename,)
        #     self.load_binary_stl(filename)
        print "reading binary stl file "+str(filename,)
        self.load_binary_stl(filename)

  
    #read text stl match keywords to grab the points to build the model
    def load_text_stl(self,filename):
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

    #load binary stl file check wikipedia for the binary layout of the file
    #we use the struct library to read in and convert binary data into a format we can use
    def load_binary_stl(self,filename):
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


class draw_scene:
    def __init__(self,style=1):
        #create a model instance and
        self.model1=loader()
        #self.model1.load_stl(os.path.abspath('')+'/text.stl')
        self.model1.load_stl(os.path.abspath('')+'/Cube_Cad.STL')
        self.init_shading()


    #solid model with a light / shading
    def init_shading(self):
        glShadeModel(GL_SMOOTH)
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClearDepth(1.0)
        glEnable(GL_DEPTH_TEST)
        glShadeModel(GL_SMOOTH) 
        glDepthFunc(GL_LEQUAL)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
      
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)   
        glLight(GL_LIGHT0, GL_POSITION,  (0, 1, 1, 0))      
        glMatrixMode(GL_MODELVIEW)

    def init(self):
        glShadeModel(GL_SMOOTH)
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClearDepth(1.0)
        glEnable(GL_DEPTH_TEST)
        glShadeModel(GL_SMOOTH) 
        glDepthFunc(GL_LEQUAL)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

        glEnable(GL_COLOR_MATERIAL)
      
        glEnable(GL_LIGHTING)
        glEnable(GLx_LIGHT0)   
        glLight(GL_LIGHT0, GL_POSITION,  (0, 1, 1, 0))

        glMatrixMode(GL_MODELVIEW)

    def draw(self):
        global angle

        
        # glLoadIdentity()
      
        glTranslatef(0, 100.0, 100.0)
        # glRotatef(angle,  1, 0, 0)
        glScale(.11, .11, .11)
        self.model1.draw()

def initGL():
    global contour
    global center
    global camera 
    global capture
    global ret
    global frame

    contour = Contours()
    center = Centers()
    camera = Camera()
    # cv2.waitKey(25)

    blueLower = np.array([90,100,10])
    blueUpper = np.array([150,255,255])
    blackLower = np.array([0,0,0])
    blackUpper = np.array([180, 255, 150])

    images = glob.glob('*.png')
    for fname in images:
        img = cv2.imread(fname)
        hsv_frame = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        ## construct a mask for the color "blue", then remove any imperfections
        mask_blue = cv2.inRange(hsv_frame, blueLower, blueUpper)
        mask_blue = cv2.erode(mask_blue, None, iterations=1)
        mask_blue = cv2.dilate(mask_blue, None, iterations=1)
        ## create black mask for tracking corner
        mask_black = cv2.inRange(hsv_frame, blackLower, blackUpper)
        ## create edges in which to create contours
        # edges = cv2.Canny(mask_blue,100,200, apertureSize = 3)
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

        ##creates information about the contours
        contour_information = cv2.findContours(mask_blue.copy(), cv2.RETR_CCOMP,
            cv2.CHAIN_APPROX_SIMPLE)

        ##updates each of the elements in the classes
        contour.update_contours(contour_information)
        center.update_centers(contour.contour_list, mask_black)
        center.reorganize_centers()
        camera.grab_frame_information(img, center.final_corners)

    # capture = cv2.VideoCapture(0)
    ## keep looping
    ret, frame = capture.read()
    # gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    camera.calibrate_camera(gray)

    glClearColor(0.0, 0.0, 0.0, 1.0) # Set background color to black and opaque  

    glutDisplayFunc(display)       
    glutKeyboardFunc(keyboard)
    glutIdleFunc(idle)

    glutTimerFunc(25, update, 0)


def display():

    global scene
    global view_matrix
    global camera

    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

    set2DTexMode()

    # Draw textured Quads
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex2f(0.0, 0.0)
    glTexCoord2f(1.0, 0.0)
    glVertex2f(width, 0.0)
    glTexCoord2f(1.0, 1.0)
    glVertex2f(width, height)
    glTexCoord2f(0.0, 1.0)
    glVertex2f(0.0, height)
    glEnd()

    set3DMode()

    if(camera.view_matrix):
        # print'a'
        glLoadMatrixf(view_matrix)
        scene.draw()

    glFlush()
    glutSwapBuffers()


def keyboard(key, x, y):
    if key == chr(27):
        sys.exit()
    if key == chr(107):
        camera.view_matrix = not camera.view_matrix

def update(dt):
    global angle
    global position

    angle += 2.0
    if angle > 360.0:
        angle -= 360.0

    # Update position with global position

    glutPostRedisplay()

    glutTimerFunc(25, update, 0)

def idle():
    #capture next frame
    global camera
    global capture
    global ret
    global frame
    global contour
    global center
    global view_matrix

    _,image = capture.read()
    # ## grab the current frame
    # ret, frame = capture.read()

    ## resize the frame, blur it, and convert it to the HSV
    frame = imutils.resize(image, width=640)
    # frame = cv2.flip(frame,1)
    # cv2.imshow("Original_Frame", frame)
    ## color space
    blueLower = np.array([90,100,10])
    blueUpper = np.array([150,255,255])
    blackLower = np.array([0,0,0])
    blackUpper = np.array([180, 255, 150])

    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    ## construct a mask for the color "blue", then remove any imperfections
    mask_blue = cv2.inRange(hsv_frame, blueLower, blueUpper)
    mask_blue = cv2.erode(mask_blue, None, iterations=1)
    mask_blue = cv2.dilate(mask_blue, None, iterations=1)
    ## create black mask for tracking corner
    mask_black = cv2.inRange(hsv_frame, blackLower, blackUpper)
    ## create edges in which to create contours
    # edges = cv2.Canny(mask_blue,100,200, apertureSize = 3)

    ##creates information about the contours`
    contour_information = cv2.findContours(mask_blue.copy(), cv2.RETR_CCOMP,
        cv2.CHAIN_APPROX_SIMPLE)

    ##updates each of the elements in the classes
    contour.update_contours(contour_information)
    center.update_centers(contour.contour_list, mask_black)
    if len(center.corners) == 4:
        center.reorganize_centers()
    center.update_vectors()
    center.bool_is_tracking()
    key = cv2.waitKey(1) & 0xFF
    ## if different keys are pressed
    if key == ord("d"):
        ## set boolean to draw axises
        camera.draw_axis = not camera.draw_axis
    if center.is_tracking:
        if camera.view_matrix:
            rvecs, tvecs, inliers = cv2.solvePnPRansac(camera.objp, np.array(center.final_corners, dtype = np.float32), camera.mtx, camera.dist)
            # print camera.objp
            # cv2.polylines(image, np.int32([center.final_corners]), True, (0,255,0), 3)
            view_matrix = camera.return_view_matrix(rvecs, tvecs)
            # print view_matrix
        print'a'

        # if camera.draw_axis:
            ##draw the cube
            #print my_mesh
            #axis = np.float32([[1,0,0], [0,1,0], [0,0,1]]).reshape(-1,3)

            #axis_length = 1.5
            #axis = np.float32([[0,0,0], [0,axis_length,0], [axis_length,axis_length,0], [axis_length,0,0],
            #       [0,0,axis_length],[0,axis_length,axis_length],[axis_length,axis_length,axis_length],[axis_length,0,axis_length] ])
            #print axis
            # rvecs, tvecs, inliers = cv2.solvePnPRansac(camera.objp, np.array(center.final_corners, dtype = np.float32), camera.mtx, camera.dist)
            # imgpts, jac = cv2.projectPoints(mesh_grid, rvecs, tvecs, camera.mtx, camera.dist)
            #draw_axis(frame, center.main_corner, imgpts)
            # draw_mesh(frame, imgpts)
            ##otherwise, draw the lines to the dots
        for i, corner in enumerate(center.final_corners):
            ## for each corner, color each one a different color
            if i == 0:
                ##print 'green'
                cv2.circle(image, corner, 20, (0,255,0), thickness=-1)
            elif i == 1:
                ##print 'red'
                cv2.circle(image, corner, 15, (0,0,255), thickness=-1)
            elif i == 2:
                ##print 'yellow'
                cv2.circle(image, corner, 10, (0,255,255), thickness=-1)
            else:
                ##print 'white'
                cv2.circle(image, corner, 5, (255,255,255), thickness=-1)
            ##uses the vector to draw a line on the tracked square
        for i, vector in enumerate(center.vectors):
            reference_point_x = center.main_corner[0] + vector[0]
            reference_point_y = center.main_corner[1] + vector[1]
            points = np.array([center.main_corner, (reference_point_x, reference_point_y)])
            cv2.polylines(image, np.int32([points]), True, (0,255,0), 3)
                # print 'a'
    ## shows each video analysis in different windows
    # cv2.imshow("Mask", mask_blue)
    # cv2.imshow("MaskBlack", mask_black)
    # cv2.imshow('edges', edges)
    # cv2.imshow("Frame", frame)
    #you must convert the image to array for glTexImage2D to work
    #maybe there is a faster way that I don't know about yet...

    # frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
    image = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)

    image = cv2.flip(image,0)
    image = cv2.flip(image,1)
    # Create Texture
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, image)
    # cv2.imshow('frame',image)

    glutPostRedisplay()

def drawAxes(length):
  glPushAttrib(GL_POLYGON_BIT | GL_ENABLE_BIT | GL_COLOR_BUFFER_BIT) ;

  glPolygonMode(GL_FRONT_AND_BACK, GL_LINE) ;
  glDisable(GL_LIGHTING) ;

  glBegin(GL_LINES) ;
  glColor3f(1,0,0) ;
  glVertex3f(0,0,0) ;
  glVertex3f(length,0,0);

  glColor3f(0,1,0) ;
  glVertex3f(0,0,0) ;
  glVertex3f(0,length,0);

  glColor3f(0,0,1) ;
  glVertex3f(0,0,0) ;
  glVertex3f(0,0,length);
  glEnd() ;

  glPopAttrib();

def set2DTexMode():
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

    glDisable(GL_COLOR_MATERIAL)
    glDisable(GL_LIGHTING)
    glDisable(GL_LIGHT0)   

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    gluOrtho2D(0, width, 0, height)

    glDisable(GL_DEPTH_TEST)
    glDepthMask(GL_FALSE)

    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_TEXTURE_2D)
    glLoadIdentity()

def set3DMode():
    glDepthMask(GL_TRUE)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0) 

    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    # glViewport(0,0, width, height)
    gluPerspective(45.0, (float(width)/float(height)), 0, 500.0);
    # gluLookAt(0.0,-20.0,75.0,0,-20,0,0,40.0,0)
    # gluLookAt(0.0,-20,0.01,0,-20,0,0,100,0)

    glMatrixMode(GL_MODELVIEW);
    glDisable(GL_TEXTURE_2D)
    glLoadIdentity();


#main program loop
def main():
    global capture
    #start openCV capturefromCAM
    capture = cv2.VideoCapture(0)
    # print capture
    capture.set(3,width)
    capture.set(4,height)
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(width, height)   # Set the window's initial width & height
    glutInitWindowPosition(0, 0) # Position the window's initial top-left corner
    glutCreateWindow("CHICKEN")          # Create window with the given title
    # glutFullScreen()

    global scene
    global angle
    angle = 30.0
    scene = draw_scene()
    initGL()                       # Our own OpenGL initialization
    glutMainLoop()                 # Enter the infinite event-processing loop


if __name__ == '__main__':
    # my_mesh = mesh.Mesh.from_file('Test_Piece.STL')
    # mesh_grid = create_mesh_grid(my_mesh)
    # program(mesh_grid)
    width = 640
    height = 480

    main()