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
Mode = 0 # mode == 0: remote only
		 # mode == 1: remote with IMU correction
		 # mode == 2: autonomous mode with camera

IMU_position = []
IMU_accel = []
IMU_gyro = []
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
			global IMU_position, IMU_gyro, IMU_accel
			IMU_position, IMU_gyro, IMU_accel = self.imup.getIMU()
			time.sleep(self.sleep_time)
		if self.debug:
			print "Thread IMU exiting"

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

class Thread_COM(Thread):
	def __init__(self, sleep_time, debug=False):
		super(Thread_COM, self).__init__()
		print "COM Init"
		self.arduino = COMwithArduino(0x12, 10, debug)
		self.transmission_time = 0.005
		self.sleep_time = sleep_time - self.transmission_time
		self.debug = debug
		#Logging init
		self.log = SaveData("./images/test/log")
		COM_header = ["Battery", "Luminosity", "Remote Speed", "Remote Steering", "Remote Switch", "Motor Speed", "Steering", "Motor State"]
		Motor_header = ["Motor speed", "Steering"]
		IMU_header = ["IMU Roll", "IMU Pitch", "IMU Yaw", "Gyro Roll", "Gyro Pitch", "Gyro Yaw", "Acc X", "Acc Y", "Acc Z"]
		GPS_header = ["GPS Longitude", "GPS Lattitude", "GPS altitude"]
		Camera_header = ["Camera X", "Camera Y"]
		header = ["Time"]
		header.extend(COM_header)
		header.extend(Motor_header)
		header.extend(IMU_header)
		header.extend(GPS_header)
		header.extend(Camera_header)
		self.log.write(header)
		self.factorP = 60 # P factor for steering control

	def run(self):
		while not Done:
			
			global COM_message, Mode
			COM_message = self.arduino.Read() #Receive data from Arduino
			if COM_message == False:
				continue #skip the rest of this while loop and goes back to testing the expression
			if self.debug:
				print "COM: ", COM_message
			battery_voltage = COM_message[0]
			remote_speed = COM_message[2]-100
			remote_steering = COM_message[3]-100
			Mode = COM_message[4] 
			if battery_voltage > 70:
				if Mode == 1: #remote with IMU correction
					if self.debug:
						print "steering: ", remote_steering, self.factorP, IMU_gyro[2]
					motor_steering = int(remote_steering - self.factorP*IMU_gyro[2])
					motor_speed = remote_speed
				elif Mode == 2: #Autonomous mode with camera
					motor_speed = remote_speed
					motor_steering = remote_steering
				else: #if Mode = 0, no processing, data are only logged
					motor_speed = remote_speed
					motor_steering = remote_steering
			else: # Low battery : stop the car
				motor_speed = 0
				motor_steering = 0

			message2Arduino = [motor_speed+100, motor_steering+100, 0]
			self.arduino.Send(message2Arduino) #Send data to Arduino
			#Log data
			data = []
			data.extend([time.time()])
			data.extend(COM_message)
			data.extend(message2Arduino)
			data.extend(IMU_position)
			data.extend(IMU_gyro)
			data.extend(IMU_accel)
			data.extend(GPS_position)
			#data.extend(im_proc)
			# if self.debug:
			# 	print "Logging: ", data
			self.log.write(data)
			time.sleep(self.sleep_time)
		self.log.close()
		if self.debug:
			print "Thread COM exiting"

		
if __name__ == '__main__':
	#Init

	capture_resolution = (800,600)
	resize_factor = 2
	color = int(sys.argv[1])
	framerate = int(sys.argv[2])

	thread_imu = Thread_IMU(0.05, debug=False)
	thread_com = Thread_COM(0.1, debug=True)
	#thread_gps = Thread_GPS(0.5, debug=False)
	#thread_camera = ImageAquisition(capture_resolution, framerate, color, resize_factor=resize_factor, debug=False)

	print ''
	#Start threads
	time_start = time.time()
	#thread_camera.start()
	thread_imu.start()
	#thread_gps.start()
	time.sleep(0.5) # Wait for data aquisition
	thread_com.start()


	time.sleep(10)
	
	#Stop threads
	Done = True
	#images_processed = thread_camera.stop()
	loop_time = time.time()-time_start
	
	# print ''
	# print 'Loop time:         %.1f' % (loop_time/images_processed)
	# print 'Processed Images: ', images_processed
	# print 'Real framerate:    %.2f'  % (images_processed/loop_time)
	# print ''
