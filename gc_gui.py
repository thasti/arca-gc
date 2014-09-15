# ARCA Groundstation software.
# This little software communicates with
# the experiment via UDP (downlink) and TCP (uplink).
# Beside that it sends TCP packets to planeplotter.
# 
# 
# Commands:
# 		RA\n -> Reboot ARM
# 		RF\n -> Reset FPGA
#		SA\n -> Shutdown ARM
#	optional:
# 		GL\n -> get CPU load
# 		SY\n -> sync, writes all files
#		TU 1234\n -> set new timestamp with UNIX time
# 
#	ToDo:
# 		- MatplotLib!
#		- TCP send in Funktionen
#		- Dialoge behandeln "Wirklich reseten?"
#
# IP-adress of the experiment will be
#		-> 172.16.18.110
#
# IP-adress of the gc will be
#		-> 172.16.18.111


import wx
import socket
import time
from threading import *

ip_experiment = "172.16.18.110"
port_data   = 10000
port_health = 10001
port_uplink = 10002
port_planeplotter = 1232

# downlink TLM event types
typeHealth = 1
typeData = 2

# Global variable for old adsb timestamp
oldTimestampADSB = int(time.time())

# plane plotter communication (got from socket->accept())
PPcomm = None

worker = [None,None,None]

EVT_RESULT_ID = wx.NewId()

def EVT_RESULT(win, func):
	win.Connect(-1, -1, EVT_RESULT_ID, func)

class ResultEvent(wx.PyEvent):

	def __init__(self, evType, data):
		wx.PyEvent.__init__(self)
		self.SetEventType(EVT_RESULT_ID)
		self.evType = evType
		self.data = data

class HealthReceiver(Thread):
	def __init__(self, notify_window):
		Thread.__init__(self)
		self._notify_window = notify_window
		self.start()

	def run(self):
		temperatures = [0,0,0,0,0,0]
		try:
			udpSocketHealth = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			udpSocketHealth.bind(("0.0.0.0", port_health)) 
		except:
			print "Could not open & bind socket on port " + str(port_health)
			return

		while 1:
			try:
				rawHealthData, addr = udpSocketHealth.recvfrom(1024)
			except:
				udpSocketHealth.close()
				print "Health Thread exception"
				return
			# TODO: write rawHealthData to to file
			healthData = rawHealthData.split(",")
			for n in range(6):
				temperatures[n] = float(healthData[n + 1]) / 1000
			wx.PostEvent(self._notify_window, ResultEvent(typeHealth, temperatures))

class PayloadReceiver(Thread):
	def __init__(self, notify_window):
		Thread.__init__(self)
		self._notify_window = notify_window
		self.start()

	def run(self):
		try:
			udpSocketData = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			udpSocketData.bind(("0.0.0.0", port_data))
		except:
			print "Could not open & bind socket on port " + str(port_data)
			return

		while 1:
			try:
				rawData, addr = udpSocketData.recvfrom(1500)
			except:
				udpSocketHealth.close()
				print "Data Thread exception"
				return
			# TODO: write rawData to to file
			data = rawData.split("\n")
			wx.PostEvent(self._notify_window, ResultEvent(typeData, data))

class PlanePlotterSrv(Thread):
	def __init__(self, notify_window):
		Thread.__init__(self)
		self._notify_window = notify_window
		self.start()

	def run(self):
		global PPcomm
		try:
			planePlotterSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			planePlotterSocket.bind(("0.0.0.0", port_planeplotter))
			planePlotterSocket.listen(1)
		except:
			planePlotterSocket.close()
			print "Could not bind to Planeplotter TCP Port"
			return
		while 1:
			print "Waiting for PlanePlotter connection..."
			PPcomm, addr = planePlotterSocket.accept()
			print "Planeplotter connection accepted!"
			# TODO better blocking check for broken pipe
			PPcomm.recv(1)
			PPcomm = None

