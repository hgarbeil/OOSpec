from PyQt5 import QtCore, QtGui, QtWidgets, uic
import sys
from OO import *
from myfit import *
import numpy
from rubyfit import *



class OOSpec(QtWidgets.QMainWindow) :

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.ui = uic.loadUi ("mainwindow.ui",self)
        self.ui.startCollectButton.clicked.connect (self.getSpectra)
        self.ui.focusButton.clicked.connect(self.startFocus)
        self.ui.stopFocusButton.clicked.connect (self.stopFocus)
        ###
        self.ui.testdataButton.clicked.connect (self.testdata)
        self.myOO = OO ()
        self.myOO.newData.connect (self.plot_new_data)
        self.myOO.lastData.connect (self.last_collect)
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
        #self.myfit = MyFit ()
        #self.myfit.refined_fit.connect (self.fit_done)
        self.rfit = RubyFit ()

    def mousePos (self, xydat) :
        #print xydat.x()
        str="%7.1f"%xydat.x()
        self.ui.xposLE.setText (str)
        str = "%7.1f"%xydat.y()
        self.ui.yposLE.setText (str)

    def linePos (self, xdat) :
        str = "%7.1f"% xdat
        self.ui.vlineLE.setText(str)

    def testdata (self) :

        x = numpy.zeros(315, dtype=numpy.float32)
        y = numpy.zeros(315, dtype=numpy.float32)
        
        f = file("M:/data/HE_P1.OO_Spec", 'r')
        f.readline()
        count = 0
        for line in f:
            m = line.split()
            x[count] = m[0]
            y[count] = m[1]
            count = count + 1
            if count == 315:
                break
        f.close()
        
        wave0 = x[0]
        wave1 = x[count-1]
        wavestep = (wave1 - wave0) / 2047.
        self.newx = numpy.zeros(2048, dtype=numpy.float32)
        self.newy = numpy.zeros(2048, dtype=numpy.float32)



        for i in range (2048) :
            self.newx[i]=wave0+i*wavestep
        
        self.newy = numpy.interp (self.newx, x, y)
        #for i in range (2048) :
        #    print i, self.newx[i], self.newy[i]

        #print newy.shape

        #self.myOO.setData (newx, newy)
        #loc = self.myOO.getMaxPeaks ()
        #maxval = numpy.max(self.myOO.newy)
        #minval = numpy.min(self)
        #print loc
        #mystr = "max loc is %d"%loc


        testx = x[140:200]
        testy = y[140:200]
        #self.myfit.set_x_y (self.newx, self.newy)
        rf = RubyFit ()
        self.ui.plotWidget.setMyData(rf.wave, rf.ydata)
        #rf.setXY (self.newx, self.newy)
        rf.fitXY ()



    def getSpectra (self) :
        self.myOO.getSpectrum (self.outdata)
        self.ui.plotWidget.setMyData(self.myOO.waves, self.outdata)
        #self.last_collect()

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
        #print "Plot new data ...."
        self.ui.plotWidget.setMyData(self.myOO.waves, self.outdata)
        
        
        
    # start the setup for fitting   
    def last_collect (self) :
        print "Acquisition complete"
        print "Loading test data"
        self.rfit.setXY (self.myOO.waves, self.outdata)
        return


        str='%f'%self.myfit.params0[0]
        self.ui.base0LE.setText (str)

        self.ui.amp0LE.setText (str)
        str='%f'%self.myfit.params0[2]
        self.ui.peak0LE.setText (str)
        str='%f'%self.myfit.params0[3]
        self.ui.width0LE.setText (str)
        self.myfit.do_fit(1)
        str='%f'%self.myfit.params1[0]
        self.ui.base1LE.setText (str)
        str='%f'%self.myfit.params1[1]
        self.ui.amp1LE.setText (str)
        str='%f'%self.myfit.params1[2]
        self.ui.peak1LE.setText (str)
        str='%f'%self.myfit.params1[3]
        self.ui.width1LE.setText (str)
        #self.myfit.do_fit(1)
        
    def fit_done (self) :
        str='%f'%self.myfit.params0[0]
        self.ui.base0LE.setText (str)
        str='%f'%self.myfit.params0[1]
        self.ui.amp0LE.setText (str)
        str='%f'%self.myfit.params0[2]
        self.ui.peak0LE.setText (str)
        str='%f'%self.myfit.params0[3]
        self.ui.width0LE.setText (str)
        



if __name__=='__main__':
    app = QtWidgets.QApplication(sys.argv)
    oo = OOSpec ()
    oo.show()
    sys.exit (app.exec_())