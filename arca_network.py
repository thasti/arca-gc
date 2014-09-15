# Small little server which simulates the arca
# experiment. 
# The server sends data to the ground station.
#  
# The experiment will have a fixed adress:
# 	-> 172.16.18.42
#
# This server runs in client mode. 

# Planeplotter moechte diesen Aufbau hier haben.


import socket

adress_gc = "127.0.0.1"
port_data   = 10000
port_health = 10001
port_uplink = 10002
port_planeplotter = 1232

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
sock.bind((adress_gc, port_uplink)) 
sock.listen(1)

try: 
	while True: 

		komm, addr = sock.accept()
		data = komm.recv(1024)
		print "[%s] %s" % (addr[0], data)
#	print komm
#	nachricht = raw_input("Antwort: ") 
#	komm.send(nachricht)

#	if komm:
#		print "test"
	

#		komm, addr = sock.accept() 
	#	while True: 
	#		data = komm.recv(1024)

		#	print "[%s] %s" % (addr[0], data) 
		#	nachricht = raw_input("Antwort: ") 
		#	komm.send(nachricht) 

finally: 
	sock.close()
