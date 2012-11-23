import sys
import time 
import sched
import operator

import numpy as np

import cv
import cv2

from PyQt4 import QtCore, QtGui
from qt_ui.stimulus_window import StimulusWindow
from qt_ui.control_window import ControlWindow

import stimulus
import snippet
import timeseries
import annotation
import utils
import player
import gazes

class Player:
    def __init__(self, stimulus):
        # scheduler
        self.qscheduler = QtCore.QTimer()
        QtCore.QObject.connect(self.qscheduler, QtCore.SIGNAL("timeout()"), self.run)
        
        # general data
        self.stimulus = stimulus
        
        self.snippets = []
        self.snippets.append(snippet.Snippet(utils.time2seconds(0,00,00,000), stimulus.nFrames*1./stimulus.fps, "user defined"))
        self.snippet_id = 0
        
        # gazess
        self.gazes = None
        
        # windows
        self.app = QtGui.QApplication(sys.argv)
        self.stim_win = StimulusWindow(self)
        self.stim_win.resize(stimulus.width+2, stimulus.height+22)
        self.stim_win.show()
        
        self.control_win = ControlWindow(self)
        self.control_win.show()
        self.control_win.update_snipped_pixmap()
        
        # time series
        self.timeseries = []
        
        # annotations
        self.annotations = []
        
        # configs
        self.movie_gray = 0
        self.movie_opacity = 1
        
        self.stop_after = False
        
        self.show_aperture = 0
        
        self.show_gazes_each = 0
        self.show_gazes_clustered = 0
        
        #inits 
        self.load_snippet(0)

    def play(self):
        if not self.qscheduler.isActive():
            # sets texts
            if self.snippet_id == 0:
                self.stim_win.snip.setText(self.snippets[self.snippet_id].label)
            else:
                self.stim_win.snip.setText('Snippet %(id)i/%(id_max)i: %(label)s' %{'id':self.snippet_id, 'id_max': len(self.snippets)-1, 'label': self.snippets[self.snippet_id].label})
            self.control_win.update_block_section()
            
            # start scheduler
            self.stimulus.start_time = time.time()
            self.stimulus.start_pos = self.stimulus.act_pos
            self.snippets[self.snippet_id].skipped_frames = 0
            self.qscheduler.start(1000./self.stimulus.speed/self.stimulus.fps)
    
    def load_snippet(self, idx):
        idx = idx % len(self.snippets)
        if self.qscheduler.isActive():
            self.qscheduler.stop()
        self.snippet_id = idx
        self.stimulus.set_pos(self.snippets[self.snippet_id].begin)

    def play_snippet(self, idx):
        was_playing = self.qscheduler.isActive()
        if was_playing:
            self.qscheduler.stop()
        self.load_snippet(idx)
        if was_playing:
            self.play()
        else:
            self.show_frame()

    def show_frame(self, time = None):
        self.qscheduler.stop()
        if time != None:
            self.stimulus.set_pos(time)
        self.run()

    def pause(self):
        if self.qscheduler.isActive():
            self.qscheduler.stop()
        else:
            self.play()
    
    def stop(self):
        self.qscheduler.stop()
        self.snippets[0] = snippet.Snippet(utils.time2seconds(0,00,00,000), self.stimulus.nFrames*1./self.stimulus.fps, "user defined")
        self.load_snippet(0)
        self.show_frame()
    
    def set_stop_after(self, val):
        self.stop_after = val
    
    def set_movie_gray(self, val):
        self.movie_gray = val

    def set_movie_opacity(self, val):
        self.movie_opacity = val
    
    def set_show_gaze_each(self, val):
        self.show_gazes_each = val
    
    def set_show_gaze_clustered(self, val):
        self.show_gazes_clustered = val
    
    def set_show_aperture(self, val):
        self.show_aperture = val
    
    def add_timeseries(self, path, name='timeseries'):
        self.timeseries.append(timeseries.TimeSeries(path, name))
    
    def add_annotation(self, path, name, timestamp_idx=0):
        self.annotations.append(annotation.Annotation(self.stimulus, path, timestamp_idx, name))
    
    def run(self):
        """ This function shows the frame and all visualizations. It is also responsable for synchronization of stimulus and computer time."""
                
        """ scheduler configuration """
        cpu_time = time.time()
        self.snippets[self.snippet_id].frame_count += 1
        #act_frame_element = s.enterabs(sequence.time_started+1/stimulus.fps/SPEED*sequence.frame_count, 1, showFrame, (s,stimulus,sequence,gazess,player))    
        
        """ load image """
        frameImg = self.stimulus.get_next_frame()
        if frameImg is None:
            return False
        
        """ adjusting stimulus, due to slow computers """
        if self.qscheduler.isActive():
            skipped_frames = self.stimulus.resync()
            self.snippets[self.snippet_id].skipped_frames += skipped_frames
        
        """ when snippet is over, stop scheduler through deleting next schedule element """
        if not self.snippets[self.snippet_id].contains(self.stimulus.act_pos):
            if self.snippet_id + 1 >= len(self.snippets):
                self.play_snippet(1)
            else:
                self.play_snippet(self.snippet_id + 1)
            if self.stop_after:
                self.qscheduler.stop()
            return
        
        """ bgr to gray convertion for using gray stimulus image """
        if self.movie_gray > 0:
            frameImg = cv2.cvtColor(frameImg,cv.CV_BGR2GRAY)
            frameImg = cv2.cvtColor(frameImg,cv.CV_GRAY2BGR)
        showPic = cv2.addWeighted(frameImg, self.movie_opacity, frameImg, 0, 0)     #TODO: find better implementation
        
        for ts in self.timeseries:
            ts.show(self.stimulus.act_pos)
        
        for an in self.annotations:
            an.show(int(self.stimulus.act_pos*self.stimulus.fps))
        
        
        heatMap = None
        if self.show_aperture > 0:
            heatMap = self.gazes.get_heat_map(self.stimulus, .5)
            aperture = cv2.resize(heatMap, (self.stimulus.width, self.stimulus.height)) / 255.
            ap_pic = showPic.copy()
            for i in range(3):
                ap_pic[:,:,i] = showPic[:,:,i] * aperture
            showPic = ap_pic
            
        if self.show_gazes_each > 0:
            ovImg = self.gazes.get_each(self.stimulus)
            showPic = cv2.addWeighted(showPic, 1, ovImg, self.show_gazes_each, 0)
        
        if self.show_gazes_clustered > 0:
            ovImg = self.gazes.get_clustered(self.stimulus, heatMap)
            showPic = cv2.addWeighted(showPic, 1, ovImg, self.show_gazes_clustered, 0)
        
        """ shows final stimulus visualized image """
        self.stim_win.show_img(showPic)
        self.control_win.update_texts(self)
        self.stim_win.pos.setText('%(start)s / %(end)s' %{'start':utils.sec2time(self.stimulus.act_pos), 'end': self.stimulus.end_pos_str})
        self.stim_win.debug.setText('skipped: %(fr)i' %{'fr':self.snippets[self.snippet_id].skipped_frames})
        cv2.waitKey(1)
        
    def close(self):
        self.qscheduler.stop()
        self.control_win.deleteLater()
        self.stim_win.deleteLater()
        for ts in self.timeseries:
            #if not ts.win is None:
            #    ts.win.deleteLater()
            if not ts.p is None:
                ts.p.deleteLater()
        for an in self.annotations:
            if not an.win is None:
                an.win.deleteLater()
        
