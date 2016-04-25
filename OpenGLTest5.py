import cv2
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
import sys
import pdb


width = 848 
height = 480

global angle
global position
global capture

angle = 30.0
position = [0,0,0]
capture = None

# What is this?
def cv2array(im):     
    h,w,c=im.shape
    a = np.fromstring( 
        im.tostring(), 
        dtype=im.dtype, 
        count=w*h*c) 
    a.shape = (h,w,c) 
    return a

def initGL():
    glClearColor(0.0, 0.0, 0.0, 1.0) # Set background color to black and opaque


    glEnable(GL_TEXTURE_2D)
    glClearDepth(1.0)                   # Set background depth to farthest
    glEnable(GL_DEPTH_TEST)   # Enable depth testing for z-culling
    glDepthFunc(GL_LEQUAL)    
    glShadeModel(GL_SMOOTH)  
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)  

    glutDisplayFunc(display)       
    glutKeyboardFunc(keyboard)
    glutIdleFunc(idle)

    glutTimerFunc(25, update, 0)



def idle():
    #capture next frame
    # print "idlings"
    global capture
    _,image = capture.read()

    image = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
    image = cv2.flip(image,0)
    image = cv2.flip(image,1)
    #you must convert the image to array for glTexImage2D to work
    #maybe there is a faster way that I don't know about yet...


    # Create Texture
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, image)

    cv2.imshow('frame',image)
    glutPostRedisplay()


def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)   

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
 
    glTranslatef(0.0, 0.0, -10.0)  # Move right and into the screen
    glRotatef(angle, 1, 1, 1)

    vertices = cube_vertices(position, 5)
    drawCube(vertices)    

    glFlush()  
    glutSwapBuffers()  # Swap the front and back frame buffers (double buffering)


def set2DTexMode():
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

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

    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    # glViewport(0,0, width, height)
    gluPerspective(60.0, (float(width)/float(height)), 0.1, 100.0);

    glMatrixMode(GL_MODELVIEW);
    glDisable(GL_TEXTURE_2D)
    glLoadIdentity();

def drawCube(vertices):

    glBegin(GL_QUADS) 

    for i in range(0,len(vertices), 3):
        if i == 0:     # Top Face
            glColor3f(1.0, 0.0, 0.0)
        elif i == 12:   # Bottom Face
            glColor3f(0.0, 1.0, 0.0)
        elif i == 24:   # Left Face
            glColor3f(0.0, 0.0, 1.0)
        elif i == 36:   # Right Face
            glColor3f(1.0, 1.0, 0.0)
        elif i == 48:   # Front Face
            glColor3f(0.0, 1.0, 1.0)
        elif i == 60:   # Back Face
            glColor3f(1.0, 0.0, 1.0)
        glVertex3f(vertices[i], vertices[i+1], vertices[i+2])
   
    glColor3f(1.0, 1.0, 1.0)     # White
    glEnd()  # End of drawing color-cube

def cube_vertices(position, width):
    """ 
    Return the vertices of the cube at position (x, y, z) with a given size.
    """
    x, y, z = position
    n = width / 2.0 #distance of faces from the cube's center

    return [
        #lower left  #lower right #upper right #upper left
        x-n,y+n,z-n, x-n,y+n,z+n, x+n,y+n,z+n, x+n,y+n,z-n,  #top
        x-n,y-n,z-n, x+n,y-n,z-n, x+n,y-n,z+n, x-n,y-n,z+n,  #bottom
        x-n,y-n,z-n, x-n,y-n,z+n, x-n,y+n,z+n, x-n,y+n,z-n,  #left
        x+n,y-n,z+n, x+n,y-n,z-n, x+n,y+n,z-n, x+n,y+n,z+n,  #right
        x-n,y-n,z+n, x+n,y-n,z+n, x+n,y+n,z+n, x-n,y+n,z+n,  #front
        x+n,y-n,z-n, x-n,y-n,z-n, x-n,y+n,z-n, x+n,y+n,z-n   #back
    ]

def update(dt):
    global angle
    global position

    angle += 2.0
    if angle > 360.0:
        angle -= 360.0

    # Update position with global position

    glutPostRedisplay()

    glutTimerFunc(25, update, 0)

def keyboard(key, x, y):
    global anim
    if key == chr(27):
        sys.exit()

def main():             # Initialize GLUT

    global capture
    #start openCV capturefromCAM
    capture = cv2.VideoCapture(0)
    # print capture
    capture.set(3,width)
    capture.set(4,height)
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH) # Enable double buffered mode
    glutInitWindowSize(width, height)   # Set the window's initial width & height
    glutInitWindowPosition(0, 0) # Position the window's initial top-left corner
    glutCreateWindow("CHICKEN")          # Create window with the given title
    glutFullScreen()

    initGL()                       # Our own OpenGL initialization
    glutMainLoop()                 # Enter the infinite event-processing loop

main()