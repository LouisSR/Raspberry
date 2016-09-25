#! /usr/bin/python

import io
import time
from threading import Thread, Lock ,Event
import picamera
import sys
import cv2
import numpy as np

from blobDetection import BlobDetection

#Initialization
iteration = 0
lock = Lock()
pool = []
BestBlob = []

class ImageProcessor(Thread):
	def __init__(self, color, debug=False):
		super(ImageProcessor, self).__init__()
		self.stream = io.BytesIO()
		self.event = Event()
		self.terminated = False
		self.process_time = 0
		self.color = color
		self.debug = debug
		self.blob = BlobDetection(debug=False, path="./images/test/")
		self.start()

	def run(self):
		# This method runs in a separate thread
		global iteration, lock, pool, BestBlob
		while not self.terminated:
			# Wait for an image to be written to the stream
			if self.event.wait(1):
				try:
					self.stream.seek(0)
					# Read the image and do some processing on it
					# Construct a numpy array from the stream
					data = np.fromstring(self.stream.getvalue(), dtype=np.uint8)
					image = cv2.imdecode(data, 1)
					if self.debug:
						print '\nIteration: ', iteration,
					if iteration%10: #Save every 10th image
						blob_detected = self.blob.detect(image, self.color, save=False)
					else:
						blob_detected = self.blob.detect(image, self.color, save=True)
					if blob_detected:
						BestBlob = [self.blob.best_keypoint_x, self.blob.best_keypoint_y]
						BestBlob = [self.blob.best_keypoint_x, 150]
						if self.debug:
							print ' Blob: ', BestBlob
					else:
						BestBlob = []
						print " No blob"
					iteration += 1

				finally:
					# Reset the stream and event
					self.stream.seek(0)
					self.stream.truncate()
					self.event.clear()
					# Return ourselves to the pool
					with lock:
						pool.append(self)



class ImageAquisition(Thread):
	def __init__(self, resolution, framerate, color, resize_factor=1, debug=False):
		super(ImageAquisition, self).__init__()
		print "Camera Init"
		global pool
		self.nb_cores = 3
		pool = [ImageProcessor(color, debug=debug) for i in range(self.nb_cores)]
		self.debug = debug
		self.camera = picamera.PiCamera()
		self.camera.framerate = framerate
		self.camera.resolution = resolution
		self.resized = (resolution[0]/resize_factor, resolution[1]/resize_factor)
		#camera.start_preview()
		time.sleep(2)
		self.aquire = True

	def getBlob(self):
		#This function retunrs Blob coordinates as integers [-100,100]
		global BestBlob
		if BestBlob:
			blob = [ 100 * BestBlob[0] / self.resized[0], 100 * BestBlob[1] / self.resized[1] ]
		else:
			blob = BestBlob
		return blob


	def run(self):
		try:
			self.camera.capture_sequence(self.streams(), use_video_port=True, resize=self.resized)
		finally:
			if self.debug:
				print "Cam close"
			self.camera.close()

	def stop(self):
		global lock, pool, iteration
		self.aquire = False
		time.sleep(0.5)
		if self.debug:
			print"Thread Cam exiting..."
		# Wait until every thread is in the pool
		while len(pool) != self.nb_cores:
			time.sleep(0.1)
		# Shut down the processors in an orderly fashion
		while pool:
			with lock:
				processor = pool.pop()
			processor.terminated = True
			processor.join()
		if self.debug:
			print"Done"
		return iteration

	def streams(self):
		while self.aquire:
			with lock:
				if pool:
					processor = pool.pop()
				else:
					processor = None
			if processor:
				yield processor.stream
				processor.event.set()
			else:
				# When the pool is starved, wait a while for it to refill
				time.sleep(0.05)


if __name__ == '__main__':

	#Constants
	framerate = 2
	capture_resolution = (800,600)
	resize_factor = 2
	color = int(sys.argv[1])
	aquisition = ImageAquisition(capture_resolution,framerate, color, resize_factor=resize_factor,debug=True)
	print 'Started Aquisition'
	aquisition.start()
	time.sleep(5)
	print 'Stopping Aquisition'
	aquisition.stop()
	print 'End of Processing'