class MainWindow(wx.Frame):
	def __init__(self, parent, title):

		bHeight = 25
		bWidth = 130
		dB = 30 # distance Buttons to each other
		dT = 20 # distance text boxes to each other
		sB = 20 # start point of the buttons
		sT = 250 # start point of the text
		x  = 7
		x2 = 10
		x3 = 110

		wx.Frame.__init__(self, parent, title=title, size=(650, 520))

		self.sp = wx.SplitterWindow(self)
		self.p1 = wx.Panel(self.sp, style = wx.SUNKEN_BORDER)
		self.p2 = wx.Panel(self.sp, style = wx.SUNKEN_BORDER)
		self.sp.SplitVertically(self.p1, self.p2, 350)

		self.statusbar = self.CreateStatusBar()
		self.statusbar.SetStatusText("ARCA GC system ready")

		text1 = wx.StaticText(self.p1, label = "Uplink commands", pos = (5, 3))

		self.getAliveSignalButton = wx.Button(self.p1, -1, "Ping experiment", \
				size = (bWidth, bHeight), pos = (x, sB + dB*0))
		self.fpgaResetButton = wx.Button(self.p1, -1, "Hard Reset FPGA", \
				size = (bWidth, bHeight), pos = (x, (sB + dB*1)))
		self.rebootButton = wx.Button(self.p1, -1, "Hard Reset ARM", \
				size = (bWidth, bHeight), pos = (x, (sB + dB*2)))
		self.shutdownButton = wx.Button(self.p1, -1, "Shutdown ARM", \
				size = (bWidth, bHeight), pos = (x, (sB + dB*3)))
		self.closeFilesButton = wx.Button(self.p1, -1, "Sync filesystem", \
				size = (bWidth, bHeight), pos = (x,(sB + dB*4)))
		self.getCpuLoadButton = wx.Button(self.p1, -1, "Get CPU load", \
				size = (bWidth, bHeight), pos = (x, (sB + dB*5)))
		self.setNewTimeButton = wx.Button(self.p1, -1, "Upload time", \
				size = (bWidth, bHeight), pos = (x, (sB + dB*6)))

		self.getAliveSignalButton.Bind(wx.EVT_BUTTON, self.getAliveSignal)
		self.closeFilesButton.Bind(wx.EVT_BUTTON, self.closeFiles)
		self.getCpuLoadButton.Bind(wx.EVT_BUTTON, self.getCpuLoad)
		self.setNewTimeButton.Bind(wx.EVT_BUTTON, self.setTime)
		self.fpgaResetButton.Bind(wx.EVT_BUTTON, self.fpgaReset)
		self.rebootButton.Bind(wx.EVT_BUTTON, self.reboot)
		self.shutdownButton.Bind(wx.EVT_BUTTON, self.shutdown)

		experimentStatusText 	= wx.StaticText(self.p1, label = "Experiment Status", 	pos = (5, sT - dT))
		textAlive		= wx.StaticText(self.p1, label = "Ping Answer:",	pos = (x2, (sT + dT*0)))
		textLoad		= wx.StaticText(self.p1, label = "CPU load:", 		pos = (x2, (sT + dT*1)))
		textTempFPGA		= wx.StaticText(self.p1, label = "Temp. FPGA:",  	pos = (x2, (sT + dT*2)))
		textTempADC		= wx.StaticText(self.p1, label = "Temp. ADC:", 		pos = (x2, (sT + dT*3)))
		textTempETH		= wx.StaticText(self.p1, label = "Temp. ETH:",  	pos = (x2, (sT + dT*4)))
		textTempPCB		= wx.StaticText(self.p1, label = "Temp. PCB:",   	pos = (x2, (sT + dT*5)))
		textTempIN 		= wx.StaticText(self.p1, label = "Temp. Inside:", 	pos = (x2, (sT + dT*6)))
		textTempOUT		= wx.StaticText(self.p1, label = "Temp. Outside:", 	pos = (x2, (sT + dT*7)))
		textTime		= wx.StaticText(self.p1, label = "Last Upl. Cmd:", 	pos = (x2, (sT + dT*8)))
		textLastCmd		= wx.StaticText(self.p1, label = "Last TLM:",		pos = (x2, (sT + dT*9)))
		textFrameRate		= wx.StaticText(self.p1, label = "ADS-B FPS:",		pos = (x2, (sT + dT*10)))

		self.showAlive		=  wx.StaticText(self.p1, label = "-", pos = (x3, (sT + dT*0)))
		self.showLoad		=  wx.StaticText(self.p1, label = "-", pos = (x3, (sT + dT*1)))
		self.showTemp = [0,0,0,0,0,0]
		self.showTemp[0]	=  wx.StaticText(self.p1, label = "-", pos = (x3, (sT + dT*2)))
		self.showTemp[1]	=  wx.StaticText(self.p1, label = "-", pos = (x3, (sT + dT*3)))
		self.showTemp[2]	=  wx.StaticText(self.p1, label = "-", pos = (x3, (sT + dT*4)))
		self.showTemp[3]	=  wx.StaticText(self.p1, label = "-", pos = (x3, (sT + dT*5)))
		self.showTemp[4]	=  wx.StaticText(self.p1, label = "-", pos = (x3, (sT + dT*6)))
		self.showTemp[5]	=  wx.StaticText(self.p1, label = "-", pos = (x3, (sT + dT*7)))
		self.showTime		=  wx.StaticText(self.p1, label = "-", pos = (x3, (sT + dT*8)))
		self.showLastCmd	=  wx.StaticText(self.p1, label = "-", pos = (x3, (sT + dT*9)))
		self.showFrameRate	=  wx.StaticText(self.p1, label = "-", pos = (x3, (sT + dT*10)))

		EVT_RESULT(self, self.OnIncomingTLM)
		global worker
		worker[0] = HealthReceiver(self)
		worker[1] = PayloadReceiver(self)
		worker[2] = PlanePlotterSrv(self)


	#
	# Button events
	#
	def getAliveSignal(self, event):
		reply = self.sendUplinkCmd("PI\n")
		if (reply != None):
			self.showAlive.SetLabel("Yes")
		else:
			self.showAlive.SetLabel("No")


	def fpgaReset(self, event):
		dialReset = wx.MessageDialog(None, 'Do you really want to reset the FPGA?', 'Question', wx.YES_NO |
			wx.NO_DEFAULT | wx.ICON_QUESTION)
		answerReset = dialReset.ShowModal()

		if answerReset == wx.ID_YES:
			self.sendUplinkCmd("RF\n")
		else:
			self.statusbar.SetStatusText("FPGA reset denied by user.")


	def closeFiles(self, event):
		self.sendUplinkCmd("SY\n")


	def reboot(self, event):
		dialReboot = wx.MessageDialog(None, 'Do you really want to reboot the ARM computer?', 'Question',
			 wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
		answerReboot = dialReboot.ShowModal()

		if answerReboot == wx.ID_YES:
			self.sendUplinkCmd("RA\n")
		else:
			self.statusbar.SetStatusText("ARM computer reboot denied by user.")


	def shutdown(self, event):
		dialShutdown = wx.MessageDialog(None, 'Do you really want to shutdown the ARM computer?', 'Question',
			 wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
		answerShutdown = dialShutdown.ShowModal()

		if answerShutdown == wx.ID_YES:
			self.sendUplinkCmd("SA\n")
		else:
			self.statusbar.SetStatusText("ARM computer shutdown denied by user.")


	def getCpuLoad(self, event):
		load = self.sendUplinkCmd("GL\n")
		if (load != None):
			self.showLoad.SetLabel(load)
		else:
			self.showLoad.SetLabel("N/A")


	def setTime(self, event):
		load = self.sendUplinkCmd("TU %s\n" % int(time.time()))
		udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	#
	# Uplink TCP command send
	#
	def sendUplinkCmd(self, cmd):
		try:
			tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			tcpSocket.connect((ip_experiment, port_uplink))
			tcpSocket.send(cmd)
			reply = tcpSocket.recv(100)
			self.showTime.SetLabel(time.ctime(time.time()))
		except:
			self.statusbar.SetStatusText("Cmd: " + cmd.split("\n")[0] + " - TCP connection not successful.")
			return None
		finally:
			tcpSocket.close()

		self.statusbar.SetStatusText("Cmd: " + cmd.split("\n")[0] + " - Reply: " + reply.split("\n")[0])
		return reply

	#
	# Telemetry packet return event
	#
	def OnIncomingTLM(self, event):
		global oldTimestampADSB
		global PPcomm
		if event.evType == typeHealth:
			temperatures = event.data
			print "Health data received."
			for i in range(6):
				self.showTemp[i].SetLabel(str(temperatures[i]))
			self.showLastCmd.SetLabel("Health @ " + time.ctime(time.time()))
			return
		if event.evType == typeData:
			print "Payload data received."
			data = event.data
			preamble = data[0].split(",")

			# Read status informations about the data received
			newTimestampADSB = int(preamble[0])
			adsbDataCount = int(preamble[1])

			# TODO use better resolution (ms, us) because packets may arrive in same second
			#adsbPacketsPerSecond = adsbDataCount / (newTimestampADSB - oldTimestampADSB)
			adsbPacketsPerSecond = 5
			oldTimestampADSB = newTimestampADSB
			self.showLastCmd.SetLabel("Data @ " + time.ctime(time.time()))
			self.showFrameRate.SetLabel(str(adsbPacketsPerSecond) + " FPS")

			for i in range(adsbDataCount):
				planeplotterMessage = "*%s;\r\n\0" % data[i + 1]
				if PPcomm != None:
					PPcomm.send(planeplotterMessage)
			return


app = wx.App(redirect = False)
frame = MainWindow(None, "ARCA ground control system v0.3")
frame.Show()
app.MainLoop()

for n in range(3):
	# TODO find terminating function call
	pass
