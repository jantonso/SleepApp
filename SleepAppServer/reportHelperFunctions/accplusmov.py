import numpy
import urllib2
import json
import matplotlib.pyplot as pl
import math

user_name = '96e2404550ebf3cc'
session = '51'

result = urllib2.urlopen("http://totemic-tower-91423.appspot.com/getsessiondata/?user_name=" + user_name + "&session_number=" + session).read()

# get all the acc data for the given user and session number
data = json.loads(result)
x_acc = data['x_acc']
y_acc = data['y_acc']
z_acc = data['z_acc']
time = data['time_data']

numSeconds = int(math.ceil((time[len(time)-1] - time[0])/float(1000)))
print numSeconds

xaccd = numpy.diff(x_acc)
yaccd = numpy.diff(y_acc)
zaccd = numpy.diff(z_acc)

x_d = xaccd
y_d = yaccd
z_d = yaccd

# We want windows of 2 seconds
windowSize = 2*(len(xaccd) / numSeconds) 

# Threshold values
x_min = -0.10
y_min = -0.10
z_min = -0.10
x_max = 0.10
y_max = 0.10
z_max = 0.10

window_movements = [0.0 for i in xrange(0,len(x_d),windowSize)]
current_index = 0
for i in xrange(0,len(x_d),windowSize):
	# For each 2 second window count the number of movement readings
	for j in xrange(i,i+windowSize):
		if j >= (len(x_d)):
			break
		if (x_d[j] < x_min or x_d[j] > x_max):
			window_movements[current_index] += 1.0
		if (y_d[j] < y_min or y_d[j] > y_max):
			window_movements[current_index] += 1.0
		if (z_d[j] < z_min or z_d[j] > z_max):
			window_movements[current_index] += 1.0
	current_index += 1

# Normalize the 2 second widnow weights and remove negligable movements, i.e. < 0.20
max_movements = max(window_movements)
for k in xrange(0,len(window_movements)):
	window_movements[k] = window_movements[k] / max_movements
	if window_movements[k] <= 0.20:
		window_movements[k] = 0.0

print len(window_movements)
print len(xaccd)
acc_length = 220

# Create a figure which is a bar chart of the movement weights for 2 sec windows
fig = pl.figure()
ax = fig.add_subplot(111)
fig.subplots_adjust(top=0.85)
index = numpy.arange(len(window_movements))*windowSize
bar_width = windowSize
rects1 = ax.bar(index, window_movements,bar_width,color='g')
ax.set_xlabel('time index')
ax.set_ylabel('Movement Level (normalized)')
ax.set_xlim([0,acc_length])
pl.title("Movement levels w/ respect to time for session %s" % session)
pl.show()
fig.savefig("sessions/%s/shortmovements%s.png" % (user_name,session))

# Create a figure which shows x,y,z acc derivatives for the session
fig3 = pl.figure()
pl.subplot(3,1,1)
pl.title("x acc derivative w/ respect to time for session %s" % session)
pl.plot([i for i in xrange(0,acc_length)],xaccd[0:acc_length])
pl.ylabel("x acc derivative")
pl.xlabel("time index")

pl.subplot(3,1,2)
pl.title("y acc derivative w/ respect to time for session %s" % session)
pl.plot([i for i in xrange(0,acc_length)],yaccd[0:acc_length])
pl.xlabel("time index")
pl.ylabel("y acc derivative")

pl.subplot(3,1,3)
pl.title("z acc derivative w/ respect to time for session %s" % session)
pl.plot([i for i in xrange(0,acc_length)],zaccd[0:acc_length])
pl.xlabel("time index")
pl.ylabel("z acc derivative")

pl.subplots_adjust(hspace=0.8)

pl.show()
fig3.savefig("sessions/%s/accovertime%s.png" % (user_name,session))

# Create a figure w/ both movement levels and x,y,z acc derivatives
fig4 = pl.figure()
ax = fig4.add_subplot(111)
pl.xlabel('time index')
ax.set_ylabel('Movement level (normalized)')
pl.xlim([0,acc_length])
pl.title("Movement levels and acc derivative data w/ respect to time for session %s" % session)
ax2 = ax.twinx()
ax2.plot([i for i in xrange(0,acc_length)],[abs(xaccd[i]) for i in xrange(0,acc_length)], color='r', label='x acc derivative')
ax2.plot([i for i in xrange(0,acc_length)],[abs(yaccd[i]) for i in xrange(0,acc_length)], color='b', label='y acc derivative')
ax2.plot([i for i in xrange(0,acc_length)],[abs(zaccd[i]) for i in xrange(0,acc_length)], color='k', label='z acc derivative')
ax2.set_ylabel('acc derivative (absolute)')
rects1 = ax.bar(index, window_movements,bar_width,color='g')
ax.set_xlim([0,acc_length])
pl.subplots_adjust(hspace=0.8)

pl.legend()

pl.show()
fig4.savefig("sessions/%s/combined%s.png" % (user_name,session))
