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

	frame1 = frame
	frame2 = frame



	ratio = 960.0/frame.shape[1];
	dim = (960, int(frame.shape[0]*ratio))

	resized_frame1 = cv2.resize(frame1, dim, interpolation=cv2.INTER_AREA)
	resized_frame2 = cv2.resize(frame2, dim, interpolation=cv2.INTER_AREA)


	offset_frame1 = resized_frame1[:,80:960]
	offset_frame2 = resized_frame2[:,0:880]


	google_frame = np.hstack((offset_frame1, offset_frame2))

	#display resulting frame 
	#cv2.namedWindow('Google Cardboard', cv2.WINDOW_NORMAL)
	#cv2.setWindowProperty('Google Cardboard', cv2.WND_PROP_FULLSCREEN, cv2.cv.CV_WINDOW_FULLSCREEN)
	cv2.imshow('Google Cardboard', google_frame)

	if cv2.waitKey(1) & 0xFF == ord('q'):
		break		
	

cam.release()
cv2.destroyAllWindows()
