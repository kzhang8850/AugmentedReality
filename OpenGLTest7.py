import os
import struct
import cv2

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
import sys

global capture
capture = None

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
            glNormal3f(tri.normal.x,tri.normal.y,tri.normal.z)
            glVertex3f(tri.points[0].x,tri.points[0].y,tri.points[0].z)
            glVertex3f(tri.points[1].x,tri.points[1].y,tri.points[1].z)
            glVertex3f(tri.points[2].x,tri.points[2].y,tri.points[2].z)
        glEnd()

    #load stl file detects if the file is a text file or binary file
    def load_stl(self,filename):
        #read start of file to determine if its a binay stl file or a ascii stl file
        fp=open(filename,'rb')
        h=fp.read(80)
        type=h[0:5]
        fp.close()

        print "reading binary stl file "+str(filename,)
        self.load_binary_stl(filename)

  
  
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
        # glShadeModel(GL_SMOOTH)
        # glClearColor(0.0, 0.0, 0.0, 0.0)
        # glClearDepth(1.0)
        # glEnable(GL_DEPTH_TEST)
        # glShadeModel(GL_SMOOTH) 
        # glDepthFunc(GL_LEQUAL)
        # glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
      

        # glEnable(GL_COLOR_MATERIAL)
        # glEnable(GL_LIGHTING)
        # glEnable(GL_LIGHT0)   
        # glLight(GL_LIGHT0, GL_POSITION,  (0, 1, 1, 0))      
        # glMatrixMode(GL_MODELVIEW)

        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)   
        glLight(GL_LIGHT0, GL_POSITION,  (1, 1, 1, 0))      
        glMatrixMode(GL_MODELVIEW)


    def draw(self):
        global angle

        
        glLoadIdentity()
      
        glTranslatef(0.0, -25.0, -250.0)

        glRotatef(angle, 1, 1, 3)
        # glScale(.5, .5, .5)
        self.model1.draw()


def initGL():

    glClearColor(0.0, 0.0, 0.0, 1.0) # Set background color to black and opaque  

    glutDisplayFunc(display)       
    glutKeyboardFunc(keyboard)
    glutIdleFunc(idle)
    glutTimerFunc(25, update, 0)


def display():

    global scene

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
    
    scene.draw()

    glFlush()
    glutSwapBuffers()


def keyboard(key, x, y):
    if key == chr(27):
        sys.exit()

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

    global capture
    _,image = capture.read()
    #print test
    image = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
    image = cv2.flip(image,0)
    image = cv2.flip(image,1)
    #you must convert the image to array for glTexImage2D to work
    #maybe there is a faster way that I don't know about yet...

    # Create Texture
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, image)

    cv2.imshow('frame',image)
    glutPostRedisplay()

def set2DTexMode():
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

    glDisable(GL_COLOR_MATERIAL)
    glDisable(GL_LIGHTING)
    glDisable(GL_LIGHT1)   

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
    glDisable(GL_COLOR_MATERIAL)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT1) 

    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    # glViewport(0,0, width, height)
    gluPerspective(45.0, (float(width)/float(height)), 0.1, 500.0);
    # gluLookAt(0.0,-20.0,75.0,0,-20,0,0,40.0,0)

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
    glutFullScreen()

    global scene
    global angle
    angle = 30.0
    scene = draw_scene()
    initGL()                       # Our own OpenGL initialization
    glutMainLoop()                 # Enter the infinite event-processing loop

if __name__ == '__main__':
    width = 848
    height = 480

    main()