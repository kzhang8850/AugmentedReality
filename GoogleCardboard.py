""" Attempt at Creating Google Cardboard Rendering Video for Augmented Reality """

"""
Final Project
Completed by Kevin Zhang and Daniel Daugherty
Software Design Spring 2016
"""

import cv2
import numpy as np

#initalizing video of camera
cam = cv2.VideoCapture(0)



while True:

	#capture frame by frame

	ret, frame = cam.read()

	ratio = 800.0/frame.shape[1];
	dim = (800, int(frame.shape[0]*ratio))

	resized_frame = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)

	google_frame = np.hstack((resized_frame, resized_frame))

	#display resulting frame 
	cv2.imshow('Google Cardboard', google_frame)

	if cv2.waitKey(1) & 0xFF == ord('q'):
		break		
	

cam.release()
cv2.destroyAllWindows()
