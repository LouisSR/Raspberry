#! /usr/bin/python
# Written by Dan Mandle http://dan.mandle.me September 2012
# License: GPL 2.0
 
import os
from gps import *
import time
from threading import Thread
 
class GpsPoller(Thread):
	def __init__(self):
		super(GpsPoller, self).__init__()
		self.gpsd = gps(mode=WATCH_ENABLE) #starting the stream of info
		self.running = True #setting the thread running to true

	def run(self):
		while self.running:
			if self.gpsd.waiting():
				self.gpsd.next() #this will continue to loop and grab EACH set of gpsd info to clear the buffer
	def getGpsPosition(self):
		latitude = self.gpsd.fix.latitude
		longitude = self.gpsd.fix.longitude
		altitude = self.gpsd.fix.altitude
		return [latitude, longitude, altitude]

	def displayAll(self):
		os.system('clear')
		print
		print ' GPS reading'
		print '----------------------------------------'
		print 'latitude    ' , self.gpsd.fix.latitude
		print 'longitude   ' , self.gpsd.fix.longitude
		print 'time utc    ' , self.gpsd.utc,' + ', self.gpsd.fix.time
		print 'altitude (m)' , self.gpsd.fix.altitude
		print 'eps         ' , self.gpsd.fix.eps
		print 'epx         ' , self.gpsd.fix.epx
		print 'epv         ' , self.gpsd.fix.epv
		print 'ept         ' , self.gpsd.fix.ept
		print 'speed (m/s) ' , self.gpsd.fix.speed
		print 'climb       ' , self.gpsd.fix.climb
		print 'track       ' , self.gpsd.fix.track
		print 'mode        ' , self.gpsd.fix.mode
		print
		print 'sats        ' , self.gpsd.satellites
 
if __name__ == '__main__':

	myGps = GpsPoller() # create the thread
	try:
		myGps.start() # start it up
		while True:
			#It may take a second or two to get good data
			#myGps.displayAll()

			time.sleep(2) #set to whatever
		 
 
	except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
		print "\nKilling Thread... ",
		myGps.running = False
		myGps.join() # wait for the thread to finish what it's doing
	print "Done.\nExiting."