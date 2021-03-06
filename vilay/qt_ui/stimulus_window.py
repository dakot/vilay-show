from PyQt4 import QtCore, QtGui
from ui_stimulus import Ui_Stimulus

import cv2

class StimulusWindow(QtGui.QWidget):
    def __init__(self, player, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_Stimulus()
        self.ui.setupUi(self)
        self.player = player
        self.pos = self.ui.stim_pos
        self.snip = self.ui.stim_snip
        self.debug = self.ui.stim_debug
        self.img = self.ui.stim_img
        self.npimg = None
        
        self.inp_buffer = ""
    
    def keyPressEvent(self, e):
        self.inp_buffer += e.text()
        
        if e.key() == QtCore.Qt.Key_Enter or e.key() == QtCore.Qt.Key_Return:
            try:
                snip_id = int(self.inp_buffer)
                self.player.play_snippet(snip_id)
            except:
                pass
            self.inp_buffer = ''
                
            
        if e.key() == QtCore.Qt.Key_Space:
            self.player.pause()
            self.inp_buffer = ""
    
    def show_img(self,npimg):
        self.npimg = npimg
        
        h, w, channels = self.npimg.shape
        self.npimg = cv2.cvtColor(self.npimg, cv2.COLOR_BGR2BGRA)

        # Qt expects 32bit BGRA data for color images:    
        qimg = QtGui.QImage(self.npimg.data, w, h, QtGui.QImage.Format_RGB32)
        qimg.ndarray = self.npimg
        
        scene = QtGui.QGraphicsScene()
        scene.addPixmap(QtGui.QPixmap(qimg))
        
        self.img.setScene(scene)

    def closeEvent(self, event):
        self.player.close()