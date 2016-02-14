import cv2
import numpy as np
import time
import sys

def getColor(event,x,y,flags,param):
	if event == cv2.EVENT_LBUTTONUP:
		[h,s,v] = image_hsv[y,x] 
		cv2.setTrackbarPos('H','image',h)
		cv2.setTrackbarPos('S','image',s)
		cv2.setTrackbarPos('V','image',v)
		cv2.imshow('image',image)
	else:
		pass

def nothing(x):
	pass


filename = sys.argv[1]
cv2.namedWindow('image')

# create trackbars for color change
cv2.createTrackbar('H','image',0,179,nothing)
cv2.createTrackbar('S','image',0,255,nothing)
cv2.createTrackbar('V','image',0,255,nothing)

cv2.setMouseCallback('image',getColor)

image = cv2.imread(filename)
image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
cv2.imshow('image',image)

while(1):
    time.sleep(0.05)
    k = cv2.waitKey(1) & 0xFF
    if k == 27: # Esc key to stop
        break

cv2.destroyAllWindows()
