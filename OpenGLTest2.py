import pyglet
from pyglet.gl import *
from pyglet.window import key
import cv2
import numpy

window = pyglet.window.Window()

camera=cv2.VideoCapture(0)


def update(dt):
	pass

@window.event
def on_key_press(symbol, modifiers):
    if symbol == key.ESCAPE:
        print 'Application Exited with Key Press'
        window.close()

@window.event
def on_draw():
	window.clear()
	print "HI"
	retval,img = camera.read()
	img = cv2.flip(img, 0)
	# print "booger"
	sy,sx,number_of_channels = img.shape
	number_of_bytes = sy*sx*number_of_channels

	img = img.ravel()

	# image_texture = (GLubyte * number_of_bytes)( *img.astype('uint8') )
	image_texture = (GLubyte*number_of_bytes)(*img.astype('uint8'))
	# my webcam happens to produce BGR; you may need 'RGB', 'RGBA', etc. instead
	pImg = pyglet.image.ImageData(sx, sy, 'BGR', image_texture, pitch = sx*number_of_channels)
	pImg.blit(0,0)
	glMatrixMode(GL_MODELVIEW)
	glBegin(GL_QUADS)
	glColor3f(1,0,0)
	glVertex2i(300,300)
	glColor3f(0,1,0)
	glVertex2i(400,200)
	glColor3f(0,0,1)
	glVertex2i(200,200)
	glColor3f(1,1,1)
	glEnd()

pyglet.clock.schedule_interval(update, 1.0/75.0)
pyglet.clock.set_fps_limit(75)
pyglet.app.run()