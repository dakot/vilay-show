import sys
import time 
import sched
import operator

import numpy as np

import cv
import cv2

from PyQt4 import QtCore, QtGui
from qt_ui.ui_stimulus import Ui_Stimulus
from qt_ui.ui_control import Ui_Control

import stimulus
import sequence
import timeseries
import utils
import player

import user_data

PATH_MOVIE = user_data.PATH_MOVIE # e.g. '/home/movie.m4v' 
PATH_GAZES = user_data.PATH_GAZES # e.g. ['gaze1.npy',gaze2.npy], format: time, x, y, pupil , use indy_utils.py

GAZE_DISP_EACH = 0
GAZE_DISP_MEAN = 0
GAZE_DISP_CLUSTERED = 0
GAZE_DISP_HEAT_MAP = 0
GAZE_DISP_HEAT_MAP_GAUSS = 27
GAZE_DISP_HEAT_MAP_THRESHOLD = 120
GAZE_DISP_HEAT_MAP_N_HEAT_LINES = 3

MOVIE_GRAY = False
MOVIE_OPACITY = 0.8

SPEED = 1



class Player:
    def __init__(self, stimulus):
        # general data
        self.stimulus = stimulus
        self.sequence = None
        self.sequences = []
        self.sequences.append(sequence.Sequence(utils.time2seconds(0,00,00,000), stimulus.nFrames*1./stimulus.fps, "user defined"))
        self.sequences.append(sequence.Sequence(utils.time2seconds(1,00,00,000), 55, "Eins"))
        self.sequences.append(sequence.Sequence(utils.time2seconds(1,05,00,000), 5, "Zwei"))
        self.gazes = None

        # scheduler
        self.qscheduler = QtCore.QTimer()
        QtCore.QObject.connect(self.qscheduler, QtCore.SIGNAL("timeout()"), self.run)
        
        # windows
        self.app = QtGui.QApplication(sys.argv)
        self.stim_win = StimulusWindow(self)
        self.stim_win.resize(stimulus.width+2, stimulus.height+22)
        self.stim_win.show()
        
        self.control_win = ControlWindow(self)
        self.control_win.show()
        self.control_win.update_snipped_pixmap()
        
        self.play()


    def play(self):
        if not self.qscheduler.isActive():
            if self.sequence is None:
                self.sequence = 0
                self.load_sequence()
            else:
                #self.qscheduler.start(1000)
                self.stim_win.seq.setText('Seq %(id)i/%(id_max)i: %(label)s' %{'id':self.sequence+1, 'id_max': len(self.sequences), 'label': self.sequences[self.sequence].label})
                self.control_win.update_block_section()
                self.qscheduler.start(1000./self.stimulus.speed/self.stimulus.fps)
    
    def play_seq(self, idx):
        idx = idx % len(self.sequences)
        self.qscheduler.stop()
        self.sequence = idx
        self.load_sequence()
        
        self.play()

    def show_frame_at(self, time):
        self.qscheduler.stop()
        
        self.stimulus.set_pos(time)
        self.run()

    def pause(self):
        if self.qscheduler.isActive():
            self.qscheduler.stop()

    def load_sequence(self):
        self.qscheduler.stop()
        self.stimulus.set_pos(self.sequences[self.sequence].begin)
        
        self.play()

    def next_sequence(self):
        self.qscheduler.stop()
        self.sequence += 1
        if self.sequence >= len(self.sequences):
            self.sequence = None
        else:
            self.load_sequence()

    def run(self):
        """ This function shows the frame and all visualizations. It is also responsable for synchronization of stimulus and computer time."""
                
        """ scheduler configuration """
        cpu_time = time.time()
        self.sequences[self.sequence].frame_count += 1
        #act_frame_element = s.enterabs(sequence.time_started+1/stimulus.fps/SPEED*sequence.frame_count, 1, showFrame, (s,stimulus,sequence,gazes,player))    
        
        """ load image """
        frameImg = self.stimulus.get_next_frame()
        if frameImg is None:
            return False
        
        """ adjusting stimulus, due to slow computers """
        #skipped_frames = stimulus.resync(sequence.begin + (cpu_time - sequence.time_started)*SPEED)
        #sequence.skipped_frames += skipped_frames
        
        """ when sequence is over, stop scheduler through deleting next schedule element """
        if not self.sequences[self.sequence].contains(self.stimulus.act_pos):
            self.next_sequence()
        
        """ bgr to gray convertion for using gray stimulus image """
        if MOVIE_GRAY:
            frameImg = cv2.cvtColor(frameImg,cv.CV_BGR2GRAY)
            frameImg = cv2.cvtColor(frameImg,cv.CV_GRAY2BGR)
        showPic = cv2.addWeighted(frameImg, MOVIE_OPACITY, frameImg, 0, 0)     #TODO: find better implementation
        
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
        self.stim_win.show_img(showPic)
        self.control_win.update_texts(self)
        self.stim_win.pos.setText('%(start)s / %(end)s' %{'start':utils.sec2time(self.stimulus.act_pos), 'end': self.stimulus.end_pos_str})
        #self.stim_win.debug.setText('skipped: %(fr)i' %{'fr':sequence.skipped_frames})

    def close(self):
        self.qscheduler.stop()
        self.control_win.deleteLater()
        self.stim_win.deleteLater()
        
        
