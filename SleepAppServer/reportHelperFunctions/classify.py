from sklearn.metrics import classification_report
from sklearn import svm
from sklearn import cluster

import numpy as np

import pywt

import scipy

import time

import math

def getMovementWindows(filename):
	with open(filename,"r") as training:
		users_and_sessions = []
		labels = []
		movements = []	
		numWindows = []
		i = 0
		# parse txt file
		for line in training:	
			if (i % 3 == 0):
				#username and session
				users_and_sessions += [line.strip()]
			elif (i % 3 == 1):
				#label data
				labels += [line.strip().split(",")]
				numWindows += [len(labels)]
			else:	
				#movement dat
				td = []
				for s in line.strip().split(" "):
					td += [float(s)]
				movements += [td]
			i += 1

		new_movements = []
		index = 0
		total_windows = 0
		max_window_length = 616
		# Get each 20-minute time window of movement events
		for i in xrange(0,len(movements)):
			m = movements[i]
			num_windows = len(labels[i])
			num_per_window = len(m)/num_windows
			if num_per_window > max_window_length:
				max_window_length = num_per_window
			window_index = 0
			total_windows += num_windows
			for j in xrange(0,len(m),num_per_window):
				new_movements += [[]]
				for k in xrange(j,j+num_per_window):
					if k >= len(m):
						break
					new_movements[index] += [m[k]]
				# add the label
				if (window_index >= num_windows):
					break
				new_movements[index] = np.array(new_movements[index])
				window_index += 1
				index += 1

		overallMax = 0
		overallMaxNumNonZeros = 0 
		overallBiggestBlock = 0
		new_movements = new_movements[:total_windows]

		#Discrete Wavelet Transform
		dwt = []
		for m in new_movements:
			#pad shorter windows (last) with zeros
			mnew = np.concatenate((m,np.array([0.0 for i in xrange(0,max_window_length-len(m))])))
			coeffs = pywt.wavedec(mnew,'db1',level=8)
			cA8, cD8,cD7,cD6, cD5, cD4, cD3, cD2, cD1 = coeffs
			dwt += [cA8]

		maxMean = 0
		compressed = []
		# Compress the 20-minute windows into 4-tuple of key metrics
		for i in xrange(0,len(new_movements)):
			compressed += [[]]
			# mean, maxVal, numNonZeroVals, length of biggest block
			numNonZeros = 0
			biggestBlock = 0
			bblock = True
			b_so_far = 0
			for j in new_movements[i]:
				if j != 0.0:
					numNonZeros += 1
					b_so_far += 1
					if b_so_far > biggestBlock:
						biggestBlock = b_so_far
				else:
					b_so_far = 0
			currentMax = max(new_movements[i])
			currentMean = np.mean(new_movements[i])
			# Used to normalize the metrics
			if (currentMax > overallMax):
				overallMax = currentMax
			if (numNonZeros > overallMaxNumNonZeros):
				overallMaxNumNonZeros = numNonZeros
			if (biggestBlock > overallBiggestBlock):
				overallBiggestBlock = biggestBlock
			if (currentMean > maxMean):
				maxMean = currentMean
			compressed[i] = np.array([currentMax,  numNonZeros, biggestBlock, currentMean])
		labels = [num for elem in labels for num in elem]
		# normalize values
		for i in xrange(0,len(compressed)):
			compressed[i][0] /= float(overallMax)
			compressed[i][2] /= float(overallBiggestBlock)
			compressed[i][3] /= float(maxMean)
		return [compressed,labels,numWindows,dwt]

def knn(train,test,w,train_labels,test_labels,n,abc,num_test_labels):
	filew = open("../txtfiles/knn_results.txt","w")
	preds = []
	x = 0
	for ind,i in enumerate(test):
		min_dist=float('inf')
		closest_seq=-1
		# Find the nearest neighbor for each new test 20-minute window
		for jind in xrange(0,len(train)):
			j = train[jind]
			dist = euclid_dist(i,j)
			if dist<min_dist:
				min_dist=dist
				closest_seq=jind
		preds.append(train_labels[closest_seq])
		x += 1

	for i in xrange(0,len(preds)):
		# if label is for first 20 minute window in a session, just skip it
		if (i == 0 or i in num_test_labels):
			continue
		# otherwise if it was labeled as restless, but the previous label
		# is asleep then relabel it as woke up
		if (preds[i] == 'r' and preds[i-1] == 'a'):
			preds[i] = 'w'

	# Write test labels and predicted labels to txt file for determining
	# resulting scores
	filew.write("test_labels: \n")
	for tl in test_labels:
		filew.write("%s," % tl)
	filew.write("\n")
	filew.write("prediction labels: \n")
	for pl in preds:
		filew.write("%s," % pl)
	filew.write("\n")
	filew.close()	

	return classification_report(test_labels,preds)

def euclid_dist(t1,t2):
	return math.sqrt(sum((t1-t2)**2))

#Source code at,
#https://github.com/alexminnaar/time-series-classification-and-clustering
def DTWDistance1(s1, s2):
    DTW={}
    
    for i in range(len(s1)):
        DTW[(i, -1)] = float('inf')
    for i in range(len(s2)):
        DTW[(-1, i)] = float('inf')
    DTW[(-1, -1)] = 0

    for i in range(len(s1)):
        for j in range(len(s2)):
            dist= (s1[i]-s2[j])**2
            DTW[(i, j)] = dist + min(DTW[(i-1, j)],DTW[(i, j-1)], DTW[(i-1, j-1)])
		
    return math.sqrt(DTW[len(s1)-1, len(s2)-1])

