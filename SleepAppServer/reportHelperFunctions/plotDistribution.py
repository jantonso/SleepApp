import urllib2

import scipy.stats as stats

import json

import numpy

import pylab as pl

xacc = []
yacc = []
zacc = []
xaccd = []
yaccd = []
zaccd = []

def getDistribution(user_name, session_number):
    result = urllib2.urlopen("http://totemic-tower-91423.appspot.com/getsessiondata/?user_name=" + user_name + "&session_number=" + session_number).read()
    global xacc
    global yacc
    global zacc
    global xaccd
    global yaccd
    global zaccd

    data = json.loads(result)
    x_acc = data['x_acc']
    y_acc = data['y_acc']
    z_acc = data['z_acc']

    for i in xrange(0,len(x_acc)):
        xacc += [x_acc[i]]
        yacc += [y_acc[i]]
        zacc += [z_acc[i]]

# add/remove user names or session numbers 
user_names = ['ffb9f6271e490fa0']
session_numbers = ['1','2','3']

for i in xrange(0,len(user_names)):
	user_name = user_names[0]
	for session_number in session_numbers:
		print session_number
		getDistribution(user_name, session_number)

# Plot figure with x,y,z acc distributions
fig2 = pl.figure()
fig2.suptitle("x,y,z acc distributions")
pl.subplot(3,1,1)
h1 = sorted(xacc)
fit1 = stats.norm.pdf(h1,numpy.mean(h1),numpy.std(h1))
#pl.plot(h1,fit1,'-o')
pl.hist(h1, bins=1000, normed=True)
pl.title("x_acc")
pl.xlim((-2,2))

pl.subplot(3,1,2)
h2 = sorted(yacc)
fit2 = stats.norm.pdf(h2,numpy.mean(h2),numpy.std(h2))
#pl.plot(h2,fit2,'-o')
pl.hist(h2, bins=1000, normed=True)
pl.title("y_acc")
pl.xlim((-2,2))

pl.subplot(3,1,3)
h3 = sorted(zacc)
fit3 = stats.norm.pdf(h3,numpy.mean(h3),numpy.std(h3))
#pl.plot(h3,fit3,'-o')
pl.hist(h3, bins=1000, normed=True)
pl.title("z_acc")
pl.xlim((-11,11))

pl.subplots_adjust(hspace=0.8)

pl.show()
fig2.savefig("sessions/%s/accdata.png" % user_name)

# Plot figure with only x acc distribution, might need to tune xlim parameters
fig3 = pl.figure()
fig3.suptitle("x acc distribution")
pl.subplot(1,1,1)
h1 = sorted(xacc)
fit1 = stats.norm.pdf(h1,numpy.mean(h1),numpy.std(h1))
pl.plot(h1,fit1,'-o')
pl.hist(h1, bins=1000, normed=True)
pl.xlim((-3,3))
pl.xlabel("x acc")
pl.show()
fig3.savefig("sessions/x.png")

print(numpy.mean(h1))
print(numpy.std(h1))

# Plot figure with only y acc distribution, might need to tune xlim parameters
fig4 = pl.figure()
fig4.suptitle("y acc distribution")
pl.subplot(1,1,1)
pl.plot(h2,fit2,'-o')
pl.hist(h2, bins=1000, normed=True)
pl.xlim((-3,3))
pl.xlabel("y acc")
pl.show()
fig3.savefig("sessions/y.png")
print(numpy.mean(h2))
print(numpy.std(h2))

# Plot figure with only z acc distribution, might need to tune xlim parameters
fig3 = pl.figure()
fig3.suptitle("z acc distribution (zoomed in on l population)")
pl.subplot(1,2,1)
pl.title("left population")
pl.xlabel("z acc")
h3 = sorted(zacc)
new_h3 = []
for h in h3:
	if h > -11 and h < -9:
		new_h3 += [h]
print(numpy.mean(new_h3))
print(numpy.std(new_h3))
fit3 = stats.norm.pdf(new_h3,numpy.mean(new_h3),numpy.std(new_h3))
pl.plot(new_h3,fit3,'-o')
pl.hist(new_h3, bins=100, normed=True)
pl.xlim((-11,-9))

pl.subplot(1,2,2)
pl.title("right population")
new_h4 = []
for h in h3:
	if h > 9 and h < 11:
		new_h4 += [h]
fit4 = stats.norm.pdf(new_h4, numpy.mean(new_h4),numpy.std(new_h4))
pl.plot(new_h4, fit4, '-o')
pl.hist(new_h4,bins=100,normed=True)
pl.xlim((9,11))
pl.xlabel("z acc")

print(numpy.mean(new_h4))
print(numpy.std(new_h4))

pl.show()
fig3.savefig("sessions/z.png") 
