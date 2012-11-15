import code
import sys

from datetime import datetime

import numpy as np

from PyQt4 import QtCore, QtGui

import cv
import cv2

import warnings
import sequence
import stimulus

movie_width = 1680.
movie_height = 727.
gaze_width = 716.
gaze_height = 368.
gaze_y_offset = 162.
offset = 0

"""
TODO TODO TODO this file has to be cleaned up completely!!! TODO TODO TODO 
"""

def hierarchy_recursion(hierarchy_levels, hierarchy, idx ,act_level):
	if idx < 0:
		return hierarchy_levels
	hierarchy_levels[idx] = act_level
	hierarchy_levels = hierarchy_recursion(hierarchy_levels, hierarchy, hierarchy[0,idx,0] ,act_level)
	hierarchy_levels = hierarchy_recursion(hierarchy_levels, hierarchy, hierarchy[0,idx,2] ,act_level+1)
	return hierarchy_levels

def get_hierarchy_levels(hierarchy):
	if hierarchy is None:
		return np.array([])
	hierarchy_levels = np.zeros(len(hierarchy[0]),dtype=int) - 1
	
	for i in range(len(hierarchy_levels)):
		if hierarchy_levels[i] < 0:
			hierarchy_levels = hierarchy_recursion(hierarchy_levels, hierarchy, i ,0)
	
	return hierarchy_levels

	
def cv2array(im):
	depth2dtype = {
		cv.IPL_DEPTH_8U: 'uint8',
		cv.IPL_DEPTH_8S: 'int8',
		cv.IPL_DEPTH_16U: 'uint16',
		cv.IPL_DEPTH_16S: 'int16',
		cv.IPL_DEPTH_32S: 'int32',
		cv.IPL_DEPTH_32F: 'float32',
		cv.IPL_DEPTH_64F: 'float64',
	}

	arrdtype=im.depth
	a = np.fromstring(
		im.tostring(),
		dtype=depth2dtype[im.depth],
		count=im.width*im.height*im.nChannels)
	a.shape = (im.height,im.width,im.nChannels)
	return a

def array2cv(a):
	dtype2depth = {
		'uint8':   cv.IPL_DEPTH_8U,
		'int8':    cv.IPL_DEPTH_8S,
		'uint16':  cv.IPL_DEPTH_16U,
		'int16':   cv.IPL_DEPTH_16S,
		'int32':   cv.IPL_DEPTH_32S,
		'float32': cv.IPL_DEPTH_32F,
		'float64': cv.IPL_DEPTH_64F,
	}
	try:
		nChannels = a.shape[2]
	except:
		nChannels = 1
	cv_im = cv.CreateImageHeader((a.shape[1],a.shape[0]),dtype2depth[str(a.dtype)], nChannels)
	cv.SetData(cv_im, a.tostring(),a.dtype.itemsize*nChannels*a.shape[1])
	return cv_im



def autumn(n):
	""" Calculating n maximal different rgb-colors and returns them.
	Calculation is done by using the hue value of hsv-pictures. Therefor
	helperfunction valFromHue is used. """
	
	result = []
	for i in range(n):
		hue = int(i*360/n)
		result.append((valFromHue(0,hue),valFromHue(1,hue),valFromHue(2,hue)))
	return result
	
def valFromHue(channel,hue):
	""" Calculating one channel of an rgb signal in relation to the
	hsv-hue value. Channel 0=r,1=g,2=b."""
	
	hue = (hue + (channel)*120 + 120) % 360
	if hue < 60:
		return int(255 * hue /60)
	elif hue < 180:
		return 255
	elif hue < 240:
		return int(-255 * hue /60 + 4*255)
	else:
		return 0

def gauss(x, s):
	return np.exp(-.5*(float(x)/s)**2)

def createGaussMatrix(sigma, cut_relativ):
	dim = sigma * 6 + 1					# outer matrix elements are maximal 0.01
	gauss_vector = np.array(range(dim))
	gauss_vector = np.vectorize(gauss)(gauss_vector-int(dim/2),sigma)
	cut = int(dim/2 * cut_relativ)
	gauss_vector = gauss_vector[cut:dim-cut]
	gauss_matrix = np.multiply(gauss_vector, np.reshape(gauss_vector,(dim-2*cut,1)))
	return gauss_matrix
	
def addArrayAtPosition(heatMap,gaussOverlay,x,y):
	gauss_offset = int(len(gaussOverlay)/2)
	x0 = x-gauss_offset
	x1 = 0
	if x0 < 0:
		x1 = -x0
		x0 = 0
	
	y0 = y-gauss_offset
	y1 = 0
	if y0 < 0:
		y1 = -y0
		y0 = 0
	
	w = len(gaussOverlay) - x1
	if x0 + w > len(heatMap):
		w = len(heatMap) - x0
	
	h = len(gaussOverlay[0]) - y1
	if y0 + h > len(heatMap[0]):
		h = len(heatMap[0]) - y0
	
	#print [x0,x0+w,y0,y0+h, "--" ,x1,w+x1,y1,h+y1]
	heatMap[x0:x0+w,y0:y0+h] += gaussOverlay[x1:w+x1,y1:h+y1]
	
	return heatMap

def thresholds(x,threshold,steps):
	helper = (255-threshold)/steps
	if x < threshold:
		return 0
	
	for i in range(steps):
		if x < threshold + helper*(i+1):
			return threshold + helper*(i)
	else:
		return -1

def time2seconds(h,m,s,ms):
	return h*3600+m*60+s+ms*1./1000
	
