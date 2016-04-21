import cv2
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
import sys


#window dimensions
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

def init():
    #glclearcolor (r, g, b, alpha)
    glClearColor(0.0, 0.0, 0.0, 1.0)

    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutIdleFunc(idle)  

    glEnable(GL_TEXTURE_2D)
    glClearDepth(1.0)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
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



    # glBegin(GL_QUADS)
    # glColor3f(1,0,0)
    # glVertex2i(400,400)
    # glColor3f(0,1,0)
    # glVertex2i(400,200)
    # glColor3f(0,0,1)
    # glVertex2i(200,200)
    # glColor3f(0,1,1)
    # glVertex2i(200,400)
    # glColor3f(1,1,1)
    # glEnd()

    # glBegin(GL_QUADS)
    # glVertex3f(400, 400, 0)
    # glVertex3f(200, 400, 0)
    # glVertex3f(200, 200, 0)
    # glVertex3f(400, 200, 0)
    # glEnd()

  
    vertices = cube_vertices([0,0,-100], 100)

    # print vertices[60],vertices[61],vertices[62]

    glLoadIdentity()
    glTranslatef(width/2, height/2, 0)
    glBegin(GL_QUADS)

    #Bottom
    glColor3f(1,0,0)
    glVertex3f(vertices[12], vertices[13], vertices[14])
    glVertex3f(vertices[15], vertices[16], vertices[17])
    glVertex3f(vertices[18], vertices[19], vertices[20])
    glVertex3f(vertices[21], vertices[22], vertices[23])
    #Left
    glColor3f(0,0,1)
    glVertex3f(vertices[24], vertices[25], vertices[26])
    glVertex3f(vertices[27], vertices[28], vertices[29])
    glVertex3f(vertices[30], vertices[31], vertices[32])
    glVertex3f(vertices[33], vertices[34], vertices[35])
    #Top
    glColor3f(1,0,0)
    glVertex3f(vertices[0], vertices[1], vertices[2])
    glVertex3f(vertices[3], vertices[4], vertices[5])
    glVertex3f(vertices[6], vertices[7], vertices[8])
    glVertex3f(vertices[9], vertices[10], vertices[11])
    #Right
    glColor3f(0,1,0)
    glVertex3f(vertices[36], vertices[37], vertices[38])
    glVertex3f(vertices[39], vertices[40], vertices[41])
    glVertex3f(vertices[42], vertices[43], vertices[44])
    glVertex3f(vertices[45], vertices[46], vertices[47])
    #Back
    glColor3f(1,0,0)
    glVertex3f(vertices[60], vertices[61], vertices[62])
    glVertex3f(vertices[63], vertices[64], vertices[65])
    glVertex3f(vertices[66], vertices[67], vertices[68])
    glVertex3f(vertices[69], vertices[70], vertices[71])
    #Front
    glColor3f(1,0,0)
    glVertex3f(vertices[48], vertices[49], vertices[50])
    glVertex3f(vertices[51], vertices[52], vertices[53])
    glVertex3f(vertices[54], vertices[55], vertices[56])
    glVertex3f(vertices[57], vertices[58], vertices[59])


    glColor3f(1,1,1)

    glEnd()


    glFlush()
    glutSwapBuffers()

def reshape(w, h):
    if h == 0:
        h = 1

    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)

    glLoadIdentity()
    gluPerspective(45, (width/height), 0.1, 500.0)

    # allows for reshaping the window without distoring shape

    if w <= h:
        glOrtho(-nRange, nRange, -nRange*h/w, nRange*h/w, -nRange, nRange)
    else:
        glOrtho(-nRange*w/h, nRange*w/h, -nRange, nRange, -nRange, nRange)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()






def keyboard(key, x, y):
    global anim
    if key == chr(27):
        sys.exit()

def main():
    global capture
    #start openCV capturefromCAM
    capture = cv2.VideoCapture(0)
    print capture
    capture.set(3,1280)
    capture.set(4,720)
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(width, height)
    glutInitWindowPosition(100, 100)
    glutCreateWindow("OpenGL + OpenCV")

    init()
    glutMainLoop()

main()