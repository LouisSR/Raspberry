#! /usr/bin/python

import time
import math
import sys
from threading import Thread
from minIMU import IMUPoller
from COMwithArduino import COMwithArduino
from gpsUltimate import GpsPoller
from saveData import SaveData
from ImageAquisition import ImageAquisition

Done = False

IMU_position = []
COM_message = []
GPS_position = []

class Thread_IMU(Thread):
	def __init__(self, sleep_time, debug=False):
		super(Thread_IMU, self).__init__()
		print "Thread IMU init"
		self.imup = IMUPoller()
		self.sleep_time = sleep_time
		self.debug = debug
	
	def run(self):
		while not Done:
			global IMU_position
			IMU_position = self.imup.getIMU_position()
			if self.debug:
				print "IMU: Roll %.2f" % math.degrees(IMU_position[0])
			time.sleep(self.sleep_time)
		if self.debug:
			print "Thread IMU exiting"

class Thread_COM(Thread):
	def __init__(self, sleep_time, debug=False):
		super(Thread_COM, self).__init__()
		print "COM Init"
		self.arduino = COMwithArduino(0x12)
		self.transmission_time = 0.005
		self.sleep_time = sleep_time - self.transmission_time
		self.debug = debug

	def run(self):
		while not Done:
			try:
				self.arduino.Send( [111, 97] )
			except IOError:
				if self.debug:
					print "Com IO Error"
				pass
			time.sleep(self.transmission_time)
			global COM_message
			COM_message = self.arduino.Read()
			if self.debug:
				print "COM: ", COM_message
			time.sleep(self.sleep_time)
		if self.debug:
			print "Thread COM exiting"

class Thread_GPS(Thread):
	def __init__(self, sleep_time, debug=False):
		super(Thread_GPS, self).__init__()
		print "GPS Init"
		self.poller = GpsPoller() # create the GPS poller thread
		self.poller.start()
		self.sleep_time = sleep_time
		self.debug = debug

	def run(self):
		while not Done:
			global GPS_position
			GPS_position = self.poller.getGpsPosition()
			if self.debug:
				print 'GPS:', GPS_position
			time.sleep(self.sleep_time)
		self.stop()

	def stop(self):
		print "Thread GPS exiting"
		self.poller.running = False
		self.poller.join() # wait for the thread to finish what it's doing

class Thread_Logger(Thread):
	def __init__(self, sleep_time, debug=False):
		super(Thread_Logger, self).__init__()
		print "Logger Init"
		self.sleep_time = sleep_time
		self.log = SaveData("./images/test/log")
		self.debug = debug

	def run(self):
		while not Done:
			data = []
			data.extend(IMU_position)
			data.extend(GPS_position)
			data.extend(COM_message)
			#data.extend(im_proc)
			if self.debug:
				print "Logger: ", data
			self.log.write(data)
			time.sleep(self.sleep_time)
		self.log.close()
		if self.debug:
			print "Thread Logger exiting"

		
if __name__ == '__main__':
	#Init

	framerate = 2
	capture_resolution = (800,600)
	resize_factor = 2
	color = int(sys.argv[1])

	thread_imu = Thread_IMU(0.1, debug=False)
	thread_com = Thread_COM(0.3, debug=False)
	thread_gps = Thread_GPS(0.5, debug=False)
	thread_logger = Thread_Logger(0.5, debug=False)
	thread_camera = ImageAquisition(capture_resolution, framerate, color, resize_factor=resize_factor, debug=False)

	#Start threads
	thread_camera.start()
	thread_imu.start()
	thread_gps.start()
	thread_com.start()
	thread_logger.start()

	time.sleep(5)
	
	#Stop threads
	Done = True
	thread_camera.stop()
