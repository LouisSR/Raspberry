#! /usr/bin/python
import sys
import cv2
import numpy as np;
from datetime import datetime

class BlobDetection:
	def __init__(self, debug=False, path=""):
		# Setup SimpleBlobDetector parameters.
		params = cv2.SimpleBlobDetector_Params()

		#Filter by color: do not work if blob has hole
		params.filterByColor = True 
		blobColor = 0 #Black

		#Change repeatability
		params.minRepeatability = 1
		
		# Change thresholds
		params.minThreshold = 120
		params.maxThreshold = params.minThreshold+30
		params.thresholdStep = 50

		# Filter by Area.
		params.filterByArea = True
		params.minArea = 100
		params.maxArea = 70000

		# Filter by Circularity
		params.filterByCircularity = False
		params.minCircularity = 0.1

		# Filter by Convexity
		params.filterByConvexity = False
		params.minConvexity = 0.87
		    
		# Filter by Inertia
		params.filterByInertia = False
		params.minInertiaRatio = 0.1

		# Create a detector with the parameters
		self.detector = cv2.SimpleBlobDetector_create(params)

		self.debug = debug
		self.path = path

	def binarize(self,color):
		#Change BGR to HSV
		image_hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)

		color_interval = 7
		max_hue = 180

		if color < color_interval:
			low_hue = max_hue - color_interval + color
			high_hue = color + color_interval 
			two_ranges = True
		elif color > max_hue - color_interval:
			low_hue = color - color_interval
			high_hue = color + color_interval - max_hue
			two_ranges = True
		else:
			high_hue = color + color_interval
			low_hue = color - color_interval
			two_ranges = False

		high_color = np.array((high_hue, 255, 255))
		low_color = np.array((low_hue, 50, 50))

		if self.debug:
			print "[Binarize] Color: %d --> [%d, %d]" % (color, low_hue, high_hue), two_ranges

		if two_ranges:
			min_color = np.array((0, 50, 50))
			max_color = np.array((max_hue, 255, 255))
			imageBW = cv2.inRange(image_hsv, min_color, high_color) + cv2.inRange(image_hsv, low_color, max_color)
		else:
			imageBW = cv2.inRange(image_hsv, low_color, high_color)

		imageBW = 255-imageBW #Invert color: detector needs black blobs, ie. background is white

		return(imageBW)

	def detect(self, image, color, save=True):
		self.image = image

		#Binarize image
		self.imageBW = self.binarize(color)
		
		# Detect blobs
		self.keypoints = self.detector.detect(self.imageBW)
		
		#Select best blob
		status = self.select()
		
		#Save images
		if save == True:
			filename = self.path + datetime.now().strftime('%H:%M:%S.%f')[:-4] + ' '
			self.draw(status, filename)

		return status
		
	def select(self):
		if self.keypoints:
			#Init best keypoint
			self.best_keypoint = self.keypoints[0]
			max_size = self.keypoints[0].size
			#Select biggest keypoint
			for i in range(len(self.keypoints)):
				size = self.keypoints[i].size
				if size > max_size:
					max_size = size
					self.best_keypoint = self.keypoints[i]
				if(self.debug):
					print "[Select] keypoint size ",size

			self.best_keypoint_x = int(self.best_keypoint.pt[0])
			self.best_keypoint_y = int(self.best_keypoint.pt[1])
			return True
		else:
			if(self.debug):
				print "[Select] No blob!"
			return False

	def draw(self, detected, filename=""):
		#save original image
		name = filename + "original.jpg"
		cv2.imwrite(name, self.image)
	
		#save B&W image with blobs
		name = filename + "blobs.jpg"
		image_with_keypoints = cv2.drawKeypoints(self.imageBW, self.keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
		cv2.imwrite(name, image_with_keypoints)	
		
		if self.debug:
			cv2.imshow("Blobs", image_with_keypoints)
		
		if detected:
			#save colored image with best blob
			name = filename + "bestBlob.jpg"
			#image_with_bestkeypoint = cv2.drawKeypoints(self.image, [self.best_keypoint], np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
			image_with_bestkeypoint = cv2.circle(self.image,(self.best_keypoint_x, self.best_keypoint_y), 10, ((0,255,0)), 5)
			cv2.imwrite(name, image_with_bestkeypoint)

			#Show images
			if self.debug:
				cv2.imshow("BestBlob", image_with_bestkeypoint)
		if self.debug:
			cv2.waitKey(0)


if __name__ == '__main__':

	#Read arguments
	filename = sys.argv[1]
	color = int(sys.argv[2])

	#Init BlobDetection
	blob = BlobDetection(debug=True, path="./images/testblobdetection/")

	# Read image
	im = cv2.imread(filename)

	#Detect blob
	bestblob = blob.detect(im, color)
	if bestblob:
		print "Best blob (%d, %d)" % (blob.best_keypoint_x, blob.best_keypoint_y)
