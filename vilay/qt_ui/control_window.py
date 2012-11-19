from PyQt4 import QtCore, QtGui
from ui_control import Ui_Control

import cv2
import numpy as np
import utils
import snippet

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
        self.connect(self.ui.stop,QtCore.SIGNAL("clicked()"),player.stop)
        self.connect(self.ui.back,QtCore.SIGNAL("clicked()"),self.go_back)
        self.connect(self.ui.forw,QtCore.SIGNAL("clicked()"),self.go_forward)
        self.connect(self.ui.snip_stop,QtCore.SIGNAL("clicked()"),self.snip_stop)
        
        self.connect(self.ui.snip_pre,QtCore.SIGNAL("clicked()"),self.play_pre_snippet)
        self.connect(self.ui.snip_next,QtCore.SIGNAL("clicked()"),self.play_next_snippet)
        
        self.ui.slider.sliderMoved[int].connect(self.slider_event)
        self.ui.slider.sliderReleased.connect(self.slider_released)
        
        self.ui.speed.valueChanged.connect(self.speed_changed)
    
    def update_texts(self, player):
        self.ui.time.setText('%(start)s / %(end)s' %{'start':utils.sec2time(player.stimulus.act_pos), 'end': player.stimulus.end_pos_str})
        self.ui.slider.setValue(int (self.ui.slider.maximum() * player.stimulus.act_pos / player.stimulus.length) )

        self.ui.snip_overview.show()
        
    def update_block_section(self):
        self.disconnect(self.ui.snip_box, QtCore.SIGNAL("currentIndexChanged(int)"), self.play_snippet_id)
        self.ui.snip_box.clear()
        self.ui.snip_box.addItem(self.player.snippets[0].label)
        for i in range(len(self.player.snippets)-1):
            self.ui.snip_box.addItem('Snippet '+ str(i+1) +': ' + self.player.snippets[i+1].label)   
        if self.player.snippet_id is not None:
            self.ui.snip_box.setCurrentIndex(self.player.snippet_id)
        self.connect(self.ui.snip_box, QtCore.SIGNAL("currentIndexChanged(int)"), self.play_snippet_id)
        
        self.update_snipped_pixmap()        
        
    def update_snipped_pixmap(self):
        h = int(self.ui.snip_overview.height())
        w = int(self.ui.snip_overview.width())
        
        img = np.zeros((h,w,3),'uint8')
        img[:,:,0:3] = 241
        
        for i in range(len(self.player.snippets)-1):
            begin = int(self.player.snippets[i+1].begin / self.player.stimulus.length * w)
            end = begin + int(self.player.snippets[i+1].duration / self.player.stimulus.length * w)+1
            img[:,begin:end,0] = 255
            img[:,begin:end,1] = 0
            img[:,begin:end,2] = 0
        
        img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
        
        # Qt expects 32bit BGRA data for color images:    
        qimg = QtGui.QImage(img.data, w, h, QtGui.QImage.Format_RGB32)
        qimg.ndarray = img
        
        self.snipped_pixmap = QtGui.QPixmap(qimg)
        self.ui.snip_overview.setPixmap(self.snipped_pixmap)
    
    def go_back(self, val = 4):
        time = self.player.stimulus.act_pos - val
        self.ui.time.setText('%(start)s / %(end)s' %{'start':utils.sec2time(time), 'end': self.player.stimulus.end_pos_str})
        self.player.snippets[0] = snippet.Snippet(time, self.player.stimulus.length-time, 'user defined')
        self.player.play_snippet(0)
    
    def go_forward(self, val = 4):
        time = self.player.stimulus.act_pos + val
        self.ui.time.setText('%(start)s / %(end)s' %{'start':utils.sec2time(time), 'end': self.player.stimulus.end_pos_str})
        self.player.snippets[0] = snippet.Snippet(time, self.player.stimulus.length-time, 'user defined')
        self.player.play_snippet(0)
    
    def snip_stop(self):
        self.player.set_stop_after(self.ui.snip_stop.isChecked())
    
    def play_pre_snippet(self):
        self.player.play_snippet(self.player.snippet_id - 1)
        
    def play_next_snippet(self):
        self.player.play_snippet(self.player.snippet_id + 1)

    def play_snippet_id(self):
        val = self.ui.snip_box.currentIndex()
        self.player.play_snippet(val)
    
    def slider_event(self, value):
        self.ui.slider.sliderMoved[int].disconnect(self.slider_event)
        self.player.qscheduler.stop()
        time = value *1./self.ui.slider.maximum() * self.player.stimulus.length
        self.ui.time.setText('%(start)s / %(end)s' %{'start':utils.sec2time(time), 'end': self.player.stimulus.end_pos_str})
        self.player.snippets[0] = snippet.Snippet(time, self.player.stimulus.length-time, 'user defined')
        self.player.show_frame(time)
        self.ui.slider.sliderMoved[int].connect(self.slider_event)
        
    def slider_released(self):
        self.player.load_snippet(0)
        self.player.play()
    
    def speed_changed(self):
        was_playing = self.player.qscheduler.isActive()
        if was_playing:
            self.player.qscheduler.stop()
        self.player.stimulus.speed = self.ui.speed.value()
        if was_playing:
            self.player.play()
    
    def closeEvent(self, event):
        self.player.close()
