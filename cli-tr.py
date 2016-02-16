__author__ = 'Daniel'


import socket
import cv2
import numpy 
import CMT
import numpy as np
import util
import time
import threading 
import SimpleCV
from SimpleCV import *
import sys
import time
import msvcrt

from LegoCarSerial import LegoCarSerial

from threading import Thread
#from LegoCarSerial import LegoCarSerial
flag=0
flag2=1
turn=1
turn2=2
initail=1
postion=0
all=1
tur_c=0
tur_c2=0
X=0
Y=0
L=LegoCarSerial("COM5",9600)
L.openSerial()
	
def func1():
	global X
	global Y
	#TCP_IP = '54.68.17.227'
	TCP_IP = 'localhost'
	TCP_PORT = 80


	sock = socket.socket()
	sock.connect((TCP_IP, TCP_PORT))
	capture = cv2.VideoCapture(0)
	i=0
	stop_counter=0

	if not capture.isOpened():
		print 'Unable to open video input.'
		sys.exit(1)
	status, img = capture.read()
	gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
	ret,img = cv2.threshold(gray,235,255,0)
	#cv2.imshow('Preview', im)	
#	img = cv2.imread(im)


	kernel = np.ones((30,30),np.float32)/900
	dst = cv2.filter2D(img,-1,kernel)


	normaldisplay = False

	img1=Image(dst)
	#img = img1.flipVertical()
	dist = img1.colorDistance(SimpleCV.Color.BLACK).dilate(2)
	segmented = dist.stretch(180,255)
	blobs = segmented.findBlobs()


	i=0
	for b in blobs:
		i=i+1
		crop_img=img1[b.minX():b.maxX(),b.minY():b.maxY()]
		hist=crop_img.histogram(10)
		if(hist[0]<1000):
			(Y,X)=b.centroid()
			print "XX={x} ,YY={y}".format(x=X, y=Y)
			break
		
	
	k = cv2.waitKey(10)
	preview = True
	while preview:
		status, im = capture.read()
		cv2.imshow('Preview', im)
		k = cv2.waitKey(10)
		if not k == -1:
			break
	cv2.destroyAllWindows()		
	# Read first frame
	status, im0 = capture.read()
	im_gray0 = cv2.cvtColor(im0, cv2.COLOR_BGR2GRAY)
	im_draw = np.copy(im0)
			
	(tl, br) = util.get_rect(im_draw)

	print 'using', tl, br, 'as init bb'		
			
	stringData= str(tl)
	sock.sendall( (stringData))
	str2 = sock.recv(10) 
	stringData= str(br)
	sock.sendall( (stringData))
	str2 = sock.recv(10) 

	import time
	#time.sleep(1)
	number_of_throw_frames=10
	i=0
	y=1
	while True:
		i+=1
		print i
		str2=""
		stringData=""
		global flag
		global flag2
		ret, frame = capture.read()
	#	frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),100]
		result, imgencode = cv2.imencode('.jpg', frame, encode_param)
		data = numpy.array(imgencode)
		stringData = data.tostring()
		sock.sendall( str((len(stringData))))
		str2 = sock.recv(10) 
	#	print str2
	#	time.sleep(0.1)
		sock.sendall( stringData )
	#	time.sleep(0.1)
		str2 = sock.recv(1024)
		values = str2.split(',')
		flag=1
		if values[0]=='nan' or values[1]=='nan':
			stop_counter=stop_counter+1;
			print "Counter={x}".format(x=stop_counter)
			if(stop_counter > 20):
				L.sendData('S')
				sys.exit("Car Lost")
			continue;
		else:
			stop_counter=0;
			if(flag2):
				func2(values)
			
	
		
		
	#	print str2
	#	i+=1
	

	sock.close()
	cv2.destroyAllWindows()

def func2(values):
	global flag
	global flag2
	global all
	global initail
	global postion
	global tur_c
	global tur_c2



	if(flag):
		flag2=0
		L.sendData('S')

		values=values
		if values[0]=='nan' or values[1]=='nan': 
				print 'Car lost'
				L.sendData('S')
				raise Exception('Lost Car')
		else:		
			time.sleep(0.3);
			x= int(float(values[0]))
			y= int(float(values[1]))
		if (initail):
	
			initail=0
			if(x>X) and (y<Y):
				postion=1 
			if(x<X) and (y<Y):
				postion=2 
			if(x>X) and (y>Y):
				postion=3 
			if(x<X) and (y>Y):
				postion=4				

		else:
			if postion == 1:
				flag=0
				print("postion == 1\n");
				Xy(values,X,Y);
				flag=1
			# elif postion == 2:
				# flag=0
				# print("postion == 2\n");
				# #xY(values,X,Y);
				# flag=1
			elif postion == 3:
				flag=0
				print("postion == 3\n");
				XY(values,X,Y);
				flag=1
			# elif postion == 4:
				# print("postion == 4");
		#print "X={x} ,Y={y}".format(x=x, y=y)

		flag2=1
		
	
	
			

#L=LegoCarSerial("COM5",9600)
#L.openSerial()	

