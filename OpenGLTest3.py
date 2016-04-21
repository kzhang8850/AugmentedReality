import pygame, pygame.image
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

import cv2
import numpy

import Image

import pdb

camera=cv2.VideoCapture(0)

verticies = (
    (1, -1, -1),
    (1, 1, -1),
    (-1, 1, -1),
    (-1, -1, -1),
    (1, -1, 1),
    (1, 1, 1),
    (-1, -1, 1),
    (-1, 1, 1)
    )

edges = (
    (0,1),
    (0,3),
    (0,4),
    (2,1),
    (2,3),
    (2,7),
    (6,3),
    (6,4),
    (6,7),
    (5,1),
    (5,4),
    (5,7)
    )


def Cube():
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(verticies[vertex])
    glEnd()


def main():
    pygame.init()
    display = (1000,747)
    screen = pygame.display.set_mode(display, OPENGL | DOUBLEBUF)
    # screen = pygame.display.set_mode(display, DOUBLEBUF|OPENGLBLIT)

    # gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)

    # glTranslatef(0.0,0.0, -5)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        retval,img = camera.read()
        img = numpy.rot90(img)
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        # new_img = pyformex.imagearray.rgb2qimage(img)
        # image = pygame.surfarray.make_surface(img)
        # pygame.image.save(image, "img.bmp")
        img_data = img.astype('uint8')

        # new_img = Image.open("img.bmp")
        # print new_img.format

        draw_background(img_data)

        

        # glRotatef(1, 3, 1, 1)
        # glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        #Cube()
        # screen.blit(image, (0,0))
        pygame.display.flip()
        pygame.time.wait(10)



def draw_background(img):
  """  Draw background image using a quad. """

  # load background image (should be .bmp) to OpenGL texture
  #bg_image = pygame.image.load(imname).convert()
  #bg_image = Image.open(imname)
  #bg_data = numpy.array(list(bg_image.getdata()), numpy.int8)
  #bg_data = pygame.image.tostring(bg_image,"RGBX", True)



  glMatrixMode(GL_MODELVIEW)
  glLoadIdentity()
  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

  # bind the texture
  glEnable(GL_TEXTURE_2D)
  glPixelStorei(GL_UNPACK_ALIGNMENT,1)
  glBindTexture(GL_TEXTURE_2D,glGenTextures(1))
  pdb.set_trace()
  glTexParameterf(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_NEAREST)
  glTexParameterf(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_NEAREST)
  glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 1000, 747, 0, GL_RGBA, GL_UNSIGNED_BYTE, img)
  
  # create quad to fill the whole window
  glBegin(GL_QUADS)
  glTexCoord2f(0.0,0.0)
  glVertex3f(-1.0,-1.0,-1.0)
  glTexCoord2f(1.0,0.0)
  glVertex3f( 1.0,-1.0,-1.0)
  glTexCoord2f(1.0,1.0)
  glVertex3f( 1.0, 1.0,-1.0)
  glTexCoord2f(0.0,1.0)
  glVertex3f(-1.0, 1.0,-1.0)
  glEnd()

  # clear the texture
  glDeleteTextures(1)

main()