#! /usr/bin/python

import cv2
import numpy as np;

class BlobDetection:
	def __init__(self, debug=False):
		# Setup SimpleBlobDetector parameters.
		params = cv2.SimpleBlobDetector_Params()

		# Change thresholds
		params.minThreshold = 100
		params.maxThreshold = params.minThreshold+11

		# Filter by Area.
		params.filterByArea = True
		params.minArea = 50

		# Filter by Circularity
		params.filterByCircularity = False
		params.minCircularity = 0.1

		# Filter by Convexity
		params.filterByConvexity = False
		params.minConvexity = 0.87
		    
		# Filter by Inertia
		params.filterByInertia = True
		params.minInertiaRatio = 0.1

		# Create a detector with the parameters
		self.detector = cv2.SimpleBlobDetector_create(params)

		self.debug=debug

	def binarize(self):
		return(self.image)

	def detect(self, image):
		self.image = image
		#Binarize image
		self.imageBW = self.binarize()

		# Detect blobs
		self.keypoints = self.detector.detect(self.imageBW)

		#Select best blob
		self.select()

	def select(self):
		if self.keypoints:
			max_size = 0
			self.best_keypoint = self.keypoints[0]
			for i in range(len(self.keypoints)):
				size = self.keypoints[i].size
				if size > max_size:
					max_size = size
					self.best_keypoint = self.keypoints[i]

			self.best_keypoint_x = int(self.best_keypoint.pt[0])
			self.best_keypoint_y = int(self.best_keypoint.pt[1])
			if(self.debug):
				print("Best keypoint",self.best_keypoint_x, self.best_keypoint_y, max_size)
			
		else:
			if(self.debug):
				print("No blob!")

	def draw(self):
		#save B&W image
		cv2.imwrite("./images/blackAndWhite.jpg", self.imageBW)

		#save B&W image with blobs
		image_with_keypoints = cv2.drawKeypoints(self.imageBW, self.keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
		cv2.imwrite("./images/blobs.jpg", image_with_keypoints)			

		#save colored image with best blob
		image_with_bestkeypoint = cv2.drawKeypoints(self.image, [self.best_keypoint], np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
		cv2.circle(image_with_bestkeypoint,(self.best_keypoint_x, self.best_keypoint_y), 10, ((0,255,0)), 5)
		cv2.imwrite("./images/bestBlob.jpg", image_with_bestkeypoint)
		
		#Show images
		if(self.debug):
			cv2.imshow("Blobs", image_with_keypoints)
			cv2.imshow("BestBlob", image_with_bestkeypoint)
			cv2.waitKey(0)


if __name__ == '__main__':

	#Init BlobDetection
	blob = BlobDetection(debug=True)

	# Read image
	im = cv2.imread("./images/TestBlobs.jpg", cv2.IMREAD_GRAYSCALE)

	#Detect blob
	blob.detect(im)

	#Draw blob
	blob.draw()
