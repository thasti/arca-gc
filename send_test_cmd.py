# Send test commands.

import socket
import time

ip_gc = "127.0.0.1"
port_data   = 10000
port_health = 10001
port_uplink = 10002


def sendData():
	adsbMessage = "%s,2\n1234567890123456789012345678\n1234567890123456789012345679\n" % (int(time.time()))
	udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	udpSocket.sendto(adsbMessage, (ip_gc, port_data))
	udpSocket.close()


def sendTime():
	timeMessage = "%s\n" % (int(time.time()))
	udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	udpSocket.sendto(timeMessage, (ip_gc, port_data))
	udpSocket.close()


def sendHealthData():
	healthData = "%s,45000,46000,34000,0,0,-12000" % (int(time.time()))
	udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	udpSocket.sendto(healthData, (ip_gc, port_health))
	udpSocket.close()

# UNIX Zeit in lesbares Format wandeln:
# 	-> time.ctime(int("UNIX-Timestamp"))

sendData()
sendHealthData()
