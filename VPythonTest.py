import cv2
import numpy as np
from visual import *

a = box()
print type(a)


cap = cv2.VideoCapture(0)

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
    # print frame

    # Display the resulting frame
    # frame[100:110,100:110] = box(display = scene)
    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()