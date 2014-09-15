import time
import csv

filename = "Health_Data_%s.csv" % int(time.time())
fileObject = open(filename, "w") 

rawHealthData = "%s,45000,46000,34000,0,0,-12000" % (int(time.time()))
#healthData = rawHealthData.split(",")

for i in range(10):
	fileObject.write(rawHealthData + "\n") 

fileObject.close()
