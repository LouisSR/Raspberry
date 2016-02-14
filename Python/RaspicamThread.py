#! /usr/bin/python

import io
import time
import threading
import numpy as np
import cv2
import picamera
import sys

from blobDetection import BlobDetection

#Initialization
iteration = 0
done = False
lock = threading.Lock()
pool = []
chrono = []

#Constants
frames = 30
framerate = 5
capture_resolution = (800,600)
resize_factor = 2
image_sized = (capture_resolution[0]/resize_factor, capture_resolution[1]/resize_factor)
color = int(sys.argv[1])


class ImageProcessor(threading.Thread):
    def __init__(self):
        super(ImageProcessor, self).__init__()
        self.stream = io.BytesIO()
        self.event = threading.Event()
        self.terminated = False
        self.start()
        self.process_time = 0
        self.blob = BlobDetection(debug=False, path="./images/test/")

    def run(self):
        # This method runs in a separate thread
        global done
        global iteration
        while not self.terminated:
            # Wait for an image to be written to the stream
            if self.event.wait(1):
                try:
                    self.stream.seek(0)
                    # Read the image and do some processing on it
                    # Construct a numpy array from the stream
                    data = np.fromstring(self.stream.getvalue(), dtype=np.uint8)
                    image = cv2.imdecode(data, 1)
                    if iteration%10:
                        status = self.blob.detect(image, color, save=False)
                    else:
                        status = self.blob.detect(image, color, save=True)
                    if not status :
                        print "No blob"
                    # Set done to True if you want the script to terminate
                    # at some point
                    chrono.append(time.time())
                    iteration += 1
                    if iteration >= frames-1:
                        done = True
                finally:
                    # Reset the stream and event
                    self.stream.seek(0)
                    self.stream.truncate()
                    self.event.clear()
                    # Return ourselves to the pool
                    with lock:
                        pool.append(self)

def streams():
    while not done:
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

with picamera.PiCamera() as camera:
    #Create a pool of image processors
    pool = [ImageProcessor() for i in range(3)]
    camera.resolution = capture_resolution
    camera.framerate = framerate
    #camera.start_preview()
    time.sleep(2)
    time_start = time.time()
    camera.capture_sequence(streams(), use_video_port=True, resize=image_sized)

time_end = time.time()
loop_time = time_end - time_start

# Shut down the processors in an orderly fashion
while pool:
    with lock:
        processor = pool.pop()
    processor.terminated = True
    processor.join()

chrono2 = [ ("%.3f" % mtime )[-7:] for mtime in chrono ]
result = [float(chrono2[i+1])-float(chrono2[i]) for i in range(len(chrono2)-1) ]
print "Period", np.mean(result)

for i, mtime in enumerate(result):
    print "\t %d \t%.3f" % (i, mtime)

print "Frames: %d \tFrame rate %.1f" % (frames, framerate)
print "Processing time: %.2fs - %d" % (loop_time/iteration, iteration)
