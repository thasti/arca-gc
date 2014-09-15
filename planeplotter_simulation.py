# ARCA planeplotter simulation software.
# This snotty little software communicates with
# the experiment via TCP.
# 
# 

import socket

portPlaneplotter = 1232 
ipPlaneplotter = "127.0.0.1"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
s.connect((ipPlaneplotter, portPlaneplotter))

try: 
#	while True:
	#	nachricht = raw_input("Nachricht: ") 
	#	s.send(nachricht) 
	antwort = s.recv(1024) 
	print "[%s] %s" % (ipPlaneplotter, antwort) 

finally: 
	s.close()
