import time 
import sched
import operator

import numpy as np

import cv
import cv2

import stimulus
import sequence
import utils

import user_data

PATH_MOVIE = user_data.PATH_MOVIE # e.g. '/home/movie.m4v' 
PATH_GAZES = user_data.PATH_GAZES # e.g. ['gaze1.npy',gaze2.npy], format: time, x, y, pupil , use indy_utils.py

GAZE_DISP_EACH = 0.1
GAZE_DISP_MEAN = 0
GAZE_DISP_CLUSTERED = 0
GAZE_DISP_HEAT_MAP = 1
GAZE_DISP_HEAT_MAP_GAUSS = 27
GAZE_DISP_HEAT_MAP_THRESHOLD = 120
GAZE_DISP_HEAT_MAP_N_HEAT_LINES = 3

MOVIE_GRAY = True
MOVIE_OPACITY = 0.6

SPEED = 1

def showFrame(s,stimulus,sequence,gazes):
	""" This function shows the frame and all visualizations. It is also responsable for synchronization of stimulus and computer time."""
	
	""" scheduler configuration """
	cpu_time = time.time()
	sequence.frame_count += 1
	act_frame_element = s.enterabs(sequence.time_started+1/stimulus.fps/SPEED*sequence.frame_count, 1, showFrame, (s,stimulus,sequence,gazes))	
	
	""" load image """
	frameImg = stimulus.get_next_frame()
	if frameImg is None:
		return False
	
	""" adjusting stimulus, due to slow computers """
	skipped_frames = stimulus.resync(sequence.begin + (cpu_time - sequence.time_started)*SPEED)
	sequence.skipped_frames += skipped_frames
	
	""" when sequence is over, stop scheduler through deleting next schedule element """
	if not sequence.contains(stimulus.act_time):
		s.cancel(act_frame_element)
	
	""" bgr to gray convertion for using gray stimulus image """
	if MOVIE_GRAY:
		frameImg = cv2.cvtColor(frameImg,cv.CV_BGR2GRAY)
		frameImg = cv2.cvtColor(frameImg,cv.CV_GRAY2BGR)
	showPic = cv2.addWeighted(frameImg, MOVIE_OPACITY, frameImg, 0, 0) 	#TODO: find better implementation
	
	""" go through every option and do calculations """
	# TODO TODO TODO documentation
	if GAZE_DISP_HEAT_MAP > 0:
		gaze_coords = utils.getGazeMovieCoords(gazes, stimulus, 0, False)
		
		heatMap = np.zeros((stimulus.height,stimulus.width),'float32')
		for (i, x, y, prio) in gaze_coords:
			heatMap = utils.addArrayAtPosition(heatMap, gaussOverlay, y, x)
		cv2.normalize(heatMap, heatMap, 0, 255, cv2.NORM_MINMAX)
		heatMap = np.array(heatMap,'uint8')
		
		nHeatLines = GAZE_DISP_HEAT_MAP_N_HEAT_LINES
		heatLines = np.zeros(heatMap.shape,'uint8')
		for i in range(nHeatLines):
			tmp_treshold = GAZE_DISP_HEAT_MAP_THRESHOLD + (255-GAZE_DISP_HEAT_MAP_THRESHOLD)/nHeatLines * i
			if i%2 == 1:
				heatLines += cv2.threshold(heatMap,tmp_treshold,200,cv2.THRESH_BINARY)[1]
			else:
				heatLines -= cv2.threshold(heatMap,tmp_treshold,200,cv2.THRESH_BINARY)[1]
		
		contours, hierarchy = cv2.findContours(heatLines, cv.CV_RETR_TREE, cv.CV_CHAIN_APPROX_NONE)
		hierarchy_levels = utils.get_hierarchy_levels(hierarchy)
		
		ovImg = np.zeros(showPic.shape, showPic.dtype)
		heat_colors = utils.autumn(nHeatLines)
		for i in range(len(contours)):
			c2 = cv2.approxPolyDP(contours[i], 2, 0)
			cv2.polylines(ovImg, [c2], 1, heat_colors[hierarchy_levels[i]], 1)
		
		#cv2.drawContours(ovImg, contours, 0, (155,130,0), 2)
		showPic = cv2.addWeighted(showPic, 1, ovImg, GAZE_DISP_HEAT_MAP, 0)

	if GAZE_DISP_EACH > 0:
		ovImg = np.zeros(showPic.shape, showPic.dtype)
		ovImgNp = ovImg
		history_length = 2

		gaze_coords = utils.getGazeMovieCoords(gazes, stimulus, history_length, False)
		gaze_coords = sorted(gaze_coords,key=operator.itemgetter(3),reverse=True)
		for (i, x, y, prio) in gaze_coords:
			pts = cv2.ellipse2Poly((x,y),(2,2),0,0,360,int(360/6))
			opacity = float(history_length-prio+1) / history_length
			cv2.fillConvexPoly(ovImgNp, pts, (int(colors[i][0]*opacity),int(colors[i][1]*opacity),int(colors[i][2]*opacity)))
		for (i, x, y, prio) in gaze_coords:
			if prio == 1:
				cv2.circle(ovImgNp, (x,y), 15, colors[i])
	
		showPic = cv2.addWeighted(showPic, 1, ovImgNp, GAZE_DISP_EACH, 0)
			
	if GAZE_DISP_MEAN > 0:
		ovImg = np.zeros(showPic.shape, showPic.dtype)
		ovImgNp = ovImg
		
		gaze_coords = utils.getGazeMovieCoords(gazes, stimulus ,1, True)
		
		(x, y, r) = utils.getMeanWithVariance(gaze_coords)
		
		color_id = len(colors)-1
		pts = cv2.ellipse2Poly((x,y),(r,r),0,0,360,int(360/18))
		cv2.fillConvexPoly(ovImgNp, pts, (colors[color_id][0]/10,colors[color_id][1]/10,colors[color_id][2]/10))
		pts = cv2.ellipse2Poly((x,y),(2,2),0,0,360,int(360/6))
		cv2.fillConvexPoly(ovImgNp, pts, colors[color_id])
		cv2.circle(ovImgNp, (x,y), r, colors[color_id])
		
		showPic = cv2.addWeighted(showPic, 1, ovImgNp, GAZE_DISP_MEAN, 0)

	if GAZE_DISP_CLUSTERED > 0:
		ovImg = np.zeros(showPic.shape, showPic.dtype)
		ovImgNp = ovImg
		
		gaze_coords = utils.getGazeMovieCoords(gazes, stimulus ,2, True)
		
		cluster_list = []
		for i in range(3):
			[circ, profit] = utils.clusterGazes(gaze_coords,i+1,[])
			cluster_list.append([circ, profit])
		cluster_list = sorted(cluster_list, key=operator.itemgetter(1), reverse=False)
		circles = cluster_list[0][0]
		
		for (x, y, var, opa) in circles:
			color_id = len(colors)-1
			r = var #20+int(var/1.5)
			pts = cv2.ellipse2Poly((x,y),(r,r),0,0,360,int(360/18))
			cv2.fillConvexPoly(ovImgNp, pts, (colors[color_id][0]*opa/10,colors[color_id][1]*opa/10,colors[color_id][2]*opa/10))
			pts = cv2.ellipse2Poly((x,y),(4,4),0,0,360,int(360/18))
			cv2.fillConvexPoly(ovImgNp, pts, (colors[color_id][0]*opa,colors[color_id][1]*opa,colors[color_id][2]*opa))
			cv2.circle(ovImgNp, (x,y), r, (colors[color_id][0]*opa,colors[color_id][1]*opa,colors[color_id][2]*opa))
		
		showPic = cv2.addWeighted(showPic, 1, ovImgNp, GAZE_DISP_CLUSTERED, 0)
	
	""" shows final stimulus visualized image """
	cv2.imshow( "Stimulus", showPic)
	cv2.waitKey(1)


