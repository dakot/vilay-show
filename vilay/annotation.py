import cv2

import numpy as np
import warnings

from PyQt4 import QtGui, QtCore
from qt_ui.ui_annotation import Ui_Annotation

import snippet


class AnnotationWindow(QtGui.QWidget):
    def __init__(self, player, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_Annotation()
        self.ui.setupUi(self)
        self.img = None

    def show_ann(self, header, content):
        html = "<table width='100%' border='1' cellspacing='0' cellpadding='4'>"
        for i,h in enumerate(header):
            if i < len(content):
                html += "<tr><td>"+h+"</td><td>"+content[i]+"</td></tr>"
        
        html += "</table>"
        self.ui.webView.setHtml(html)

class Annotation:
    """ A time series is a time-ordered vector of (time, value)-vectors. Time is
        given in seconds (float) and value is any numeric format."""
    
    def __init__(self, stimulus, filename, time_idx=0, label = "noname"):
        """ filename: path to text-file of tab-separated values
            label (optional): string that describe this time series
            approx (default=none): approximation type between values (actually just none)"""
        
        self.filename = filename
        self.data, self.header = self.load_file(self.filename, time_idx)
        self.idx = self.create_idx(self.data, stimulus)
        self.label = label
        
        self.win_w = 300
        self.win_h = 200
        self.win = None
        
    def show(self, time):
        if self.win is None:
            self.win = AnnotationWindow(self)
            self.win.setWindowTitle(self.label)
            self.win.show()
        
        content = self.get_elem(time)
        self.win.show_ann(self.header, content)
    
    def get_elem(self, frame):
        """ returns the value of the time series at a specific time point"""
        
        return self.data[self.idx[frame]][1]
    
    
    def get_snippets(self, offset = 0, function = None ):
        """ returns a list of snippets where function returns true if calculated 
            with time series values"""
        
        snippets = []
        if self.approx == "none":
            last_val = False
            begin = 0
            end = 0
            for (i,val) in self.data:
                if function is None:
                    act_val = bool(val > 0)
                else:
                    act_val = function(val)
                if last_val != act_val:
                    if act_val:
                        begin = i
                    else:
                        end = i
                        snippets.append(snippet.Snippet(min(max(0,begin+offset),self.data[len(self.data)-1,0]), end-begin, self.label))
                last_val = act_val
        
        return snippets

    def load_file(self, filename, time_idx=0):
        file = open(filename)
        line = file.readline()
        line_id = 1
        header = line.split("\t")
        data = []
        while True:
            line = file.readline()
            line_id += 1
            if line == '':
                break
            line = line[0:len(line)-1]
            
            vec = line.split("\t")
            
            if len(line) <= 1:
                pass
            else:
                try:
                    data.append([self.time_2_sec(vec[time_idx]), vec])
                except Exception, e:
                    print 'WARNING: read_seq: Could not read input in line ' + str(line_id) + '. Timestamp has to be float. FORMAT: timestamp (in sec) \\t annotations (\\t separated)'
        return data, header


    def time_2_sec(self, inp):
        if inp.isdigit():
            return inp
        else:
            timestr = inp.split(":")
            return int(timestr[0])*3600+int(timestr[1])*60+int(timestr[2])

    
    def create_idx(self, data, stimulus):
        idx = np.zeros(stimulus.nFrames,int)
        fps = stimulus.fps
        
        data_idx = -1
        for i in range(stimulus.nFrames):
            idx_time = i*1./fps
            
            while idx_time > data[data_idx+1][0]:
                data_idx += 1
                
                if data_idx == len(data)-1:
                    idx[i:stimulus.nFrames] = data_idx
                    return idx
            
            idx[i] = data_idx
        
        return idx