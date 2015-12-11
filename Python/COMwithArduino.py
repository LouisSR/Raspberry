#! /usr/bin/python

import smbus
import time

# Remplacer 0 par 1 si nouveau Raspberry
bus = smbus.SMBus(1)
address = 0x12

#Protocol :
#CMD, data_length, Data, Checksum

def Send2Arduino(cmd, data):
#Message = start,length,data
	data_length = len(data)
	#message = bytes(data_length) + bytes(data_length) + ToBytes(data)
	message = [data_length]+data+[Checksum(data)]
	print 'Message : ', message
	bus.write_i2c_block_data(address,cmd,message)

def ReadFromArduino():
	incomingData = bus.read_i2c_block_data(address,0x20,5)
	print 'Incoming data', incomingData
	incomingData = decode(incomingData)#check if incomming data are correct
	print "Message = ", incomingData
	#return incomingData

def Checksum(string):
	#todo
	return(255)

def decode(data):
#Check if start byte and length are correct and return data without start and length bytes
	if data[0] != 15: #test if start byte is expected
		print "Wrong Start byte"
		return None
	if data[-1] != 255:
		print "Wrong Checksum"
		return None

	length = data[1]
	return data[2:2+length]

def ToBytes(data):
	bytes2 = bytes(0);
	print "Data", data
	for d in data:
		high_byte = chr((d>>8) & 0xFF) # use chr() to send a binary value
		low_byte = chr(d & 0xFF)
		bytes2 = bytes2 + bytes(high_byte) + bytes(low_byte)
	return bytes2[1:] #remove the first 0

#ser.close()


if __name__ == "__main__":
	Send2Arduino(0x04, [110, 200, 15])
	# Pause de 1 seconde pour laisser le temps au traitement de se faire
	time.sleep(1)
	ReadFromArduino()