def show_sequence(stimulus, data, sequence):
	""" This function calls the frames from a specific sequence, using a scheduler"""
	
	if not stimulus.set_time(sequence.begin):
		print('  WARNING: show_sequence: Out of range. Sequence does not exist in stimulus.')
		return
	
	# set all data in this sequence to standard
	sequence.reinit()
	
	# initialize scheduler
	s = sched.scheduler(time.time, time.sleep)
	s.enterabs(sequence.time_started, 1, showFrame, (s,stimulus,sequence,data_gazes))
	s.run()

if __name__ == "__main__":
	""" load data """
	# stimulus 
	stimulus = stimulus.Stimulus(PATH_MOVIE)

	# gazes
	data_gazes = []
	for p in PATH_GAZES:
		data_gazes.append(np.load(p))
	
	# sequences
	sequences = utils.read_seq('test.seq')
	#sequences.append(sequence.Sequence(utils.time2seconds(0,02,30,000), 6, "1"))
	#sequences.append(sequence.Sequence(utils.time2seconds(0,02,45,000), 6, "2"))
	
	# precalculation of data
	colors = utils.autumn(len(data_gazes)+1)
	gaussOverlay = utils.createGaussMatrix(GAZE_DISP_HEAT_MAP_GAUSS, 0)

	""" initialize stimulus window """
	cv2.namedWindow( "Stimulus" )
	
	""" show sequences """
	for sequence in sequences:
		print "Sequence [", sequence.label,"] started at", sequence.begin, "with duration", sequence.duration
		show_sequence(stimulus, data_gazes, sequence)
		
		# if frames had to be skipped, due to slow computers, show warning
		if sequence.skipped_frames > 0:
			print "  WARNING:", sequence.skipped_frames,"frames skipped"
	
	""" close windows, if finished """
	# TODO: find out, why this does not work
	cv2.destroyAllWindows()
