# Test script which receives data from send_test_cmd.py
# Basically written to implement all the "backend" stuff
# 	for the ARCA Groundcontrol GUI.

import socket
import time

ip_experiment = "127.0.0.1"
ip_planeplotter = "127.0.0.1"
port_data   = 10000
port_health = 10001
port_uplink = 10002
port_planeplotter = 1232


def handleHealthData():
	countTempSensors = 6
	udpSocketHealth = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	try:
		udpSocketHealth.bind((ip_experiment, port_health)) 
		rawHealthData, addr = udpSocketHealth.recvfrom(1024)

		healthData = rawHealthData.split(",")

		print rawHealthData	

		print "Last Command received: %s \n" % time.ctime(int(healthData[0])) 

		for n in range(countTempSensors):
			tempValue = float(healthData[n + 1]) / 1000
			print "Sensor #" + str(n) + ": " + str(tempValue)

	finally: 
		udpSocketHealth.close()


def handleADSBdata():
	udpSocketData = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	try:
		udpSocketData.bind((ip_experiment, port_data)) 
		rawData, addr = udpSocketData.recvfrom(1024) 

		data = rawData.split("\n")
		preamble = data[0].split(",")

		print "Last Command received: %s \n" % time.ctime(int(preamble[0])) 

		for i in range(int(preamble[1])):
			print "*%s;\r\n\0" % data[i + 1]
			sendDataToPlaneplotter(data[i + 1], 0)

	finally: 
		udpSocketData.close()


def sendDataToPlaneplotter(dataToSend, disconect):
	# Planeplotter wants to have a client to talk to
	# We are setting up the connection here	
	# If disconect = 1 -> Close tcp conncetion

	# Do we still have a connection?
	if komm != 0:
		print "komm != 0"
		planeplotterMessage = "*%s;\r\n\0" % data[i + 1]
		komm.send(planeplotterMessage)
	else:
		print "Trying to build up a connection"
		planeplotterSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
		planeplotterSocket.bind((ip_planeplotter, port_planeplotter)) 
		planeplotterSocket.listen(1)
		komm, addr = sock.accept()
		
		planeplotterMessage = "*%s;\r\n\0" % data[i + 1]
		komm.send(planeplotterMessage)

	if disconect == 1:
		planeplotterSocket.close()


#handleHealthData()
handleADSBdata()


