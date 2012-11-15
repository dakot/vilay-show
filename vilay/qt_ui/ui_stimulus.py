# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_stimulus.ui'
#
# Created: Thu Nov  8 13:17:06 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Stimulus(object):
    def setupUi(self, Stimulus):
        Stimulus.setObjectName(_fromUtf8("Stimulus"))
        Stimulus.resize(700, 420)
        self.verticalLayout = QtGui.QVBoxLayout(Stimulus)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.stim_img = QtGui.QGraphicsView(Stimulus)
        self.stim_img.setObjectName(_fromUtf8("stim_img"))
        self.verticalLayout.addWidget(self.stim_img)
        self.frame = QtGui.QFrame(Stimulus)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.frame)
        self.horizontalLayout.setContentsMargins(2, 1, 2, 0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.stim_pos = QtGui.QLabel(self.frame)
        self.stim_pos.setObjectName(_fromUtf8("stim_pos"))
        self.horizontalLayout.addWidget(self.stim_pos)
        self.line = QtGui.QFrame(self.frame)
        self.line.setFrameShape(QtGui.QFrame.VLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.horizontalLayout.addWidget(self.line)
        self.stim_seq = QtGui.QLabel(self.frame)
        self.stim_seq.setObjectName(_fromUtf8("stim_seq"))
        self.horizontalLayout.addWidget(self.stim_seq)
        self.line_2 = QtGui.QFrame(self.frame)
        self.line_2.setFrameShape(QtGui.QFrame.VLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.horizontalLayout.addWidget(self.line_2)
        self.stim_debug = QtGui.QLabel(self.frame)
        self.stim_debug.setObjectName(_fromUtf8("stim_debug"))
        self.horizontalLayout.addWidget(self.stim_debug)
        self.verticalLayout.addWidget(self.frame)

        self.retranslateUi(Stimulus)
        QtCore.QMetaObject.connectSlotsByName(Stimulus)

    def retranslateUi(self, Stimulus):
        Stimulus.setWindowTitle(QtGui.QApplication.translate("Stimulus", "Stimulus", None, QtGui.QApplication.UnicodeUTF8))
        self.stim_pos.setText(QtGui.QApplication.translate("Stimulus", "0:00:00:0 / 0:00:00:0", None, QtGui.QApplication.UnicodeUTF8))
        self.stim_seq.setText(QtGui.QApplication.translate("Stimulus", "no sequences loaded", None, QtGui.QApplication.UnicodeUTF8))
        self.stim_debug.setText(QtGui.QApplication.translate("Stimulus", "skipped: 0", None, QtGui.QApplication.UnicodeUTF8))

