import sys
import time 
import sched
import operator

import numpy as np

import cv
import cv2

import utils

GAZE_DISP_EACH = 0
GAZE_DISP_HEAT_MAP = 0
GAZE_DISP_HEAT_MAP_GAUSS = 27
GAZE_DISP_HEAT_MAP_THRESHOLD = 100
GAZE_DISP_HEAT_MAP_N_HEAT_LINES = 2


movie_width = 1680.
movie_height = 727.
gaze_width = 716.
gaze_height = 368.
gaze_y_offset = 162.
offset = 0

class Gazes:
    
    def __init__(self, stimulus, gaze_files):
        self.paths = gaze_files
        
        if len(self.paths) == 0:
            print 'ERROR in gaze.py: Error loading data. Min. one file required'
            return
        
        self.gazes = []
        for path in self.paths:
            # TODO: load txt 
            self.gazes.append(np.load(path))
        self.gaussOverlay = self.createGaussMatrix(GAZE_DISP_HEAT_MAP_GAUSS, 0)
        
        self.width = np.amax(self.gazes[0][1])
        self.height = np.amax(self.gazes[0][2])
        self.x_offset = 0
        self.y_offset = 0
    
    def calibration(self, width, height, x_offset, y_offset):
        self.width = width
        self.height = height
        self.x_offset = x_offset
        self.y_offset = y_offset
    
    def get_heat_map(self, stimulus, scale=1):
        gaze_coords = self.getGazeMovieCoords(stimulus, 0, False)
        
        width = stimulus.width*scale
        height = stimulus.height*scale
        heatMap = np.zeros((height, width),'float32')
        
        gaussOverlay = cv2.resize(self.gaussOverlay.copy(),(int(self.gaussOverlay.shape[0]*scale),int(self.gaussOverlay.shape[1]*scale)))
        
        for (i, x, y, prio) in gaze_coords:
            heatMap = self.addArrayAtPosition(heatMap, gaussOverlay, int(y*height), int(x*width))
        
        cv2.normalize(heatMap, heatMap, 0, 255, cv2.NORM_MINMAX)
        heatMap = np.array(heatMap,'uint8')
        return heatMap
    
    def get_clustered(self, stimulus, heatMap = None):
        if heatMap == None:
            heatMap = self.get_heat_map(stimulus, scale=.5)
        
        nHeatLines = 3
        heatLines = np.zeros(heatMap.shape,'uint8')
        for i in range(nHeatLines):
            tmp_treshold = GAZE_DISP_HEAT_MAP_THRESHOLD + (255-GAZE_DISP_HEAT_MAP_THRESHOLD)/nHeatLines * i
            if i % 2 == 1:
                heatLines += cv2.threshold(heatMap,tmp_treshold,200,cv2.THRESH_BINARY)[1]
            else:
                heatLines -= cv2.threshold(heatMap,tmp_treshold,200,cv2.THRESH_BINARY)[1]
        
        heatLines = cv2.resize(heatLines, (stimulus.width, stimulus.height))
        
        contours, hierarchy = cv2.findContours(heatLines, cv.CV_RETR_TREE, cv.CV_CHAIN_APPROX_NONE)
        hierarchy_levels = self.get_hierarchy_levels(hierarchy)
        
        ovImg = np.zeros((stimulus.height, stimulus.width,3),'uint8')
        heat_colors = utils.autumn(nHeatLines)
        for i in range(len(contours)):
            c2 = cv2.approxPolyDP(contours[i], 2, 0)
            cv2.polylines(ovImg, [c2], 3, heat_colors[hierarchy_levels[i]], 1)
        
        #cv2.drawContours(ovImg, contours, 0, (155,130,0), 2)
        return ovImg
    
    def get_each(self, stimulus, history_length = 0, approx = False):
        ovImg = np.zeros((stimulus.height, stimulus.width,3),'uint8')
        colors = utils.autumn(len(self.gazes))
        
        gaze_coords = self.getGazeMovieCoords(stimulus, history_length, approx)
        gaze_coords = sorted(gaze_coords,key=operator.itemgetter(3),reverse=True)
        for (i, x, y, prio) in gaze_coords:
            if prio == 1:
                cv2.circle(ovImg, (int(x*stimulus.width),int(y*stimulus.height)), 15, colors[int(i)])
            pts = cv2.ellipse2Poly((int(x*stimulus.width),int(y*stimulus.height)),(2,2),0,0,360,int(360/6))
            opacity = float(history_length-prio+2) / (history_length+1)
            cv2.fillConvexPoly(ovImg, pts, (int(colors[int(i)][0]*opacity), int(colors[int(i)][1]*opacity), int(colors[int(i)][2]*opacity)))
        return ovImg    
    
    
    def getGazeMovieCoords(self, stimulus, nPast, justTakeMean):
        gaze_coords = []
        for gaze_id in range(len(self.gazes)):
            gaze_frame_id_init = int(stimulus.fps*(-self.gazes[gaze_id][0][0] + stimulus.act_pos + offset))
            
            mean_coord = np.array([0,0,0])
            for i in range(nPast+1):
                # if justTakeMean, set start_id nPast/2 later
                if justTakeMean:
                    gaze_frame_id = gaze_frame_id_init-i+int(nPast/2)
                else:
                    gaze_frame_id = gaze_frame_id_init-i
                
                # check if frame_ id exists in array
                if (gaze_frame_id >= 0) and (gaze_frame_id < self.gazes[gaze_id].shape[0]) and not np.isnan(self.gazes[gaze_id][gaze_frame_id][3]):
                    gaze_x = (self.gazes[gaze_id][gaze_frame_id][1]*1. - self.x_offset) / self.width
                    gaze_y = (self.gazes[gaze_id][gaze_frame_id][2]*1. - self.y_offset) / self.height
                    
                    #print [0, gaze_x, gaze_width, "-", 0 ,gaze_y, gaze_height]
                    if (gaze_x < 0) or (gaze_x >= 1) or (gaze_y < 0) or (gaze_y >= 1):
                        break
                    
                    if justTakeMean:
                        mean_coord += np.array([gaze_x,gaze_y,1])
                    else:
                        gaze_coords.append(np.array([gaze_id,gaze_x,gaze_y,i+1]))
            if justTakeMean and not mean_coord[2] == 0:
                gaze_coords.append(np.array([gaze_id, mean_coord[0]/mean_coord[2], mean_coord[1]/mean_coord[2], 1]))
            
        return np.array(gaze_coords)
    
    
    """ CLUSTERING """
    def gauss(self, x, s):
        return np.exp(-.5*(float(x)/s)**2)

    def createGaussMatrix(self, sigma, cut_relativ):
        dim = sigma * 6 + 1                 # outer matrix elements are maximal 0.01
        gauss_vector = np.array(range(dim))
        gauss_vector = np.vectorize(self.gauss)(gauss_vector-int(dim/2),sigma)
        cut = int(dim/2 * cut_relativ)
        gauss_vector = gauss_vector[cut:dim-cut]
        gauss_matrix = np.multiply(gauss_vector, np.reshape(gauss_vector,(dim-2*cut,1)))
        return gauss_matrix
    
    def addArrayAtPosition(self,heatMap,gaussOverlay,x,y):
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

    def hierarchy_recursion(self, hierarchy_levels, hierarchy, idx ,act_level):
        if idx < 0:
            return hierarchy_levels
        hierarchy_levels[idx] = act_level
        hierarchy_levels = self.hierarchy_recursion(hierarchy_levels, hierarchy, hierarchy[0,idx,0] ,act_level)
        hierarchy_levels = self.hierarchy_recursion(hierarchy_levels, hierarchy, hierarchy[0,idx,2] ,act_level+1)
        return hierarchy_levels

    def get_hierarchy_levels(self, hierarchy):
        if hierarchy is None:
            return np.array([])
        hierarchy_levels = np.zeros(len(hierarchy[0]),dtype=int) - 1
        
        for i in range(len(hierarchy_levels)):
            if hierarchy_levels[i] < 0:
                hierarchy_levels = self.hierarchy_recursion(hierarchy_levels, hierarchy, i ,0)
        
        return hierarchy_levels
