#! /usr/bin/python

import time
import math
import sys, os
from threading import Thread
#from minIMU import IMUPoller
from COMwithArduino import COMwithArduino
#from gpsUltimate import GpsPoller #Conflict with Camera!
from saveData import SaveData
from ImageAquisition import ImageAquisition

Done = False

CAMERA_RUNNING = 0
CAMERA_START = 1
CAMERA_STOP = 2
CAMERA_STOPPED = 3
Camera_state = CAMERA_STOPPED
BestBlob = []

MODE_REMOTE = 0 #remote only
MODE_CAMERA = 1 # autonomous mode with camera
MODE_SHUTDOWN = 2 # shutdown mode
Mode = MODE_REMOTE
		 
IMU_position = []
IMU_accel = []
IMU_gyro = []
COM_message = []
GPS_position = []
Camera_target = []



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
		self.arduino = COMwithArduino(0x12, 10, debug=False)
		self.transmission_time = 0.005
		self.sleep_time = sleep_time - self.transmission_time
		self.debug = debug
		#Logging init
		self.log = SaveData("./images/test/log")
		COM_header = ["Battery", "Luminosity", "Remote Speed", "Remote Steering", "Remote Switch", "Motor Speed", "Steering", "Motor State"]
		Motor_header = ["Motor speed", "Steering"]
		#IMU_header = ["IMU Roll", "IMU Pitch", "IMU Yaw", "Gyro Roll", "Gyro Pitch", "Gyro Yaw", "Acc X", "Acc Y", "Acc Z"]
		#GPS_header = ["GPS Longitude", "GPS Lattitude", "GPS altitude"]
		Camera_header = ["Camera X", "Camera Y"]
		header = ["Time"]
		header.extend(COM_header)
		header.extend(Motor_header)
		#header.extend(IMU_header)
		#header.extend(GPS_header)
		header.extend(Camera_header)
		self.log.write(header)

	def run(self):
		while not Done:
			
			global COM_message, Mode
			COM_message = self.arduino.Read() #Receive data from Arduino
			if COM_message == False:
				continue #skip the rest of this while loop and goes back to testing the expression
			#if self.debug:
				#print "COM: ", COM_message
			battery_voltage = COM_message[0]
			remote_speed = COM_message[2]-100
			remote_steering = COM_message[3]-100
			Mode = COM_message[4] #Mode = switch value

			if battery_voltage > 70:
				if Mode == MODE_REMOTE: #if Mode = 0, no processing, data are only logged
					motor_speed = remote_speed
					motor_steering = remote_steering
				elif Mode == MODE_CAMERA: #Autonomous mode with camera
					if BestBlob:
						motor_steering = int( (BestBlob[0]-Camera_target[0]) ) #image width
						motor_speed = int( (Camera_target[1] - BestBlob[1])/2 ) #image height
					else:
						motor_speed = 0
						motor_steering = 0
				else: #if Mode = 2, stop the car
					motor_speed = 0
					motor_steering = 0

			else: # Low battery : stop the car
				motor_speed = 0
				motor_steering = 0

			message2Arduino = [motor_speed+100, motor_steering+100, 0]
			if self.debug:
				print' BestBlob: ',BestBlob[0],' \t', motor_steering
			self.arduino.Send(message2Arduino) #Send data to Arduino
			#Log data
			data = []
			data.extend([time.time()])
			data.extend(COM_message)
			data.extend(message2Arduino)
			data.extend(BestBlob)
			#data.extend(IMU_position)
			#data.extend(IMU_gyro)
			#data.extend(IMU_accel)
			#data.extend(GPS_position)
			#data.extend(im_proc)
			# if self.debug:
			# 	print "Logging: ", data
			self.log.write(data)
			time.sleep(self.sleep_time)
		self.log.close()
		if self.debug:
			print "Thread COM exiting"

		
if __name__ == '__main__':

	#Camera Init
	resolution_width = 800
	resolution_height = 600
	resize_factor = 2
	Camera_target = [50, 40] #Init target Best blob position
	color = int(sys.argv[1])
	framerate = int(sys.argv[2])

	#thread_imu = Thread_IMU(0.05, debug=False)
	thread_com = Thread_COM(0.1, debug=True)
	#thread_gps = Thread_GPS(0.5, debug=False)
	
	print '\nStarting with:', color, framerate, '\n'
	#Start threads
	time_start = time.time()
	#thread_imu.start()
	#thread_gps.start()
	time.sleep(0.5) # Wait for data aquisition
	thread_com.start()



	while not Done:
		time.sleep(0.1)
		#Update Camera_state
		if Mode == 1 and Camera_state == CAMERA_STOPPED: #Start camera when entering Mode 1
			Camera_state = CAMERA_START
			print 'Camera start'
		elif Mode != 1 and Camera_state == CAMERA_RUNNING: #Stop camera when exiting Mode 1
			Camera_state = CAMERA_STOP
			
		#Start or stop camera
		if Camera_state == CAMERA_START:
			thread_camera = ImageAquisition((resolution_width,resolution_height), framerate, color, resize_factor=resize_factor, debug=True)
			thread_camera.start()
			Camera_state = CAMERA_RUNNING
		elif Camera_state == CAMERA_STOP:
			thread_camera.stop()
			Camera_state = CAMERA_STOPPED
			print 'Camera stop'

		if Camera_state == CAMERA_RUNNING:
			BestBlob = thread_camera.getBlob()
	
		if Mode == 2:
			Done = True

	time.sleep(2) # Wait for threads to stop
	os.system("sudo shutdown -h now")  # Shutdown
