from PyQt5 import QtWidgets, QtGui, QtCore

import pyqtgraph as pg
import numpy as np


class MyPlot (pg.PlotWidget):

    mousePos = QtCore.pyqtSignal(QtCore.QPointF)
    linePos = QtCore.pyqtSignal(float)

    def __init__(self, parent):
        pg.PlotWidget.__init__(self, parent)

        self.setXRange (0,1000)
        x = np.random.normal(size=1000)
        y = np.random.normal(size=1000)
        myplot = self.plot(x, y, pen=None, symbol='+')  ## setting pen=None disables line drawing
        self.scene().sigMouseMoved.connect (self.mouseMoved)

        self.maxLinePos = 700
        #self.vLine = pg.InfiniteLine (movable=True, angle=90)
        #self.vLine.setZValue(self.maxLinePos)
        #self.addItem(self.vLine, ignoreBounds=True)


    def setMyData (self, x,y) :
        self.clear()
        self.plot (x,y)

        self.myLine = self.addLine (x=self.maxLinePos,movable=True)
        self.myLine.sigPositionChangeFinished.connect (self.draggedLine)

    def draggedLine (self) :
        self.maxLinePos = self.myLine.value()
        #print "Max line pos ", self.maxLinePos
        self.linePos.emit (self.maxLinePos)

    def mouseMoved (self, evt) :
        #print evt
        #print self.plot.mapSceneToView(evt[0])
        xy= self.plotItem.vb.mapSceneToView(evt)
        xval = xy.x()
        yval = xy.y()

        xyval = QtCore.QPointF (xval,yval)
        self.mousePos.emit (xyval)

