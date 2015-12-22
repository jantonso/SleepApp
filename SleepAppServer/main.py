import webapp2

import logging

import numpy

import matplotlib.pyplot as plt

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext import db

import math

import json

import datetime

#from sklearn import svm

# Used to debug through web browser
MAIN_PAGE_FOOTER_TEMPLATE = """<html><body>
    <form action="/" method="post">
    	<input type="hidden" name="user_name" value="slimdog">
    	<input type="hidden" name="time" value="12">
		<input type="hidden" name="sensor_type" value="accelerometer">
		<input type="hidden" name="x_acc" value="[45.0]">
		<input type="hidden" name="y_acc" value="[63.0]">
		<input type="hidden" name="z_acc" value="[3.0]">
		<input type="hidden" name="session_number" value="5">  
		<input type="hidden" name="entry_type" value="sleep_data">
		<input type="submit" value="Sign Guestbook"></div>
    </form>
  </body>
</html>
"""

#clf = svm.SVC()

def sleepdata_key(user_name):
	return ndb.Key('SleepData', user_name or "nouser")

class SleepData(ndb.Model):
	user_name = ndb.StringProperty()
	sensor_type = ndb.StringProperty()
	x_acc = ndb.TextProperty()
	y_acc = ndb.TextProperty()
	z_acc = ndb.TextProperty()
	time = ndb.StringProperty()
	session_number = ndb.IntegerProperty()

# Retrieves the last session number for a given user
class GetSessionNumber(webapp2.RequestHandler):
	def get(self):
		user_name = self.request.get('user_name')
		sleepdata_query = SleepData.query(ancestor=sleepdata_key(user_name)).order(-SleepData.session_number)
		sleepdata = sleepdata_query.fetch(1)
		logging.info("returning response")
		# If there was a previous session, retrieve its number
		if (len(sleepdata) == 1):
			obj = {'session_number': sleepdata[0].session_number}
		# No session exists, so return 0
		else:
			obj = {'session_number': 0}
		json_obj = json.dumps(obj)
		self.response.write(json_obj)		

# Calculates the movement events for each 2 second window for a 
# given user and session number
class GetMovements(webapp2.RequestHandler):
	def get(self):
		
		user_name = self.request.get('user_name')
		try:
			session_number = int(self.request.get('session_number'))
		except ValueError:
			self.response.write('404 Error')
	   		self.response.set_status(404)

	   	# Fetch the acc data (multiple entries) for the given user and session number
		sleepdata_query = SleepData.query(ancestor=sleepdata_key(user_name)).filter(ndb.GenericProperty("session_number") == session_number).order(SleepData.time)
		sleepdata = sleepdata_query.fetch()
		
		all_x_data = []
		all_y_data = []
		all_z_data = []
		time_data = []

		# Threshold values (for each of our six test users, it was the same)
		x_min = -0.10
		x_max = 0.10
		y_min = -0.10
		y_max = 0.10
		z_min = -0.10
		z_max = 0.10
	
		# Loop through all the data (multiple entries) and combine into one array
		# for each x,y,z acc
		for data in sleepdata:		
			x_data = data.x_acc
			y_data = data.y_acc
			z_data = data.z_acc

			x_data = x_data[1:len(x_data)-1]
			y_data = y_data[1:len(y_data)-1]
			z_data = z_data[1:len(z_data)-1]
			
			# data was stored as a string, so need to parse and 
			# convert back to float array
			for x in x_data.split(","):
				all_x_data += [float(x)]
			for y in y_data.split(","):
				all_y_data += [float(y)]
			for z in z_data.split(","):
				all_z_data += [float(z)]

			timed = data.time.split(",")
			for t in timed:
				time_data += [int(t)]

		# Get the x,y,z acc derivatives with respect to time
		x_d = numpy.diff(all_x_data)
		y_d = numpy.diff(all_y_data)
		z_d = numpy.diff(all_z_data)

		# Calculate the size (number of acc datapoints) for each 2 second window
		numSeconds = int(math.ceil((time_data[len(time_data)-1]-time_data[0])/float(1000)))
		windowSize = 2*(len(x_d) / numSeconds)

		window_movements = [0.0 for i in xrange(0,len(x_d),windowSize)]
		current_index = 0
		for i in xrange(0,len(x_d),windowSize):
		# For each 2 second window count the number of movement readings
		# , i.e. abs (x, y, or z derivative value) > abs(threshold)
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

		# normalize the movement weights and remove those that are less than 0.20
		# to remove non-signficant movements
		max_movements = max(window_movements)
		for k in xrange(0,len(window_movements)):
			window_movements[k] = window_movements[k] / max_movements
			if window_movements[k] <= 0.20:
				window_movements[k] = 0.0

		# cluster together pairs of movement events if they are within a 20 second 
		# interval, taking max movement in that period
		new_window_movements = []
		for i in xrange(0,len(window_movements),10):
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

		# Convert 2 second window movement data to json and write back to client,
		# along with the times and number of windows
		obj = {'window_movements': window_movements, 'time_data': time_data, 'number_of_windows': len(time_data)/windowSize}

		json_obj = json.dumps(obj)

		self.response.write(json_obj)