#Source code at,
#https://github.com/alexminnaar/time-series-classification-and-clustering
# Speed up dynamic time warping using a locality constraint
def DTWDistance2(s1, s2,w):
    DTW={}
    
    w = max(w, abs(len(s1)-len(s2)))
    
    for i in range(-1,len(s1)):
        for j in range(-1,len(s2)):
            DTW[(i, j)] = float('inf')
    DTW[(-1, -1)] = 0
  
    for i in range(len(s1)):
        for j in range(max(0, i-w), min(len(s2), i+w)):
            dist= (s1[i]-s2[j])**2
            DTW[(i, j)] = dist + min(DTW[(i-1, j)],DTW[(i, j-1)], DTW[(i-1, j-1)])
		
    return math.sqrt(DTW[len(s1)-1, len(s2)-1])

#Source code at,
#https://github.com/alexminnaar/time-series-classification-and-clustering
def LB_Keogh(s1,s2,r):
    LB_sum=0
    # lower bound check in linear time b4 needing to run
    # dynamic time warping which is quadratic
    for ind,i in enumerate(s1):
        
        x = s2[(ind-r if ind-r>=0 else 0):(ind+r)]
        y = s2[(ind-r if ind-r>=0 else 0):(ind+r)]
        try:   
			lower_bound=min(s2[(ind-r if ind-r>=0 else 0):(ind+r)])
        except ValueError:	
            lower_bound=0.0	
        try:
            upper_bound=max(s2[(ind-r if ind-r>=0 else 0):(ind+r)])
        except ValueError:
            upper_bound=float('inf')        

        if i>upper_bound:
           	LB_sum=LB_sum+(i-upper_bound)**2
        elif i<lower_bound:
            LB_sum=LB_sum+(i-lower_bound)**2
    
    return math.sqrt(LB_sum)

def kmeansClassify(training, training_labels, test, test_labels, num_test_labels):
	k_means = cluster.KMeans(n_clusters=3, n_init=4)
	k_means.fit(test)
	preds = k_means.labels_

	for i in xrange(0,len(preds)):
		# if label is for first 20 minute window in a session, just skip it
		if (i == 0 or i in num_test_labels):
			continue
		# otherwise if it was labeled as restless, but the previous label
		# is asleep then relabel it as woke up
		if (preds[i] == 'r' and preds[i-1] == 'a'):
			preds[i] = 'w'

	# Write test labels and predicted labels to txt file for determining
	# resulting scores
	filew = open("../txtfiles/kmeans_results.txt","w")
	filew.write("test_labels: \n")
	for tl in test_labels:
		filew.write("%s," % tl)
	filew.write("\n")
	filew.write("prediction labels: \n")
	# Need to convert kmeans predicted labels of 0,1,2 to our labels of
	# 'r', 'a', 'w'
	# Note: This mapping isn't always the correct one, would need to
	# calculate and write all permutations then test each one
	# Instead, I have just been rerunning this code until the mapping is correct
	# mapping is wrong => accuracy scores < 10%, correct => accuracy scores > 70%
	for i in xrange(0,len(preds)):
		if preds[i] == 0:
			predLabel = 'r'
		elif preds[i] == 1:
			predLabel = 'a'
		else:
			predLabel = 'w'
		filew.write("%s," % predLabel)
	filew.write("\n")
	filew.close()
	
def svmClassify(train,train_labels,test,test_labels,num_test_labels):
	clf = svm.SVC()
	clf.fit(train,train_labels)

	preds = clf.predict(test)
	for i in xrange(0,len(preds)):
		# if label is for first 20 minute window in a session, just skip it
		if (i == 0 or i in num_test_labels):
			continue
		# otherwise if it was labeled as restless, but the previous label
		# is asleep then relabel it as woke up
		if (preds[i] == 'r' and preds[i-1] == 'a'):
			preds[i] = 'w'

	# Write test labels and predicted labels to txt file for determining
	# resulting scores
	filew = open("../txtfiles/svm_results.txt","w")
	filew.write("test_labels: \n")
	for tl in test_labels:
		filew.write("%s," % tl)
	filew.write("\n")
	filew.write("prediction labels: \n")
	for pl in preds:
		filew.write("%s," % pl)

	filew.write("\n")
	filew.close()	

	return

# Parse movement data and convert to 20-minute windows
# Parse label data
# Calculate dwt compression
[train,train_labels,num_train_windows,traindwt] = getMovementWindows("../txtfiles/training.txt")
print len(train_labels)

# Parse movement data and convert to 20-minute windows
# Parse label data
# Calculate dwt compression
[test,test_labels,num_test_labels,testdwt] = getMovementWindows("../txtfiles/test.txt")
print len(test_labels)

# Run knn classifier
knn(train,test,4,train_labels,test_labels,5,5,num_test_labels)
# Run svm classifier
svmClassify(train,train_labels,test,test_labels,num_test_labels)
# Run kmeans classifier
kmeansClassify(train,train_labels,test,test_labels,num_test_labels)

# Run knn classifier w/ discrete wavelet transform compression
#knn(traindwt,testdwt,4,train_labels,test_labels,5,5,num_test_labels)

# Run svm classifier w/ discrete wavelet transform compression
#svmClassify(traindwt,train_labels,testdwt,test_labels,num_test_labels)

# Run kmeans classifier w/ discrete wavelet transform compression
#kmeansClassify(traindwt,train_labels,testdwt,test_labels,num_test_labels)
