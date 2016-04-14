"""
Visualization Controller for Augmented Reality, #GetReal
Takes a set of coordinates and renders a 3D image on a background frame
Currently doing a cube, wil do CAD soon

In Progress

Daniel Daugherty and Kevin Zhang, Cedric Kim, and Kevin Guo
Software Design Spring 2016
"""

import pyglet
from pyglet.gl import *
from pyglet.window import key
from OpenGL.GL import *
from OpenGL.GLU import *
import cv2
import numpy

#Creates the window for pyglet to render everything in, also initializes the camera
window = pyglet.window.Window(800,600)
camera = cv2.VideoCapture(0)


"""
Work in Progress - Cube
"""
# verticies = (
#     (0, 50, 1),
#     (0, 0, 1),
#     (50, 0, 1),
#     (50, 50, 1),
#     (0, 50, 25),
#     (0, 0, 25),
#     (50, 50, 25),
#     (50, 0, 25)
#     )

# edges = (
#     (0,1),
#     (0,3),
#     (0,4),
#     (2,1),
#     (2,3),
#     (2,7),
#     (6,3),
#     (6,4),
#     (6,7),
#     (5,1),
#     (5,4),
#     (5,7)
#     )

# gluPerspective(145, (800/600), 0.1, 800.0)

# glTranslatef(0.0,0.0, -5)

def update(dt):
	"""
	WTF is this function
	"""
	pass
	
#window.event required by pyglet to run functions based on events/continually
@window.event
def on_key_press(symbol, modifiers):
	"""
	Allows for testing and experimentation
	Closes program on pressing esc key
	"""

	if symbol == key.ESCAPE:
	    print 'Application Exited with Key Press'
	    window.close()

@window.event
def on_draw():
	"""
	Does the rendering
	Converts OpenCV frame into OpenGL format
	Overlays a Cube on top of the frame
	"""

	window.clear()         #clears previous stuff on window
	retval,img = camera.read()     #reads camera
	img = cv2.flip(img, 0)         #flips frame because for some reason it comes upside down
	img = cv2.resize(img, (800, 600))   #resizes image
	sy,sx,number_of_channels = img.shape    #divides data into matrix dimensions
	number_of_bytes = sy*sx*number_of_channels    #transforms matrix into an array of data

	img = img.ravel()   #idk

	image_texture = (GLubyte * number_of_bytes)( *img.astype('uint8') )  #converts data into OpenGL format with GLubyte

	pImg = pyglet.image.ImageData(sx, sy, 'BGR', image_texture, pitch = sx*number_of_channels)   #creates new texture render with formatted data
	pImg.blit(0,0)    #puts new image thing onto window


	"""
	Work in Progress - Cube
	"""
	# glRotatef(1, 3, 1, 1)
	# glBegin(GL_LINES)
	# glColor3f(1,0,0)
	# for edge in edges:
	# 	for vertex in edge:
	# 		glVertex3fv(verticies[vertex])

	# glColor3f(1,1,1)
	# glEnd()


	#Creates a colorful square to be rendered on top of the frame
	glBegin(GL_QUADS)
	glColor3f(1,0,0)
	glVertex2i(400,400)
	glColor3f(0,1,0)
	glVertex2i(400,200)
	glColor3f(0,0,1)
	glVertex2i(200,200)
	glColor3f(0,1,1)
	glVertex2i(200,400)
	glColor3f(1,1,1)
	glEnd()
	cv2.waitKey(1)



pyglet.clock.schedule(update)     #creates a timer that runs update which runs on_draw at set intervals
pyglet.app.run()   #launches the program and starts processing of window events, timers, etc.