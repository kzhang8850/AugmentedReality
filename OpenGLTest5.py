import cv2
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
import sys

width = 1280
height = 720
nRange = 1.0

global capture
capture = None

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

   glutDisplayFunc(display)       # Register callback handler for window re-paint event
   glutReshapeFunc(reshape)
   glutIdleFunc(idle)  

   glEnable(GL_TEXTURE_2D)
   glClearDepth(1.0)                   # Set background depth to farthest
   glEnable(GL_DEPTH_TEST)   # Enable depth testing for z-culling
   glDepthFunc(GL_LEQUAL)    
   glShadeModel(GL_SMOOTH)  
   glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)  

def idle():
    #capture next frame

    global capture
    _,image = capture.read()


    image = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
    image = cv2.flip(image,0)
    #you must convert the image to array for glTexImage2D to work
    #maybe there is a faster way that I don't know about yet...

    #print image_arr


    # Create Texture
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 1280,720, 0, GL_RGB, GL_UNSIGNED_BYTE, image)

    cv2.imshow('frame',image)
    glutPostRedisplay()


def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    #this one is necessary with texture2d for some reason
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

    # Set Projection Matrix
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, width, 0, height)

    # Switch to Model View Matrix
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glEnable(GL_TEXTURE_2D)
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
 
   # Render a color-cube consisting of 6 quads with different colors
    glLoadIdentity()               # Reset the model-view matrix
    glTranslatef(width/2, height/2, -50)  # Move right and into the screen
    # glTranslatef(1.5, -2, -10)  # Move right and into the screen
    glDisable(GL_TEXTURE_2D)

    glBegin(GL_QUADS)
    draw_cube((0, -25, 0),  
                (25, 0, 0),
                (50, -25, 0),
                (25, -50, 0),
                (0, -25, 50),
                (25, 0, 50),
                (50,-25, 50),
                (25, -50, 50))
    glEnd()  # End of drawing color-cube

    



    # glBegin(GL_QUADS)                # Begin drawing the color cube with 6 quads
    #   # Top face (y = 1.0f)
    #   # Define vertices in counter-clockwise (CCW) order with normal pointing out
    # glColor3f(0.0, 1.0, 0.0)     # Green
    # glVertex3f( 1.0, 1.0, -1.0)
    # glVertex3f(-1.0, 1.0, -1.0)
    # glVertex3f(-1.0, 1.0,  1.0)
    # glVertex3f( 1.0, 1.0,  1.0)

    # # Bottom face (y = -1.0f)
    # glColor3f(0.0, 1.0, 0.0)     # Orange
    # glVertex3f( 1.0, -1.0,  1.0)
    # glVertex3f(-1.0, -1.0,  1.0)
    # glVertex3f(-1.0, -1.0, -1.0)
    # glVertex3f( 1.0, -1.0, -1.0)

    # # Back face (z = -1.0f)
    # glColor3f(1.0, 1.0, 0.0)     # Yellow
    # glVertex3f( 1.0, -1.0, -1.0)
    # glVertex3f(-1.0, -1.0, -1.0)
    # glVertex3f(-1.0,  1.0, -1.0)
    # glVertex3f( 1.0,  1.0, -1.0)

    # # Left face (x = -1.0f)
    # glColor3f(0.0, 0.0, 1.0)     # Blue
    # glVertex3f(-1.0,  1.0,  1.0)
    # glVertex3f(-1.0,  1.0, -1.0)
    # glVertex3f(-1.0, -1.0, -1.0)
    # glVertex3f(-1.0, -1.0,  1.0)

    # # Right face (x = 1.0f)
    # glColor3f(1.0, 0.0, 1.0)     # Magenta
    # glVertex3f(1.0,  1.0, -1.0)
    # glVertex3f(1.0,  1.0,  1.0)
    # glVertex3f(1.0, -1.0,  1.0)
    # glVertex3f(1.0, -1.0, -1.0)

    # # Front face  (z = 1.0f)
    # glColor3f(1.0, 1.0, 1.0)     # Red
    # glVertex3f( 1.0,  1.0, 1.0)
    # glVertex3f(-1.0,  1.0, 1.0)
    # glVertex3f(-1.0, -1.0, 1.0)
    # glVertex3f( 1.0, -1.0, 1.0)

    # glEnd()  # End of drawing color-cube

    glFlush()  
    glutSwapBuffers()  # Swap the front and back frame buffers (double buffering)
 

