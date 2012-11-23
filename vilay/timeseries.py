import cv2

import numpy as np

from PyQt4 import QtGui, QtCore
from qt_ui.ui_timeseries import Ui_Timeseries

from PyQt4.Qt import *
from PyQt4.Qwt5 import *
from PyQt4.Qwt5.qplt import *

import snippet

class TimeseriesWindow(QtGui.QWidget):
    def __init__(self, player, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_Timeseries()
        self.ui.setupUi(self)
        self.img = None

    def show_img(self,npimg):
        self.img = cv2.cvtColor(npimg,cv2.COLOR_BGR2BGRA)
        h, w ,c = self.img.shape
        
        # Qt expects 32bit BGRA data for color images:    
        self.qimg = QtGui.QImage(self.img.data, w, h, QtGui.QImage.Format_RGB32)
        self.qimg.ndarray = self.img
        
        scene = QtGui.QGraphicsScene()    
        scene.addPixmap(QtGui.QPixmap(self.qimg))
        self.ui.graphicsView.setScene(scene)

class TimeSeries:
    """A time series is a time-ordered vector of (time, value)-vectors. Time is
    given in seconds (float) and value is any numeric format."""
    
    def __init__(self, filename, label = "noname", approx = "none"):
        """filename: path to text-file of tab-separated values
         label (optional): string that describe this time series
         approx (default=none): approximation type between values (actually just none)"""
        
        self.filename = filename
        self.data = np.loadtxt(filename)
        self.val_min = np.amin(self.data[:,1])
        self.val_max = np.amax(self.data[:,1])
        self.label = label
        self.equal_tupel_length = self.calc_tupel_length()
        self.approx = approx
        self.act_pos = 0
        
        #self.win_w = 300
        #self.win_h = 200
        #self.win = None
        #self.img = np.zeros((self.win_h,self.win_w,3),'uint8')
        
        self.p = Plot(
            Curve(self.data[:,0], self.data[:,1], Pen(Magenta, 2), self.label))
            #Curve([self.act_pos, self.act_pos], [self.val_min, self.val_max], Pen(Red), "pos"))
        #self.p.setAxisScale(2,0,200)
        self.m = QwtPlotMarker()
        self.m.setLineStyle(2)
        self.m.attach(self.p)
  
    def show(self, time):
        self.act_pos = time
        #if self.p.AxisInterval(2)
        #self.p.set
        self.m.setXValue(self.act_pos)
        self.p.replot()
        """
        if self.win is None:
            self.win = TimeseriesWindow(self)
            self.win.setWindowTitle(self.label)
            self.win
            self.win.show()
        
        val = self.get_elem(time)
        p_val = int((val-self.val_min) / (self.val_max-self.val_min) * self.win_h)
        
        # shift left
        self.img[:,0:self.win_w-1,:] = self.img[:,1:self.win_w,:]
        self.img[:,self.win_w-1,:] = 0
        # draw value
        self.img[p_val,self.win_w-1,:] = 255
       
        #cv2.imshow('sd',self.img)
        self.win.show_img(self.img)
        
        pass
        #self.
        """
    
    def get_elem(self, request_time):
        """returns the value of the time series at a specific time point"""
        if self.approx == "none":
            if self.equal_tupel_length > 0:
                n = int( (request_time - self.data[0,0]) / self.equal_tupel_length)
                return self.data[n][1]
            else:
                print "ERROR: not implemented yet"  #TODO
                return None
        else:
            print "ERROR: only approx = 'none' implemented"
    
    def calc_tupel_length(self):
        """returns the duration of one tupel, if constant. Otherwise returns -1"""
        dist = self.data[1,0]-self.data[0,0]
        for i in range(len(self.data)-1):
            if dist != (self.data[i+1,0]-self.data[i,0]):
                return -1
        
        return dist
    
    def get_snippets(self, offset = 0, function = None ):
        """returns a list of snippets where function returns true if calculated 
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

# TODO delete (helper function for testing get_snippets)
def greater_zero(a):
    return a>0
    
