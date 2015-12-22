from sklearn.metrics import classification_report

# Dynamic time warping results
with open("../txtfiles/dw_results.txt","r") as training:
	i = 0
	# parse txt file
	for line in training:
		if i == 1:
			tests = line.strip().split(",")
		if i == 3:
			preds = line.strip().split(",")
		i += 1

preds = preds[:len(preds)-1]
tests = tests[:len(tests)-1]

total_right = 0
a_right = 0
a_total = 0
r_right = 0
r_total = 0
w_right = 0
w_total = 0
# Count numbers of each label to determine accuracies
for i in xrange(0,len(preds)):
	if preds[i] == tests[i]:
		total_right += 1
		if preds[i] == 'r':
			r_right += 1
		elif preds[i] == 'w':
			w_right += 1
		elif preds[i] == 'a':
			a_right += 1
	if tests[i] == 'a':
		a_total += 1
	elif tests[i] == 'r':
		r_total += 1
	elif tests[i] == 'w':
		w_total += 1 

print "\n"
print "Classification Results using nearest neighbor & Dynamic Time Warping"
print "\n"
print "total accuracy = %s\n" % (total_right / float(len(preds)))
print "asleep accuracy (a) = %s\n" % (a_right / float(a_total))
print "restless accuracy (r) = %s\n" % (r_right / float(r_total))
print "woke up accuracy (w) = %s\n" % (w_right / float(w_total))

print classification_report(tests,preds)

# kNN results
with open("../txtfiles/knn_results.txt","r") as training:
	i = 0
	# parse txt file
	for line in training:
		if i == 1:
			tests = line.strip().split(",")
		if i == 3:
			preds = line.strip().split(",")
		i += 1

preds = preds[:len(preds)-1]
tests = tests[:len(tests)-1]

total_right = 0
a_right = 0
a_total = 0
r_right = 0
r_total = 0
w_right = 0
w_total = 0
# Count numbers of each label to determine accuracies
for i in xrange(0,len(preds)):
	if preds[i] == tests[i]:
		total_right += 1
		if preds[i] == 'r':
			r_right += 1
		elif preds[i] == 'w':
			w_right += 1
		elif preds[i] == 'a':
			a_right += 1
	if tests[i] == 'a':
		a_total += 1
	elif tests[i] == 'r':
		r_total += 1
	elif tests[i] == 'w':
		w_total += 1 

print "\n"
print "Classification Results using kNN"
print "\n"
print "total accuracy = %s\n" % (total_right / float(len(preds)))
print "asleep accuracy (a) = %s\n" % (a_right / float(a_total))
print "restless accuracy (r) = %s\n" % (r_right / float(r_total))
print "woke up accuracy (w) = %s\n" % (w_right / float(w_total))

print classification_report(tests,preds)

# svm results
with open("../txtfiles/svm_results.txt","r") as training:
	i = 0
	# parse txt file
	for line in training:
		if i == 1:
			tests = line.strip().split(",")
		if i == 3:
			preds = line.strip().split(",")
		i += 1

preds = preds[:len(preds)-1]
tests = tests[:len(tests)-1]

total_right = 0
a_right = 0
a_total = 0
r_right = 0
r_total = 0
w_right = 0
w_total = 0
# Count numbers of each label to determine accuracies
for i in xrange(0,len(preds)):
	if preds[i] == tests[i]:
		total_right += 1
		if preds[i] == 'r':
			r_right += 1
		elif preds[i] == 'w':
			w_right += 1
		elif preds[i] == 'a':
			a_right += 1
	if tests[i] == 'a':
		a_total += 1
	elif tests[i] == 'r':
		r_total += 1
	elif tests[i] == 'w':
		w_total += 1
		print preds[i], tests[i] 


print "\n"
print "Classification Results using svm classifier"
print "\n"
print "total accuracy = %s\n" % (total_right / float(len(preds)))
print "asleep accuracy (a) = %s\n" % (a_right / float(a_total))
print "restless accuracy (r) = %s\n" % (r_right / float(r_total))
print "woke up accuracy (w) = %s\n" % (w_right / float(w_total))

print classification_report(tests,preds)

# kmeans results
with open("../txtfiles/kmeans_results.txt","r") as training:
	i = 0
	# parse txt file
	for line in training:
		if i == 1:
			tests = line.strip().split(",")
		if i == 3:
			preds = line.strip().split(",")
		i += 1

preds = preds[:len(preds)-1]
tests = tests[:len(tests)-1]

total_right = 0
a_right = 0
a_total = 0
r_right = 0
r_total = 0
w_right = 0
w_total = 0
# Count numbers of each label to determine accuracies
for i in xrange(0,len(preds)):
	if preds[i] == tests[i]:
		total_right += 1
		if preds[i] == 'r':
			r_right += 1
		elif preds[i] == 'w':
			w_right += 1
		elif preds[i] == 'a':
			a_right += 1
	if tests[i] == 'a':
		a_total += 1
	elif tests[i] == 'r':
		r_total += 1
	elif tests[i] == 'w':
		w_total += 1 

print "\n"
print "Classification Results using kmeans clustering w/ k = 3"
print "\n"
print "total accuracy = %s\n" % (total_right / float(len(preds)))
print "asleep accuracy (a) = %s\n" % (a_right / float(a_total))
print "restless accuracy (r) = %s\n" % (r_right / float(r_total))
print "woke up accuracy (w) = %s\n" % (w_right / float(w_total))

print classification_report(tests,preds)
