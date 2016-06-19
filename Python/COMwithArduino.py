#! /usr/bin/python

import smbus
import time

#Protocol :
#CMD, data_length, Data

class COMwithArduino:
	def __init__(self, i2cAddress, readLength, debug=False):
		self.bus = smbus.SMBus(1) # if old raspberry : 0 , else 1
		self.address = i2cAddress
		self.send_cmd = 0x04
		self.read_cmd = 0x20
		self.readLength = readLength
		self.debug = debug
		print "Debug", self.debug

	def Send(self, data):
		data_length = len(data)
		message = [data_length] + data
		if self.debug:
			print 'Message to send: ', message
		try:
			self.bus.write_i2c_block_data(self.address, self.send_cmd, message)
		except IOError:
			if self.debug:
				print "Com with Arduino: Send Error"
			pass

	def Read(self):
		try:
			incomingData = self.bus.read_i2c_block_data(self.address, self.read_cmd, self.readLength)
		except IOError:
			if self.debug:
				print "Com with Arduino: Read Error"
			incomingData = False
			#pass
		if incomingData:
			decodedData = self.decode(incomingData)#check if incomming data are correct
			if self.debug:
				print 'Incoming data', incomingData
				print "Message received: ", decodedData
		else:
			decodedData = False
		return decodedData


	def decode(self, data):
	#Check if start byte and length are correct and return data without start and length bytes
		if data[0] != 15: #test if start byte is expected
			print "Wrong Start byte"
			return False
		length = data[1]
		message = data[2:2+length]

		return message

# def ToBytes(data):
# 	bytes2 = bytes(0);
# 	print "Data", data
# 	for d in data:
# 		high_byte = chr((d>>8) & 0xFF) # use chr() to send a binary value
# 		low_byte = chr(d & 0xFF)
# 		bytes2 = bytes2 + bytes(high_byte) + bytes(low_byte)
# 	return bytes2[1:] #remove the first 0


if __name__ == "__main__":

	arduino = COMwithArduino(0x12, debug=True)
	arduino.Send([110, 200, 15])
	# Pause de 1 seconde pour laisser le temps au traitement de se faire
	time.sleep(1)
	arduino.Read()

