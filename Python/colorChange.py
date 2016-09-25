import cv2
import numpy as np
import time
import sys
from tkFileDialog import askopenfilename

def getColor(event,x,y,flags,param):
	if event == cv2.EVENT_LBUTTONUP:
		[h,s,v] = imageHSV[y,x] 
		print 'Click at [%d %d %d]' % (h, s, v)
	else:
		pass

def hue(position):
	global flag, hue
	hue = position
	flag = 1

def saturationMin(position):
	global flag, min_saturation
	min_saturation = position
	flag = 1

def saturationMax(position):
	global flag, max_saturation
	max_saturation = position
	flag = 1

def valueMin(position):
	global flag, min_value
	min_value = position
	flag = 1

def valueMax(position):
	global flag, max_value
	max_value = position
	flag = 1

def binarize(image):
	high_hue = hue + color_interval
	low_hue = hue - color_interval
	high_color = np.array((high_hue, max_saturation, max_value))
	low_color = np.array((low_hue, min_saturation, min_value))
	image2 = cv2.inRange(imageHSV, low_color, high_color)
	print 'Binarize', low_hue, high_hue, min_saturation, max_saturation, min_value, max_value
	return image2

#######   Main   #######

filename = askopenfilename(initialdir="/home/pi/Desktop/Robotique/images/") # show an "Open" dialog box and return the path to the selected file

#Create window
cv2.namedWindow('original')
cv2.moveWindow('original', 150, 50)
cv2.namedWindow('BW')
cv2.moveWindow('BW', 150, 650)


# create trackbars for color change
cv2.createTrackbar('H','original',0,179,hue)
cv2.createTrackbar('Smin','original',0,255,saturationMin)
cv2.createTrackbar('Smax','original',0,255,saturationMax)
cv2.createTrackbar('Vmin','original',0,255,valueMin)
cv2.createTrackbar('Vmax','original',0,255,valueMax)

cv2.setMouseCallback('original',getColor)

#Prepare image
imageRGB = cv2.imread(filename)
imageRGB = cv2.copyMakeBorder(imageRGB,10,10,10,10,cv2.BORDER_CONSTANT,value=[0,0,0])
imageHSV = cv2.cvtColor(imageRGB, cv2.COLOR_BGR2HSV)
cv2.imshow('original',imageRGB)

flag = 0
color_interval = 6
hue = 9 #orange
min_saturation = 100
max_saturation = 255
min_value = 100
max_value = 255

cv2.setTrackbarPos('H','original',hue)
cv2.setTrackbarPos('Smin','original',min_saturation)
cv2.setTrackbarPos('Smax','original',max_saturation)
cv2.setTrackbarPos('Vmin','original',min_value)
cv2.setTrackbarPos('Vmax','original',max_value)

imageBW = binarize(imageHSV)
cv2.imshow('BW',imageBW)

while(1):
	if flag == 1:
		imageBW = binarize(imageHSV)
		imageBW = 255-imageBW #Invert color: detector needs black blobs, ie. background is white
		kernel = np.ones((3, 3))
		imageBW = cv2.dilate(imageBW,kernel) #remove small blob
		imageBW = cv2.erode(imageBW,kernel)#fill small holes
		cv2.imshow('BW',imageBW)
		flag = 0

	time.sleep(0.05)
	k = cv2.waitKey(1) & 0xFF
	if k == 27: # Esc key to stop
		break

cv2.destroyAllWindows()
