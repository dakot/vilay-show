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

GAZE_DISP_EACH = 0.1
GAZE_DISP_MEAN = 0
GAZE_DISP_CLUSTERED = 0
GAZE_DISP_HEAT_MAP = 1
GAZE_DISP_HEAT_MAP_GAUSS = 27
GAZE_DISP_HEAT_MAP_THRESHOLD = 120
GAZE_DISP_HEAT_MAP_N_HEAT_LINES = 3

MOVIE_GRAY = False
MOVIE_OPACITY = 0.8

SPEED = 1


def show_sequence(stimulus, data, sequence, player):
    """ This function calls the frames from a specific sequence, using a scheduler"""
    
    if not stimulus.set_pos(sequence.begin):
        print('  WARNING: show_sequence: Out of range. Sequence does not exist in stimulus.')
        return
    
    # set all data in this sequence to standard
    sequence.reinit()
    
    # initialize scheduler
    s = sched.scheduler(time.time, time.sleep)
    s.enterabs(sequence.time_started, 1, showFrame, (s,stimulus,sequence,data_gazes,player,))
    s.run()

def run_frequently():
    showFrame(stimulus,sequence,gazes,player)
    #print "sched"
    pass
    
if __name__ == "__main__":
    """ load data """
    # stimulus 
    stimulus = stimulus.Stimulus(PATH_MOVIE)

    # gazes
    data_gazes = []
    for p in PATH_GAZES:
        data_gazes.append(np.load(p))
    
    ts = timeseries.TimeSeries("timeseries/dlpfc.txt", "dlpfc")
    
    
    player = player.Player(stimulus)
    
    """old"""
    
    # sequences
    #sequences = ts.get_sequences(offset=-3, function=timeseries.greater_zero)
    #sequences = tils.read_seq('seq/clusterevent17.txt')
    #sequences = []
    #sequences.append(sequence.Sequence(utils.time2seconds(1,02,30,000), 60, "1"))
    #sequences.append(sequence.Sequence(utils.time2seconds(0,02,45,000), 6, "2"))
    
    # precalculation of data
    #colors = utils.autumn(len(data_gazes)+1)
    #gaussOverlay = utils.createGaussMatrix(GAZE_DISP_HEAT_MAP_GAUSS, 0)

    """ QT environment """
    """app = QtGui.QApplication(sys.argv)
    stim_app = StimulusWindow()
    stim_app.show()
    stim_app.resize(stimulus.width+2, stimulus.height+22)
    
    control = ControlWindow()
    control.show()
    
    qscheduler = QtCore.QTimer()
    QtCore.QObject.connect(qscheduler, QtCore.SIGNAL("timeout()"), run_frequently)
    sequence = sequences[0]
    gazes = data_gazes
    player = stim_app
    
    qscheduler.start(1./stimulus.fps)
    """
    """ show sequences """
    """for i in range(len(sequences)):
        if not stimulus.set_pos(sequences[i].begin):
            print('  WARNING: show_sequence: Out of range. Sequence does not exist in stimulus.')
            break

        #showFrame(s,stimulus,sequence,gazes,player)
        print "Sequence [", sequences[i].label,"] started at", utils.sec2time(sequences[i].begin), "with duration", sequences[i].duration
        #stim_app.seq.setText('Seq %(id)i/%(id_max)i: %(label)s' %{'id':i+1, 'id_max': len(sequences), 'label': sequences[i].label})
        #show_sequence(stimulus, data_gazes, sequences[i], stim_app)
        
        # if frames had to be skipped, due to slow computers, show warning
        if sequences[i].skipped_frames > 0:
            print "  WARNING:", sequences[i].skipped_frames,"frames skipped"
    """
    """ close windows, if finished """
    #sys.exit(app.exec_())