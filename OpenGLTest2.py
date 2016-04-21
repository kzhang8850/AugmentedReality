import cv2
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
import sys


def initGL():
   glClearColor(0.0, 0.0, 0.0, 1.0) # Set background color to black and opaque
   glClearDepth(1.0)                   # Set background depth to farthest
   glEnable(GL_DEPTH_TEST)   # Enable depth testing for z-culling
   glDepthFunc(GL_LEQUAL)    # Set the type of depth-test
   glShadeModel(GL_SMOOTH)   # Enable smooth shading
   glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)  # Nice perspective corrections

 

def display(): 
   	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) # Clear color and depth buffers
   	glMatrixMode(GL_MODELVIEW)     # To operate on model-view matrix
 
   # Render a color-cube consisting of 6 quads with different colors
   	glLoadIdentity()                 # Reset the model-view matrix
   	glTranslatef(1.5, -2, -10.0)  # Move right and into the screen
 
   	glBegin(GL_QUADS)                # Begin drawing the color cube with 6 quads
      # Define vertices in counter-clockwise (CCW) order with normal pointing out
	# Bottom face (y = -1.0f)
	glColor3f(1.0, 0.5, 0.0)     # Orange
	glVertex3f( 1.0, -1.0,  1.0)
	glVertex3f(-1.0, -1.0,  1.0)
	glVertex3f(-1.0, -1.0, -1.0)
	glVertex3f( 1.0, -1.0, -1.0)

	# Back face (z = -1.0f)
	glColor3f(1.0, 1.0, 0.0)     # Yellow
	glVertex3f( 1.0, -1.0, -1.0)
	glVertex3f(-1.0, -1.0, -1.0)
	glVertex3f(-1.0,  1.0, -1.0)
	glVertex3f( 1.0,  1.0, -1.0)

	# Left face (x = -1.0f)
	glColor3f(0.0, 0.0, 1.0)     # Blue
	glVertex3f(-1.0,  1.0,  1.0)
	glVertex3f(-1.0,  1.0, -1.0)
	glVertex3f(-1.0, -1.0, -1.0)
	glVertex3f(-1.0, -1.0,  1.0)

	# Right face (x = 1.0f)
	glColor3f(1.0, 0.0, 1.0)     # Magenta
	glVertex3f(1.0,  1.0, -1.0)
	glVertex3f(1.0,  1.0,  1.0)
	glVertex3f(1.0, -1.0,  1.0)
	glVertex3f(1.0, -1.0, -1.0)

	# Top Face
	glColor3f(0.0, 1.0, 0.0)     # Green
	glVertex3f( 1.0, 1.0, -1.0)
	glVertex3f(-1.0, 1.0, -1.0)
	glVertex3f(-1.0, 1.0,  1.0)
	glVertex3f( 1.0, 1.0,  1.0)
 
   	# Front face  (z = 1.0f)
	glColor3f(1.0, 1.0, 0.0)     # Red
	glVertex3f( 1.0,  1.0, 1.0)
	glVertex3f(-1.0,  1.0, 1.0)
	glVertex3f(-1.0, -1.0, 1.0)
	glVertex3f( 1.0, -1.0, 1.0)

	glEnd()
 
   
   	glutSwapBuffers()  # Swap the front and back frame buffers (double buffering)

 

def reshape(width, height):  # GLsizei for non-negative integer
   # Compute aspect ratio of the new window
   if (height == 0):
   		height = 1                # To prevent divide by 0
   		
   aspect = width / height
 
   # Set the viewport to cover the new window
   glViewport(0, 0, width, height)
 
   # Set the aspect ratio of the clipping volume to match the viewport
   glMatrixMode(GL_PROJECTION)  # To operate on the Projection matrix
   glLoadIdentity()             # Reset
   # Enable perspective projection with fovy, aspect, zNear and zFar
   gluPerspective(45.0, aspect, 0.1, 100.0)

 

def main():
   glutInit(sys.argv)            # Initialize GLUT
   glutInitDisplayMode(GLUT_DOUBLE) # Enable double buffered mode
   glutInitWindowSize(640, 480)   # Set the window's initial width & height
   glutInitWindowPosition(50, 50) # Position the window's initial top-left corner
   glutCreateWindow("TEST")          # Create window with the given title
   glutDisplayFunc(display)       # Register callback handler for window re-paint event
   glutReshapeFunc(reshape)       # Register callback handler for window re-size event
   initGL()                       # Our own OpenGL initialization
   glutMainLoop()                 # Enter the infinite event-processing loop

main()