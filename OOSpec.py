from PyQt5 import QtCore, QtGui, QtWidgets, uic
import sys
from OO import *
import numpy as np


class OOSpec(QtWidgets.QMainWindow) :

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.ui = uic.loadUi ("mainwindow.ui",self)
        self.ui.startCollectButton.clicked.connect (self.getSpectra)
        self.ui.focusButton.clicked.connect(self.startFocus)
        self.ui.stopFocusButton.clicked.connect (self.stopFocus)
        self.myOO = OO ()
        self.myOO.newData.connect (self.plot_new_data)
        self.ui.plotWidget.mousePos.connect (self.mousePos)
        self.ui.plotWidget.linePos.connect(self.linePos)
        self.ui.plotWidget.setXRange (self.myOO.waves[0], self.myOO.waves[2047])
        self.ui.plotWidget.setMyData (self.myOO.waves, self.myOO.spec_data)
        self.ui.integTimeLE.editingFinished.connect (self.setIntegTime)

        self.integTime = 100 ;
        str="%d"%self.integTime
        self.ui.integTimeLE.setText (str)
        self.myOO.setIntegrationTime (self.integTime, 1)

        self.outdata = np.zeros(2048, dtype=np.float64)

    def mousePos (self, xydat) :
        print xydat.x()
        str="%7.1f"%xydat.x()
        self.ui.xposLE.setText (str)
        str = "%7.1f"%xydat.y()
        self.ui.yposLE.setText (str)

    def linePos (self, xdat) :
        print xdat
        str = "%7.1f"% xdat
        self.ui.vlineLE.setText(str)

    def getSpectra (self) :
        print "HELLO"

        self.myOO.getSpectrum (self.outdata)
        self.ui.plotWidget.setMyData(self.myOO.waves, self.outdata)

    def startFocus (self) :
        self.myOO.startFocus (self.outdata)

    def stopFocus (self) :
        self.myOO.stopFocus ()

    def setIntegTime (self) :
        print "in here"
        val=self.ui.integTimeLE.text()
        val = int(val)
        self.myOO.setIntegrationTime (val,1)
        print float(val)

    def plot_new_data (self) :
        print "Plot new data ...."
        self.ui.plotWidget.setMyData(self.myOO.waves, self.outdata)



if __name__=='__main__':
    app = QtWidgets.QApplication(sys.argv)
    oo = OOSpec ()
    oo.show()
    sys.exit (app.exec_())