class StimulusWindow(QtGui.QWidget):
    def __init__(self, player, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_Stimulus()
        self.ui.setupUi(self)
        self.player = player
        self.pos = self.ui.stim_pos
        self.seq = self.ui.stim_seq
        self.debug = self.ui.stim_debug
        self.img = self.ui.stim_img
        self.npimg = None
        
    def show_img(self,npimg):
        self.npimg = npimg
        
        h, w, channels = self.npimg.shape
        self.npimg = cv2.cvtColor(self.npimg, cv.CV_BGR2BGRA)

        # Qt expects 32bit BGRA data for color images:    
        qimg = QtGui.QImage(self.npimg.data, w, h, QtGui.QImage.Format_RGB32)
        qimg.ndarray = self.npimg
        
        scene = QtGui.QGraphicsScene()
        scene.addPixmap(QtGui.QPixmap(qimg))
        
        self.img.setScene(scene)
        
        cv2.waitKey(1)

    def closeEvent(self, event):
        self.player.close()


class ControlWindow(QtGui.QWidget):
    def __init__(self, player, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_Control()
        self.ui.setupUi(self)
        
        self.player = player
        self.snipped_pixmap = None
        
        self.update_block_section()
        
        self.connect(self.ui.play,QtCore.SIGNAL("clicked()"),player.play)
        self.connect(self.ui.pause,QtCore.SIGNAL("clicked()"),player.pause)
        self.connect(self.ui.pause,QtCore.SIGNAL("clicked()"),player.pause)
        self.connect(self.ui.back,QtCore.SIGNAL("clicked()"),self.go_back)
        self.connect(self.ui.forw,QtCore.SIGNAL("clicked()"),self.go_forward)
        
        self.connect(self.ui.seq_pre,QtCore.SIGNAL("clicked()"),self.play_pre_seq)
        self.connect(self.ui.seq_next,QtCore.SIGNAL("clicked()"),self.play_next_seq)
        
        self.ui.slider.sliderMoved[int].connect(self.slider_event)
        self.ui.slider.sliderReleased.connect(self.slider_released)
        
        self.ui.speed.valueChanged.connect(self.speed_changed)
    
    def update_texts(self, player):
        self.ui.time.setText('%(start)s / %(end)s' %{'start':utils.sec2time(player.stimulus.act_pos), 'end': player.stimulus.end_pos_str})
        self.ui.slider.setValue(int (self.ui.slider.maximum() * player.stimulus.act_pos / player.stimulus.length) )

        self.ui.seq_overview.show()
        
    def update_block_section(self):
        self.disconnect(self.ui.seq_box, QtCore.SIGNAL("currentIndexChanged(int)"), self.play_block)
        self.ui.seq_box.clear()
        self.ui.seq_box.addItem(self.player.sequences[0].label)
        for i in range(len(self.player.sequences)-1):
            self.ui.seq_box.addItem('Snippet '+ str(i+1) +': ' + self.player.sequences[i+1].label)   
        if self.player.sequence is not None:
            self.ui.seq_box.setCurrentIndex(self.player.sequence)
        self.connect(self.ui.seq_box, QtCore.SIGNAL("currentIndexChanged(int)"), self.play_block)
        
        self.update_snipped_pixmap()        
        
    def update_snipped_pixmap(self):
        h = int(self.ui.seq_overview.height())
        w = int(self.ui.seq_overview.width())
        
        img = np.zeros((h,w,3),'uint8')
        img[:,:,0:3] = 241
        
        for i in range(len(self.player.sequences)-1):
            begin = int(self.player.sequences[i+1].begin / self.player.stimulus.length * w)
            end = begin + int(self.player.sequences[i+1].duration / self.player.stimulus.length * w)+1
            img[:,begin:end,0] = 255
            img[:,begin:end,1] = 0
            img[:,begin:end,2] = 0
        
        img = cv2.cvtColor(img, cv.CV_BGR2BGRA)
        
        # Qt expects 32bit BGRA data for color images:    
        qimg = QtGui.QImage(img.data, w, h, QtGui.QImage.Format_RGB32)
        qimg.ndarray = img
        
        self.snipped_pixmap = QtGui.QPixmap(qimg)
        self.ui.seq_overview.setPixmap(self.snipped_pixmap)
    
    def go_back(self, val = 1):
        self.player.pause()
        time = self.player.stimulus.act_pos - val
        self.ui.time.setText('%(start)s / %(end)s' %{'start':utils.sec2time(time), 'end': self.player.stimulus.end_pos_str})
        self.player.sequences[0] = sequence.Sequence(time, self.player.stimulus.length-time, 'user defined')
        self.player.play_seq(0)
    
    def go_forward(self, val = 1):
        self.player.pause()
        time = self.player.stimulus.act_pos + val
        self.ui.time.setText('%(start)s / %(end)s' %{'start':utils.sec2time(time), 'end': self.player.stimulus.end_pos_str})
        self.player.sequences[0] = sequence.Sequence(time, self.player.stimulus.length-time, 'user defined')
        self.player.play_seq(0)
    
    def play_pre_seq(self):
        self.player.play_seq(self.player.sequence - 1)
        
    def play_next_seq(self):
        self.player.play_seq(self.player.sequence + 1)

    def play_block(self):
        val = self.ui.seq_box.currentIndex()
        self.player.play_seq(val)
    
    def slider_event(self, value):
        self.player.pause()
        time = value *1./self.ui.slider.maximum() * self.player.stimulus.length
        self.ui.time.setText('%(start)s / %(end)s' %{'start':utils.sec2time(time), 'end': self.player.stimulus.end_pos_str})
        self.player.sequences[0] = sequence.Sequence(time, self.player.stimulus.length-time, 'user defined')
        #self.player.show_frame_at(time)
        
    def slider_released(self):
        self.player.play_seq(0)
    
    def speed_changed(self):
        self.player.pause()
        self.player.stimulus.speed = self.ui.speed.value()
        self.player.play()
    
    def closeEvent(self, event):
        self.player.close()