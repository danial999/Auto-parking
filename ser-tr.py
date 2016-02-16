__author__ = 'Daniel'

import socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("", 80))
server_socket.listen(1)
import os
import numpy as np
import cv2
import Image

import argparse
import cv2
from numpy import empty, nan
import sys
import time
import CMT
import util

CMT = CMT.CMT()
cap = cv2.VideoCapture(0)


client_socket, address = server_socket.accept()
print "Conencted to - ",address,"\n"


strng=""
i=0
first = 1


tl = client_socket.recv(1024)
tl =tl.replace("(", '')
tl =tl.replace(")", ',')
tl =tl.replace(" ", '')
# this ack can be replaced by sleep at client 	
client_socket.send("a") 
br = client_socket.recv(1024)
br =br.replace("(", '')
br =br.replace(")", '')
br =br.replace(" ", '')
# this ack can be replaced by sleep at client 	
client_socket.send("a") 
while True:
	ack = client_socket.recv(100)
# this ack can be replaced by sleep at client 	
	client_socket.send("a") 
	count=0
	strng=""
	while True:
		str = client_socket.recv(4096)
		strng+=str
		count=len(strng)
#		print "{} -- {} -- {}".format(count,"--ack--",ack)
		if count  == (int(ack)):
#			print "done" 
#			client_socket.send("a")
			break
		if count > int(ack):
			print "Errrrroorrr"
			print "***"
			print count
			print ack
			strng+=str	
			exit()
			
		
		


	a=np.fromstring(strng, dtype='uint8')	
	decimg=cv2.imdecode(a,1)
	
	#cv2.imshow('Decoded image',decimg)
	#cv2.waitKey()
#	cv2.imwrite("file_{}.jpg".format(i),decimg)


#$$$$$$$$$$$$$$$$$4   CMT $$$$$$$$$$$$$$$$$$$$$$$$$$$
	
	# this is if is for the first frame only == initialise	
	if first==1:
	
		#out put can be changed from None to directory to save output data  
#		output = '/home/ubuntu/carsprj/tmp/out33'
		output=None
		#bbox-REC2
		bbox= tl+br
		bbox=  bbox.replace(",", ",")

		#bbox= '403 ,228 ,491, 319'

#		status, im0 = a#cap.read()
		im0=decimg

		im_gray0 = cv2.cvtColor(im0, cv2.COLOR_BGR2GRAY)
		im_draw = np.copy(im0)
		
		values = bbox.split(',')
		try:
			values = [int(v) for v in values]
		except:
			raise Exception('Unable to parse bounding box')
		if len(values) != 4:
			raise Exception('Bounding box must have exactly 4 elements')
		bbox = np.array(values)
	
		# Convert to point representation, adding singleton dimension
		bbox = util.bb2pts2(bbox[None, :])
	
		# Squeeze
		bbox = bbox[0, :]
	
		tl = bbox[:2]

		br = bbox[2:4]
		print br	


		print 'using', tl, br, 'as init bb'


		CMT.initialise(im_gray0, tl, br)
		first=0
		frame = 1
	#here we process each frame and send the output back to client 	
#	while True:
	# Read image
#		status, im = a
	im =decimg
	im_gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
	im_draw = np.copy(im)

	tic = time.time()
	CMT.process_frame(im_gray)
	toc = time.time()

	# Display results

	# Draw updated estimate
	if CMT.has_result:

		cv2.line(im_draw, CMT.tl, CMT.tr, (255, 0, 0), 4)
		cv2.line(im_draw, CMT.tr, CMT.br, (255, 0, 0), 4)
		cv2.line(im_draw, CMT.br, CMT.bl, (255, 0, 0), 4)
		cv2.line(im_draw, CMT.bl, CMT.tl, (255, 0, 0), 4)

	util.draw_keypoints(CMT.tracked_keypoints, im_draw, (255, 255, 255))
	# this is from simplescale
	util.draw_keypoints(CMT.votes[:, :2], im_draw)  # blue
	util.draw_keypoints(CMT.outliers[:, :2], im_draw, (0, 0, 255))

	if output is not None:
		# Original image
#			cv2.imwrite('{0}/input_{1:08d}.png'.format(args.output, frame), im)
		# Output image
		
		if not os.path.exists(output):
			os.makedirs(output)
		cv2.imwrite('{0}/output_{1:08d}.png'.format(output, frame), im_draw)

		# Keypoints
		with open('{0}/keypoints_{1:08d}.csv'.format(output, frame), 'w+') as f:
			f.write('x y\n')
			np.savetxt(f, CMT.tracked_keypoints[:, :2], fmt='%.2f')

		# Outlier
		with open('{0}/outliers_{1:08d}.csv'.format(output, frame), 'w+') as f:
			f.write('x y\n')
			np.savetxt(f, CMT.outliers, fmt='%.2f')

		# Votes
		with open('{0}/votes_{1:08d}.csv'.format(output, frame), 'w+') as f:
			f.write('x y\n')
			np.savetxt(f, CMT.votes, fmt='%.2f')

		# Bounding box
		with open('{0}/bbox_{1:08d}.csv'.format(output, frame), 'w+') as f:
			f.write('x y\n')
			# Duplicate entry tl is not a mistake, as it is used as a drawing instruction
			np.savetxt(f, np.array((CMT.tl, CMT.tr, CMT.br, CMT.bl, CMT.tl)), fmt='%.2f') 


		# Check key input
#				k = cv2.waitKey(pause_time)

#				key = chr(k & 255)
#				if key == 'q':
#					break
#				if key == 'd':
#					import ipdb; ipdb.set_trace()

	# Remember image
	im_prev = im_gray

	# Advance frame number
	frame += 1
	#decimg[CMT.center[0], CMT.center[1]] = 
	#cv2.imshow('Decoded image',decimg)
	#cv2.waitKey()
	#print '{5:04d}: center: {0:.2f},{1:.2f} scale: {2:.2f}, active: {3:03d}, {4:04.0f}ms'.format(CMT.center[0], CMT.center[1], CMT.scale_estimate, CMT.active_keypoints.shape[0], 1000 * (toc - tic), frame)
	#outfin = '{5:04d}: center: {0:.2f},{1:.2f} scale: {2:.2f}, active: {3:03d}, {4:04.0f}ms'.format(CMT.center[0], CMT.center[1], CMT.scale_estimate, CMT.active_keypoints.shape[0], 1000 * (toc - tic), frame)
	#print "[0]={x} ,[1]={y}".format(x=CMT.center[0], y=CMT.center[1])
	center = '{0:.3f},{1:.3f}'.format(CMT.center[0], CMT.center[1])
	
	client_socket.send(center)


	i+=1
	print i




print "Data Received successfully"
exit()
cap.release()
cv2.destroyAllWindows()
print "Data sent successfully"
exit()


