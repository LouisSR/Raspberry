#! /usr/bin/python

import sys, getopt

sys.path.append('.')
import RTIMU
import os.path
import time
import math

SETTINGS_FILE = "RTIMULib"

class IMUPoller:

	def __init__(self):
		print("Using settings file " + SETTINGS_FILE + ".ini")
		if not os.path.exists(SETTINGS_FILE + ".ini"):
		  print("Settings file does not exist, will be created")

		self.s = RTIMU.Settings(SETTINGS_FILE)
		self.imu = RTIMU.RTIMU(self.s)

		print("IMU Name: " + self.imu.IMUName())

		if (not self.imu.IMUInit()):
		    print("IMU Init Failed")
		    sys.exit(1)
		else:
		    print("IMU Init Succeeded")

		# this is a good time to set any fusion parameters

		self.imu.setSlerpPower(0.02)
		self.imu.setGyroEnable(True)
		self.imu.setAccelEnable(True)
		self.imu.setCompassEnable(True)

		poll_interval = self.imu.IMUGetPollInterval()
		print("Recommended Poll Interval: %dmS\n" % poll_interval)
		#time.sleep(poll_interval*1.0/1000.0)
		
	def getIMU_position(self):
		if (self.imu.IMURead()):
			data = self.imu.getIMUData()
			return(data["fusionPose"])
		else:
			return([0,0,0])
	    

if __name__ == '__main__':
	imup = IMUPoller()
	time.sleep(0.2)
	while True:
		IMU_position = imup.getIMU_position()
		if (IMU_position[0] != 0):
			print("r: %f p: %f y: %f" % (math.degrees(IMU_position[0]), 
		        math.degrees(IMU_position[1]), math.degrees(IMU_position[2])))
		time.sleep(0.2)
