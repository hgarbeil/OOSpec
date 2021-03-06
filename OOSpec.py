from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox
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
        # OceanOptics class calls ocean optics seabreeze library calls.
        self.myOO = OO()
        self.myOO.newData.connect (self.plot_new_data)
        self.myOO.lastData.connect (self.last_collect)
        self.ui.plotWidget.mousePos.connect (self.mouse_pos)
        self.ui.plotWidget.linePos.connect(self.linePos)
        self.rfit = RubyFit()
        self.rfit.fitDone.connect (self.fit_done)

        #self.ui.plotWidget.setXRange (self.myOO.waves[0], self.myOO.waves[2047])
        #self.ui.plotWidget.setMyData (self.myOO.waves, self.myOO.spec_data)

        #Integration time
        self.ui.integTimeLE.editingFinished.connect (self.setIntegTime)
        self.ui.lessLessITButton.clicked.connect (self.ll_IntTime)
        self.ui.lessITButton.clicked.connect(self.l_IntTime)
        self.ui.moreMoreITButton.clicked.connect(self.mm_IntTime)
        self.ui.moreITButton.clicked.connect(self.m_IntTime)

        self.ui.actionLoad_Spectrum_File.triggered.connect (self.read_spectrum)
        self.ui.actionLoad_AscSpectrum_File.triggered.connect(self.read_ascii_spectrum)
        self.ui.actionAbout_OOSpec.triggered.connect (self.about_program)
        self.ui.save_specButton.clicked.connect (self.save_spectrum)
        self.ui.browseoutfileButton.clicked.connect (self.get_output_file)
        self.ui.def_roi_button.clicked.connect (self.startRoi)
        self.ui.reset_button.clicked.connect (self.resetView)

        self.integTime = 100 ;
        str="%d"%self.integTime
        self.ui.integTimeLE.setText (str)
        self.myOO.setIntegrationTime (self.integTime)

        self.outdata = np.zeros(2048, dtype=np.float64)
        #self.myfit = MyFit ()
        #self.myfit.refined_fit.connect (self.fit_done)
        # get home directory and output spectrum file
        home = expanduser ("~")
        outfile = "%s\outspec.txt"%home
        self.ui.outfileLE.setText (outfile)


    def mouse_pos (self, xydat) :
        #print xydat.x()
        str="%7.1f"%xydat.x()
        self.ui.xposLE.setText (str)
        str = "%7.1f"%xydat.y()
        self.ui.yposLE.setText (str)


    def read_spectrum (self) :
        """ Method to read an .spe file.
        The filename is queried for and received by QFileDialog.
        The file reading is accomplished by SpeFile class """
        myfile, _ = QtWidgets.QFileDialog.getOpenFileName (self, "Spectrum File",'',"SPE File (*.SPE)")
        print myfile
        sp = SpeFile (myfile)
        self.waves = sp.x_calibration [:]
        self.outdata = sp.img[18,:]
        self.ui.plotWidget.setMyData(self.waves, self.outdata)
        self.last_collect()

    def read_ascii_spectrum (self) :
        """ Method to read an .txt file.
        The filename is queried for and received by QFileDialog.
        The file reading is accomplished by SpeFile class """
        myfile, _ = QtWidgets.QFileDialog.getOpenFileName (self, "Spec Text File",'',"Text File (*.txt)")
        print myfile
        count = 0
        wvs =[]
        vals=[]
        for line in myfile :
            line = line.strip()
            strs = line.split()
            w = float (strs[0])
            v = float (strs[1])
            wvs.append (w)
            vals.append(v)
        self.waves = np.asarray(wvs, dtype=np.float32)
        self.vals = np.asarray(vals, dtype=np.float32)
        self.ui.plotWidget.setMyData(self.waves, self.outdata)
        self.last_collect()


    def get_output_file (self) :
        outfile,_ = QtWidgets.QFileDialog.getSaveFileName (self, "ASCII Spec File",'',"Text file (*.txt)")
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
        val=self.ui.integTimeLE.text()
        val = int(val)
        self.integTime = val
        self.myOO.setIntegrationTime (val)

    def setTimeVal (self, val) :
        str = "%d" % val
        self.ui.integTimeLE.setText(str)
        self.myOO.setIntegrationTime(val)
        self.integTime = val

    def m_IntTime (self) :
        val = self.integTime + 25
        self.setTimeVal (val)

    def mm_IntTime(self):
        val = self.integTime + 100
        self.setTimeVal(val)

    def l_IntTime(self):
        val = self.integTime - 25
        if val < 0 :
            val = self.integTime / 2
        self.setTimeVal(val)

    def ll_IntTime(self):
        val = self.integTime - 100
        if val < 0:
            val = self.integTime / 4
        self.setTimeVal(val)


    def plot_new_data (self) :
        #print "Plot new data ...."
        self.ui.plotWidget.setMyData(self.myOO.waves, self.outdata)
        self.waves = self.myOO.waves

    def resetView (self) :
        self.ui.plotWidget.resetView ()
        
        
        
    # start the setup for fitting   
    def last_collect (self) :
        """The method called after the spectrum has been displayed in preparation for fitting.
        Text fields for the fit tab filled in based on spectrum estimation and peak search results."""
        #print "Acquisition complete"
        #print "Loading test data"
        self.waves = self.myOO.waves
        self.rfit.setXY (self.waves, self.outdata)
        str='%8.2f'%self.rfit.amplitude1
        self.ui.amp0LE.setText(str)
        str = '%8.2f' % self.rfit.amplitude2
        self.ui.amp1LE.setText(str)
        str='%8.3f'%self.rfit.samp1
        self.ui.peak0LE.setText(str)
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
        """ This method is called by the rubyfit class.
        This will display the fitted spectrum over the original raw data.
        """
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

    # output spectrum to file
    # get filename from as
    # two column ascii file
    # col1 : wavelength in nm
    # col2 : intensity DN

    def save_spectrum (self):
        """ This method is called by ui.save_specButton
        the function gets filename from the ui.outfileLE line edit
        the output ascii file is two columns, col1: wavelength in nm and col2 : DN
        """
        #need to get output name from text field
        numbins = numpy.size(self.myOO.waves)
        ofilename = self.ui.outfileLE.text()
        ofile = open (ofilename, 'w')
        print 'writing to file %s'%ofilename
        str='Wavelen\tDN\n'
        ofile.write (str)
        for i in range (numbins) :
            w = self.myOO.waves[i]
            v = self.outdata[i]
            str='%f\t%f\n'%(w,v)
            ofile.write(str)
        ofile.close()



    def about_program (self) :
        print "OOSpec V1.0"
        msg = QMessageBox()
        msg.setWindowTitle ("OOSpec : V1.0")
        msg.setText ("HIGP/SOEST/UHM 2018")
        msg.exec_()

if __name__=='__main__':
    """ global main function which instantiates the QApp class
    and the OOSpec class
    """
    app = QtWidgets.QApplication(sys.argv)
    oo = OOSpec ()
    oo.show()
    sys.exit (app.exec_())