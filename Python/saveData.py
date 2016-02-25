#! /usr/bin/python

from datetime import datetime
import time

class SaveData:
	def __init__(self, filename, with_date = False, delimiter=', ', debug=False):
		if with_date:
			filename = filename + datetime.now().strftime('%H:%M:%S') + '.txt'
		else:
			filename += '.txt'
		self.debug = debug
		if self.debug:
			print 'SaveData: ', filename
		self.f = open(filename, 'w')
		self.delimiter = delimiter

	def write(self, data_list):
		data = self.delimiter.join(map(str,data_list))
		data += "\n"
		if self.debug:
			print 'SaveData:', data
		self.f.write(data)

	def close(self):
		self.f.close()
		if self.debug:
			print 'SaveData: File closed'


if __name__ == '__main__':

	log = SaveData("log", debug=True)
	mylist = ['imu', 'gps', 'Arduino', 1]
	a = [time.time()]
	a.extend(mylist)
	log.write(a)
	log.close()