def reshape(width, height):   # GLsizei for non-negative integer
   # Compute aspect ratio of the new window
   if height == 0:
        height = 1                # To prevent divide by 0
    
   aspect = width / height
 
   # Set the viewport to cover the new window
   glViewport(0, 0, width, height)
 
   # Set the aspect ratio of the clipping volume to match the viewport
   glMatrixMode(GL_PROJECTION)  # To operate on the Projection matrix
   glLoadIdentity()             # Reset
   # Enable perspective projection with fovy, aspect, zNear and zFar
   gluPerspective(45.0, aspect, 0.1, 100.0)

   glMatrixMode(GL_MODELVIEW)
   glLoadIdentity()

def draw_cube(p1, p2, p3, p4, p5, p6, p7, p8):
    
    #Top Face
    glColor3f(0.0, 1.0, 0.0)     # Green
    glVertex3f(p1[0], p1[1], p1[2])
    glVertex3f(p2[0], p2[1], p1[2])
    glVertex3f(p3[0], p3[1], p3[2])
    glVertex3f(p4[0], p4[1], p4[2])
    # Bottom face (y = -1.0f)
    glColor3f(0.0, 0.0, 0.0)     # Orange
    glVertex3f(p1[0], p1[1], p1[2])
    glVertex3f(p5[0], p5[1], p5[2])
    glVertex3f(p8[0], p8[1], p8[2])
    glVertex3f(p4[0], p4[1], p4[2])
    # Back face (z = -1.0f)
    glColor3f(1.0, 1.0, 0.0)     # Yellow
    glVertex3f(p4[0], p4[1], p4[2])
    glVertex3f(p8[0], p4[1], p4[2])
    glVertex3f(p7[0], p7[1], p7[2])
    glVertex3f(p3[0], p3[1], p3[2])
    # Left face (x = -1.0f)
    glColor3f(0.0, 0.0, 1.0)     # Blue
    glVertex3f(p3[0], p3[1], p3[2])
    glVertex3f(p7[0], p7[1], p7[2])
    glVertex3f(p6[0], p6[1], p6[2])
    glVertex3f(p2[0], p6[1], p6[2])
    # Right face (x = 1.0f)
    glColor3f(1.0, 0.0, 1.0)     # Magenta
    glVertex3f(p5[0], p5[1], p5[2])
    glVertex3f(p6[0], p6[1], p6[2])
    glVertex3f(p7[0], p7[1], p7[2])
    glVertex3f(p8[0], p8[1], p8[2])
    # Front face  (z = 1.0f)
    glColor3f(1.0, 1.0, 1.0)     # Red
    glVertex3f(p1[0], p1[1], p1[2])
    glVertex3f(p5[0], p5[1], p5[2])
    glVertex3f(p6[0], p6[1], p6[2])
    glVertex3f(p2[0], p6[1], p6[2])

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
 

def main():             # Initialize GLUT
   global capture
   #start openCV capturefromCAM
   capture = cv2.VideoCapture(0)
   # print capture
   capture.set(3,1280)
   capture.set(4,720)
   glutInit(sys.argv)
   glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH) # Enable double buffered mode
   glutInitWindowSize(width, height)   # Set the window's initial width & height
   glutInitWindowPosition(100, 100) # Position the window's initial top-left corner
   glutCreateWindow("CHICKEN")          # Create window with the given title

   initGL()                       # Our own OpenGL initialization
   glutMainLoop()                 # Enter the infinite event-processing loop

main()