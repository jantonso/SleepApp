import matplotlib.pyplot as plt

labels = []
with open("../txtfiles/training.txt","r") as training:
	i = 0
	# parse txt file
	for line in training:
		if (i % 3 == 0):
			#username and session
			new_line = line.strip()
			user_name = new_line.split(":")[0]
			add = False
			if user_name == "96e2404550ebf3cc":
				add = True
		elif (i % 3 == 1):
			#label data
			if add:
				labels += [line.strip().split(",")]
		i += 1

with open("../txtfiles/test.txt","r") as training:
    i = 0
    # parse txt file
    for line in training:
        if (i % 3 == 0):
            #username and session
            new_line = line.strip()
            user_name = new_line.split(":")[0]
            add = False
            if user_name == "96e2404550ebf3cc":
                add = True
        elif (i % 3 == 1):
            #label data
            if add:
                labels += [line.strip().split(",")]
        i += 1

print labels

maxLength = 0
for l in labels:
	if len(l) > maxLength:
		maxLength = len(l)

totalScore = [0.0 for i in xrange(0,maxLength)]
numPoints = [0.0 for i in xrange(0,maxLength)]
for l in labels:
	for i in xrange(0,len(l)):
		if l[i] == "w":
			totalScore[i] += 4.0
		elif l[i] == "r":
			totalScore[i] += 0.5
		elif l[i] == "a":
			totalScore[i] += 0.0
		else:	
			print l[i]
		numPoints[i] += 1

for i in xrange(0,maxLength):
	totalScore[i] /= numPoints[i]

plt.plot([i for i in xrange(0,maxLength)],totalScore, linewidth=3.0)
plt.title('Predicted sleep/wake pattern')
plt.xlabel('20-minute window index')
plt.ylabel('Movement weight')
plt.axis([0,35,0,2.0])
plt.show()	
