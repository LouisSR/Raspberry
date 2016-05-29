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
		
	def getIMU(self):
		if (self.imu.IMURead()):
			data = self.imu.getIMUData()
			position = data['fusionPose']
			gyro = data['gyro']
			accel = data['accel']
			return(position, gyro, accel)
		else:
			return(False, False, False)
	    

if __name__ == '__main__':
	imup = IMUPoller()
	time.sleep(0.2)
	while True:
		#IMU_position = imup.getIMU_position()
		#if (IMU_position[0] != 0):
			#print("r: %f p: %f y: %f" % (math.degrees(IMU_position[0]), 
		     #   math.degrees(IMU_position[1]), math.degrees(IMU_position[2])))
		#IMU_Gyro = imup.getIMU_gyro()
		#if(IMU_Gyro[0]!=0):
		#print("Gyro Yaw: %f" % (IMU_Gyro[2]) )
		IMU_position, IMU_gyro, IMU_accel = imup.getIMU()
		if(IMU_position!=False):
			print("\nPosition: r: %f p: %f y: %f" % (math.degrees(IMU_position[0]), 
						math.degrees(IMU_position[1]), 
						math.degrees(IMU_position[2]) ) )
			print("Gyro: r: %f p: %f y: %f" % (IMU_gyro[0], IMU_gyro[1], IMU_gyro[2]) )
			print("Accel: X: %f Y: %f Z: %f" % (IMU_accel[0], IMU_accel[1], IMU_accel[2]) )
		time.sleep(1)
