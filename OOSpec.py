from PyQt5 import QtCore, QtGui, QtWidgets, uic
import sys
from os.path import expanduser
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
        self.ui.PVFitButton.clicked.connect (self.fit_data)
        self.ui.calc_pressureButton.clicked.connect (self.fit_pressure)
        self.myOO = OO ()
        self.myOO.newData.connect (self.plot_new_data)
        self.myOO.lastData.connect (self.last_collect)
        self.ui.plotWidget.mousePos.connect (self.mousePos)
        self.ui.plotWidget.linePos.connect(self.linePos)
        self.rfit = RubyFit()
        self.rfit.fitDone.connect (self.fit_done)

        #self.ui.plotWidget.setXRange (self.myOO.waves[0], self.myOO.waves[2047])
        #self.ui.plotWidget.setMyData (self.myOO.waves, self.myOO.spec_data)
        self.ui.integTimeLE.editingFinished.connect (self.setIntegTime)
        self.ui.actionLoad_Spectrum_File.triggered.connect (self.readSpectrum)
        self.ui.browseoutfileButton.clicked.connect (self.get_output_file)
        self.ui.def_roi_button.clicked.connect (self.startRoi)
        self.ui.reset_button.clicked.connect (self.resetView)

        self.integTime = 100 ;
        str="%d"%self.integTime
        self.ui.integTimeLE.setText (str)
        self.myOO.setIntegrationTime (self.integTime, 1)

        self.outdata = np.zeros(2048, dtype=np.float64)
        #self.myfit = MyFit ()
        #self.myfit.refined_fit.connect (self.fit_done)
        # get home directory and output spectrum file
        home = expanduser ("~")
        outfile = "%s/outspec.SPE"%home
        self.ui.outfileLE.setText (outfile)


    def mousePos (self, xydat) :
        #print xydat.x()
        str="%7.1f"%xydat.x()
        self.ui.xposLE.setText (str)
        str = "%7.1f"%xydat.y()
        self.ui.yposLE.setText (str)


    def readSpectrum (self) :
        myfile, _ = QtWidgets.QFileDialog.getOpenFileName (self, "Spectrum File",'',"Spec File (*.spe)")
        print myfile
        sp = SpeFile (myfile)
        self.waves = sp.x_calibration [:]
        self.outdata = sp.img[18,:]
        self.ui.plotWidget.setMyData(self.waves, self.outdata)
        self.last_collect()


    def get_output_file (self) :
        outfile,_ = QtWidgets.QFileDialog.getSaveFileName (self, "Spectrum File",'',"Spec File (*.spe)")
        self.outfileLE.setText (outfile)


    def startRoi (self) :
        self.ui.plotWidget.setBox()

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

        self.ui.plotWidget.setMyData(self.rf.wave, self.rf.ydata)
        #rf.setXY (self.rf.wave, self.newy)

    def fit_data (self) :
        print "in here"
        #self.rf.setXY (self.waves, self.outdata)
        self.rfit.fitXY ()

    def fit_pressure (self) :
        #collect params for fitting
        rsind = self.ui.ruby_scaleCB.currentIndex()
        val0 = float(self.ui.refposLE.text())

        str = self.ui.reftempLE.text()
        val1 = float(self.ui.reftempLE.text())
        val2 = float(self.ui.sampposLE.text())
        val3 = float(self.ui.samptempLE.text())
        pfitparams = np.asarray ([val0, val1, val2, val3], dtype=np.float32)
        self.rfit.set_press_params (rsind, pfitparams)
        mypressure = self.rfit.get_ruby_pressure()
        str="%f"%mypressure
        self.ui.press_calcLE.setText(str)

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
        self.waves = self.myOO.waves

    def resetView (self) :
        self.ui.plotWidget.resetView ()
        
        
        
    # start the setup for fitting   
    def last_collect (self) :
        print "Acquisition complete"
        print "Loading test data"

        self.rfit.setXY (self.waves, self.outdata)
        str='%8.2f'%self.rfit.amplitude1
        self.ui.amp0LE.setText (str)
        str = '%8.2f' % self.rfit.amplitude2
        self.ui.amp1LE.setText (str)
        str='%8.3f'%self.rfit.samp1
        self.ui.peak0LE.setText (str)
        str='%8.3f'%self.rfit.samp2
        self.ui.peak1LE.setText(str)
        str = '%5.3f' % self.rfit.samp1
        self.ui.width0LE.setText(str)
        str = '%5.3f' % self.rfit.samp2
        self.ui.width1LE.setText(str)
        str = '%5.3f' % self.rfit.fraction1
        self.ui.frac0LE.setText(str)
        str = '%5.3f' % self.rfit.fraction2
        self.ui.frac1LE.setText(str)

        # linear
        str = '%8.3f'%self.rfit.minval
        self.ui.intcptLE.setText (str)
        str ="0.0"
        self.ui.slopeLE.setText (str)
        self.ui.statusLabel.setText ("Status : Guess")

        
    def fit_done (self) :
        str='%8.2f'%self.rfit.oparams1[0]
        self.ui.amp0LE.setText (str)

        str='%8.3f'%self.rfit.oparams1[1]
        self.ui.peak0LE.setText (str)
        self.ui.sampposLE.setText(str)
        str='%5.3f'%self.rfit.oparams1[2]
        self.ui.width0LE.setText (str)
        str='%5.3f'%self.rfit.oparams1[3]
        self.ui.frac0LE.setText (str)
        str = '%8.2f' % self.rfit.oparams2[0]
        self.ui.amp1LE.setText(str)
        str = '%8.3f' % self.rfit.oparams2[1]
        self.ui.peak1LE.setText(str)
        str = '%5.3f' % self.rfit.oparams2[2]
        self.ui.width1LE.setText(str)
        str = '%5.3f' % self.rfit.oparams2[3]
        self.ui.frac1LE.setText(str)
        str = '%5.3f' % self.rfit.oparams3[0]
        self.ui.slopeLE.setText(str)
        str = '%8.2f' % self.rfit.oparams3[1]
        self.ui.intcptLE.setText(str)
        self.ui.statusLabel.setText("Status : Fitted")



        self.ui.plotWidget.over_plot (self.rfit.modelFit)
        



if __name__=='__main__':
    app = QtWidgets.QApplication(sys.argv)
    oo = OOSpec ()
    oo.show()
    sys.exit (app.exec_())