# Retrieves the acc data for a given user and a given session
class GetSessionData(webapp2.RequestHandler):
	def get(self):
		user_name = self.request.get('user_name')
		try:
			session_number = int(self.request.get('session_number'))
		except ValueError:
			session_number = 0

		# Retrieve all the entries for that user and session number
		sleepdata_query = SleepData.query(ancestor=sleepdata_key(user_name)).filter(ndb.GenericProperty("session_number") == session_number).order(SleepData.time)
		sleepdata = sleepdata_query.fetch()
		
		all_x_data = []
		all_y_data = []
		all_z_data = []
		time_data = []
	
		# Loop through all the data (multiple entries) and combine into one array
		# for each x,y,z acc
		for data in sleepdata:		
			x_data = data.x_acc
			y_data = data.y_acc
			z_data = data.z_acc

			x_data = x_data[1:len(x_data)-1]
			y_data = y_data[1:len(y_data)-1]
			z_data = z_data[1:len(z_data)-1]
			
			# data was stored as a string, so need to parse and 
			# convert back to float array
			for x in x_data.split(","):
				all_x_data += [float(x)]
			for y in y_data.split(","):
				all_y_data += [float(y)]
			for z in z_data.split(","):
				all_z_data += [float(z)]

			td = data.time.split(",")
			for t in td:
				time_data += [int(t)]

		# Convert everything to json format and write back to client
		obj = {"x_acc": all_x_data, "y_acc": all_y_data, "z_acc": all_z_data, "time_data": time_data, "session_number": session_number, "user_name": user_name}

		json_obj = json.dumps(obj)
		
		self.response.write(json_obj)

#class TrainSVM(webapp2.RequestHandler):
#	def post(self):
#		train = self.request.get('train')
#		train_labels = self.request.get('train_labels')
#		logging.info("we're trained brah")
#		clf.fit(train,train_labels)
#		self.response.write("Trained up")

class MainPage(webapp2.RequestHandler):
	# Use this page for easy debugging
	def get(self):
		self.response.write(MAIN_PAGE_FOOTER_TEMPLATE)
	# This page is for storing acc data during the user's sleep
	def post(self):
		user_name = self.request.get('user_name')
		entry_type = self.request.get('entry_type')

		if entry_type == 'sleep_data':
			# Create a new sleepdata entry
			new_data = SleepData(parent=sleepdata_key(user_name)) 
			try:
				new_data.sensor_type = self.request.get('sensor_type')
				new_data.x_acc = db.Text(self.request.get('x_acc'))
				new_data.y_acc = db.Text(self.request.get('y_acc'))
				new_data.z_acc = db.Text(self.request.get('z_acc'))
				new_data.time = self.request.get('time')		
				new_data.user_name = user_name
				new_data.session_number = int(self.request.get('session_number'))

				new_data.put()
				self.response.write("Succesfully recorded sensor data")
			except ValueError:	
				logging.info("failed...")

application = webapp2.WSGIApplication([
    ('/', MainPage),
	('/getsessionnumber/',GetSessionNumber),
	('/getsessiondata/',GetSessionData),
	('/getmovements/',GetMovements),
#	('/trainsvm/',TrainSVM),
], debug=True)

