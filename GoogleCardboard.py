""" 
Attempt at Creating Google Cardboard Rendering Video for Augmented Reality 

Now with Duet Display!
"""
	
"""
Final Project
Completed by Kevin Zhang and Daniel Daugherty
Software Design Spring 2016
"""

import cv2
import numpy as np

#initalizing video of camera
cam = cv2.VideoCapture(0)


#forever looping
while True:

	#capture frame by frame
	ret, frame = cam.read()


	#generates two copies of the image for VR
	frame1 = frame
	frame2 = frame


	#reformats the image for fullscreen
	ratio = 768.0/frame.shape[0];
	dim = (int(frame.shape[1]*ratio), 768)
	resized_frame1 = cv2.resize(frame1, dim, interpolation=cv2.INTER_AREA)
	resized_frame2 = cv2.resize(frame2, dim, interpolation=cv2.INTER_AREA)

	#offsets the images
	offset_frame1 = resized_frame1[:,160:843]
	offset_frame2 = resized_frame2[:,80:763]

	#combines the images into one VR image
	google_frame = np.hstack((offset_frame1, offset_frame2))

	#display resulting frame
	cv2.namedWindow('Google Cardboard', cv2.WINDOW_NORMAL)
	cv2.setWindowProperty('Google Cardboard', cv2.WND_PROP_FULLSCREEN, cv2.cv.CV_WINDOW_FULLSCREEN)
	cv2.imshow('Google Cardboard', google_frame)


	#press q to close window
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break		
	
#closes program
cam.release()
cv2.destroyAllWindows()