def XY(values,X,Y):
	print ('XY')
	global turn;
	global turn2;
	global tur_c;
	print "x={x} ,y={y}".format(x=values[0], y=values[1])
	if values[0]=='nan' or values[1]=='nan': 
			print 'Car lost'
			L.sendData('S')
			raise Exception('Lost Car')
	else:		
		x= int(float(values[0]))
		y= int(float(values[1]))
	if(x>(X+70)):
		print ('1')
		L.sendData('G')
		time.sleep(0.1)
		L.sendData('L')
		time.sleep(0.01)
		L.sendData('S')
	elif (x<(X+70)) and (turn) and (tur_c<4) :
		if(tur_c==3):
			turn=0
		print 'turn1'
		tur_c=tur_c+1
		L.sendData('R')
		time.sleep(0.08)
		L.sendData('S')
		L.sendData('R')
		time.sleep(0.07)
		L.sendData('S')
		turn2=1;
	
	elif (y>(Y+10)) and (turn==0) and (turn2==1):
		
		print 'turn2'
		L.sendData('G')
		time.sleep(0.1)
		L.sendData('L')
		time.sleep(0.01)
		L.sendData('S')

	else:
		sys.exit("Car Parked Success")
		L.sendData('S')	
		
def Xy(values,X,Y):
	print ('XY')
	global turn;
	global turn2;
	global tur_c;
	print "x={x} ,y={y}".format(x=values[0], y=values[1])
	if values[0]=='nan' or values[1]=='nan': 
			print 'Car lost'
			L.sendData('S')
			raise Exception('Lost Car')
	else:		
		x= int(float(values[0]))
		y= int(float(values[1]))
	if(x>(X+50)):
		print ('1')
		L.sendData('G')
		time.sleep(0.1)
		L.sendData('L')
		time.sleep(0.01)
		L.sendData('S')
	elif (x<(X+50)) and (turn) and (tur_c<4) :
		if(tur_c==3):
			turn=0
		print 'turn1'
		tur_c=tur_c+1
		L.sendData('L')
		time.sleep(0.09)
		L.sendData('S')
		L.sendData('L')
		time.sleep(0.09)
		L.sendData('S')
		turn2=1;
	
	elif (y<(Y+00)) and (turn==0) and (turn2==1):
		
		print 'turn2'
		L.sendData('G')
		time.sleep(0.1)
		L.sendData('L')
		time.sleep(0.01)
		L.sendData('S')

	else:
		sys.exit("Car Parked Success")
		L.sendData('S')			
		
def xY(values,X,Y):
	print ('xY')
	global turn;
	global turn2;
	global tur_c;
	print "X={x} ,Y={y}".format(x=values[0], y=values[1])
	if values[0]=='nan' or values[1]=='nan': 
			print 'Car lost'
			L.sendData('S')
			raise Exception('Lost Car')
	else:		
		x= int(float(values[0]))
		y= int(float(values[1]))
	if(x<X):
		print ('1')
		L.sendData('G')
		time.sleep(0.1)
		L.sendData('L')
		time.sleep(0.01)
		L.sendData('S')
	elif (x>X) and (turn) and (tur_c<4) :
		if(tur_c==3):
			turn=0
		print 'turn1'
		tur_c=tur_c+1
		L.sendData('R')
		time.sleep(0.18)
		L.sendData('S')
		turn2=1;
	
	elif (y<Y) and (turn==0) and (turn2==1):
		
		print 'turn2'
		L.sendData('G')
		time.sleep(0.1)
		L.sendData('L')
		time.sleep(0.01)
		L.sendData('S')

	else:
		sys.exit("Car Parked Success")
		L.sendData('S')	
		
		
		
#def align(values,X,Y):	
	print ('align')
	global all
	global tur_c2
	
	print "X={x} ,Y={y}".format(x=values[0], y=values[1])
	if values[0]=='nan' or values[1]=='nan': 
			print 'Car lost'
			L.sendData('S')
			raise Exception('Lost Car')
	else:		
		x= int(float(values[0]))
		y= int(float(values[1]))
	if (x>X):
		if(y<Y):
			L.sendData('G')
			time.sleep(0.1)
			L.sendData('L')
			time.sleep(0.01)
			L.sendData('S')
		elif (tur_c2<9):
			tur_c2=tur_c2+1
			print('tt')
			L.sendData('R')
			time.sleep(0.08)
			L.sendData('S')
			if(tur_c2==8):
				all=0
	
	else:
		if(y<Y):
			L.sendData('G')
			time.sleep(0.1)
			L.sendData('L')
			time.sleep(0.01)
			L.sendData('S')
			print('okk%%')
		elif (tur_c2<9):
			tur_c2=tur_c2+1
			print('tt')
			L.sendData('L')
			time.sleep(0.1)
			L.sendData('S')
			if(tur_c2==8):
				all=0
			print('okk')
		L.sendData('S')
		
		
if __name__ == '__main__':
	Thread(target=func1).start()
	Thread(target=func2([100,100])).start()	