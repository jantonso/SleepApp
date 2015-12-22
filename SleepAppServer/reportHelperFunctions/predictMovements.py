import urllib2
import json
import numpy
import matplotlib.pyplot as plt
import datetime
import math

def predictMovements(user_name, session_number, z_min, z_max, y_min, y_max, x_min, x_max, labels=[]):

	result = urllib2.urlopen("http://totemic-tower-91423.appspot.com/getsessiondata/?user_name=" + user_name + "&session_number=" + session_number).read()

	data = json.loads(result)
	x_acc = data['x_acc']
	y_acc = data['y_acc']
	z_acc = data['z_acc']
	times = data['time_data']
	print times[0]
	print times[len(times)-1]
	x_d = numpy.diff(x_acc)
	y_d = numpy.diff(y_acc)
	z_d = numpy.diff(z_acc)

	numSeconds = int(math.ceil((times[len(times)-1] - times[0])/float(1000)))
	windowSize = 2*(len(x_d) / numSeconds)

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

	# Normalize the movement weights and remove non significant movements, i.e. < 0.20
	max_movements = max(window_movements)
	for k in xrange(0,len(window_movements)):
		window_movements[k] = window_movements[k] / max_movements
		if window_movements[k] <= 0.20:
			window_movements[k] = 0.0

	# cluster together pairs of movement events if they are within a 10 second interval, taking max movement in that period
	for i in xrange(0,len(window_movements),windowSize*5):
		max_movement_so_far = 0.0
		indices = []
		for j in xrange(i,i+10):
			if j >= len(window_movements):
				break
			if window_movements[j] != 0.0:
				indices += [j]
			if window_movements[j] > max_movement_so_far:
				max_movement_so_far = window_movements[j]
		if len(indices) > 1:
			for k in xrange(min(indices),max(indices)+1):
				window_movements[k] = max_movement_so_far

	# save the window_movements to a file
	filew = open("movements_plus_labels.txt","a")
	filew.write(user_name + ":" + session_number)
	filew.write("\n")
	for wm in window_movements:
		filew.write("%f " % wm)
	filew.write("\n")
	filew.close()	
	
	
	# Creates a figure which displays movement weights for each 2 second window as bar chart
	print ("num windows = %d" % (int(math.ceil(len(window_movements)/float(600)))))	
	indices = [i*0.10 for i in xrange(0,len(window_movements),600)]
	index = numpy.arange(len(window_movements))*0.10
	bar_width = 0.10
	fig = plt.figure()
	ax = fig.add_subplot(111)
	fig.subplots_adjust(top=0.85)
	rects1 = ax.bar(index, window_movements, bar_width, color='y')
	ax.set_xlabel('20-minute time bins')
	ax.set_ylabel('Movement Level (normalized)')
	plt.title("Movement levels w/ respect to time for session %s" % session_number)
	plt.xticks(indices, [i for i in xrange(0,len(indices))])

	# Uncomment the following to add labels to the graph
	#for i in xrange(0,len(labels)):	
	#	if labels[i] == 'r':
	#		c = 'red'
	#	elif labels[i] == 'w':
	#		c = 'blue'
	#	else:
	#		c = 'green'
	#	if (i == len(labels) - 1):
	#		ax.text(i*64+25-3,0.95,labels[i],fontsize=13,color=c)
	#	else:
	#		ax.text(i*64+25,0.95, labels[i],fontsize=13,color=c)

	plt.savefig('sessions/%s/movements%s.png' % (user_name,session_number))
	plt.show()

# Me
user_name = '96e2404550ebf3cc'
z_min = -0.10
z_max = 0.10
y_min = -0.10
y_max = 0.10
x_min = -0.10
x_max = 0.10
session_numbers = ['1','3','4','5','6','8','28','36','39','40','52','53','54','55']

# Misha
#user_name = 'feb439be11e2a840'
#session_numbers = ['1','2','3','8']

# Marc
#user_name= 'ffb9f6271e490fa0'
#session_numbers = ['1','2','3','4','5','6','7']

# Joe
#user_name = 'd3368668ff62af96'
#session_numbers = ['1','2','6']

# Aayush
#user_name = '93a24a2249812075'
#session_numbers = ['3','7','8']

for session_number in session_numbers:
	print session_number
	predictMovements(user_name, session_number, z_min, z_max, y_min, y_max, x_min, x_max)