def read_seq(filename):
	file = open(filename)
	sequences = []
	while True:
		line = file.readline()
		if line == '':
			break
		line = line[0:len(line)-1]
		
		vec = line.split("\t")
		
		if len(line) <=1:
			pass
		elif len(vec) == 2:
			try:
				sequences.append(sequence.Sequence(float(vec[0]),float(vec[1])))
			except Exception, e:
				warnings.warn('read_seq: Could not read input. Begin and duraration have to be float. FORMAT: begin (in sec) TAB duration (in sec) (TAB label) ')
		elif len(vec) == 3:
			try:
				sequences.append(sequence.Sequence(float(vec[0]),float(vec[1]),vec[2]))
			except Exception, e:
				warnings.warn('read_seq: Could not read input. Begin and duraration have to be float. FORMAT: begin (in sec) TAB duration (in sec) (TAB label) ')
		else:
			warnings.warn('read_seq: Could not read input. FORMAT: begin (in sec) TAB duration (in sec) (TAB label) ')
		
	return sequences
	
def clusterGazes(gaze_coords,k,last_means):
	influence_variance = 1.0 				#std: 1
	influence_k = 0.6									#std: 1
	if len(gaze_coords) < 2*k:
		return [[],100000]
	
	samples = np.array(gaze_coords[:,1:3], np.float32)
	
	temp, classified_points, means = cv2.kmeans(data=np.asarray(samples), 
													K=k, 
													bestLabels=None, 
													criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_MAX_ITER, 0, 15), 
													attempts=1, 
													flags=cv2.KMEANS_RANDOM_CENTERS) 
	
	count_classes = np.zeros(k)
	variance = np.zeros(k)
	
	for i in range(len(classified_points)):
		label_id = classified_points[i]
		count_classes[label_id] += 1
		variance[label_id] += pow(pow(samples[i][0] - float(means[label_id,0]), 2) + 
								  pow(samples[i][1] - float(means[label_id,1]), 2),0.5)
	
	circles = []
	for i in range(len(means)):
		if count_classes[i] > 0:
			circles.append([int(means[i][0]),int(means[i][1]),int(variance[i]/count_classes[i]), count_classes[i]/len(classified_points)])
	
	profit = 0
	for (x,y,var,opa) in circles:
		profit += pow(var,influence_variance)
	
	return [circles, pow(k,influence_k)*profit/len(circles)]
	
def getMeanWithVariance(gaze_coords):
	x_m = 0
	y_m = 0
	for (i, x, y, p) in gaze_coords:
		x_m += x
		y_m += y
	x_m /= len(gaze_coords)
	y_m /= len(gaze_coords)
	
	var = 0
	for (i, x, y, p) in gaze_coords:
		var += pow(pow(x-x_m,2)+pow(y-y_m,2),.5)
	var /= len(gaze_coords)
	
	return (int(x_m), int(y_m), int(var))

def getGazeMovieCoords(gazes, stimulus, nPast, justTakeMean):
	gaze_coords = []
	for gaze_id in range(len(gazes)):
		gaze_frame_id_init = int(stimulus.fps*(-gazes[gaze_id][0][0] + stimulus.act_pos + offset))
		
		mean_coord = np.array([0,0,0])
		for i in range(nPast+1):
			if justTakeMean:
				gaze_frame_id = gaze_frame_id_init-i+int(nPast/2)
			else:
				gaze_frame_id = gaze_frame_id_init-i
			# check if frame_ id exists in array
			if (gaze_frame_id >= 0) and (gaze_frame_id < gazes[gaze_id].shape[0]) and not np.isnan(gazes[gaze_id][gaze_frame_id][3]):
				gaze_x = int(gazes[gaze_id][gaze_frame_id][1] * gaze_width/movie_width)
				gaze_y = int((gazes[gaze_id][gaze_frame_id][2] - gaze_y_offset) * gaze_height/movie_height)
				#gaze_pupil = int(gazes[gaze_id][gaze_frame_id][3])/150
				
				#print [0, gaze_x, gaze_width, "-", 0 ,gaze_y, gaze_height]
				if (gaze_x < 0) or (gaze_x >= gaze_width) or (gaze_y < 0) or (gaze_y >= gaze_height):
					break
				
				if justTakeMean:
					mean_coord += np.array([gaze_x,gaze_y,1])
				else:
					gaze_coords.append(np.array([gaze_id,gaze_x,gaze_y,i+1]))
		if justTakeMean and not mean_coord[2] == 0:
			gaze_coords.append(np.array([gaze_id, int(mean_coord[0]/mean_coord[2]), int(mean_coord[1]/mean_coord[2]), 1]))

	return np.array(gaze_coords)

	
def np2qpixmap(im):
    h, w, channels = im.shape
    im = cv2.cvtColor(im, cv.CV_BGR2BGRA)

    # Qt expects 32bit BGRA data for color images:    
    qimg = QtGui.QImage(im.data, w, h, QtGui.QImage.Format_RGB32)
    qimg.ndarray = im
    
    scene = QtGui.QGraphicsScene()
    scene.addPixmap(QtGui.QPixmap(qimg))
    
    return scene
    
def sec2time(secs):
    int_t = int(secs)
    ms = secs - int_t
    tstr = datetime.fromtimestamp(-3600 + int_t).strftime('%H:%M:%S')
    return tstr + '.%.3i' % (ms * 1000)
    
    #h = int(time/3600)
    #m = int(time%3600)/60
    #s = time%60
    #return '%(h).0f:%(m)2.f:%(s)2.3f' %{'h': h, 'm': m, 's': s}
