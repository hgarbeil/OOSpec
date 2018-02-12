from ctypes import *
import numpy
from numpy.ctypeslib import ndpointer
from threading import Thread
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMessageBox
import time

"""
The OO oceanoptics class is essentially a python wrapper of a minimal set of seabreeze API library functions.
This class utilizes the ctypes model to address the seabreeze dll calls.
Note that this class relies on the SeaBreeze.dll (or for linux the libseabreeze.so).
"""
class OO(QtCore.QObject):

    # signals to notify the OOSpec main class that new data has been obtained.
    newData = QtCore.pyqtSignal ()
    lastData = QtCore.pyqtSignal ()

    """OO class initialization. """
    def __init__ (self) :
        QtCore.QObject.__init__(self)

        #self.sea = CDLL ('/usr/lib/libseabreeze.so')
        self.sea = CDLL ('C:\Program Files\Ocean Optics\SeaBreeze\Library\SeaBreeze.dll')
        self.sea.seabreeze_open_spectrometer.argtypes=[c_int, POINTER(c_int)]
        self.sea.seabreeze_open_spectrometer.restype=c_int
        #self.sea.seabreeze_get_spectrometer_type.argtypes=[c_int, POINTER(c_int)]
        self.sea.seabreeze_get_model.argtypes=[c_int, POINTER(c_int), c_char_p, c_int]
        #self.sea.seabreeze_get_spectrometer_type.restype=c_char_p
        self.sea.seabreeze_get_model.restype=c_int

        self.sea.seabreeze_get_error_string.restype= c_char_p
        self.sea.seabreeze_get_error_string.argtypes= [c_int]

        self.waves = numpy.zeros(2048, numpy.float64)
        self.sea.seabreeze_get_wavelengths.argtypes=[c_int, POINTER(c_int), ndpointer(numpy.float64, flags="C_CONTIGUOUS"), c_int]
        self.sea.seabreeze_get_min_integration_time_microsec.argtypes = [c_int, POINTER(c_int)]
        self.sea.seabreeze_get_min_integration_time_microsec.restype = c_long

        #return

        self.err = c_int(-1)
        self.specnum = c_int(0)
        self.spectyp = c_char_p
        self.modelname = c_char_p("UNKNOWN")
        self.nchars = c_int(80)

        self.flag=c_int(0)

        print "opening spec "
        self.flag = self.sea.seabreeze_open_spectrometer(self.specnum, byref(self.err))
        print self.specnum
        print self.err
        print self.flag
        #print "result is %d : %s" % (self.flag, self.sea.seabreeze_get_error_string(self.err))

        print "getting spec type"
        self.nchars = self.sea.seabreeze_get_model(self.specnum, byref(self.err), self.modelname,self.nchars)
        print self.modelname
        if self.modelname.value == 'NONE' :
            print "no spectrometer found! "
            msgbox = QMessageBox ()
            msgbox.setWindowTitle("OOSpec: No spectrometer")
            msgbox.setText ("No spectrometer found...\nExiting")
            msgbox.exec_()
            exit(-1)


        #print "spec type is %s : %s" % (self.modelname, self.sea.seabreeze_get_error_string(self.err))

        print "getting spec waves"
        self.flag = self.sea.seabreeze_get_wavelengths(self.specnum, byref(self.err), self.waves, 2048)
        print self.waves[0], self.waves[2047]

        minint = c_long (0)
        minint = self.sea.seabreeze_get_min_integration_time_microsec (self.specnum, byref(self.err))
        print minint
        self.mininttime = long(minint) / 1000
        self.int_time = 100
        self.setIntegrationTime (self.int_time)

        self.spec_data = numpy.zeros ((2048), dtype=numpy.float64)
        self.maxloc = 0
        self.scans_avg = 1


    def getMaxPeaks (self) :
        print self.spec_data.shape
        return numpy.argmax (self.spec_data)


    def setData (self, x, y) :
        print x.shape
        print y.shape
        self.waves = x.copy()
        self.spec_data = y.copy()

    # send integration time in msec
    def setIntegrationTime(self, time_msec):
        self.int_time = time_msec
        micsec = c_ulong(time_msec * 1000)
        self.sea.seabreeze_set_integration_time_microsec.argtypes = [c_int, POINTER(c_int), c_ulong]
        self.sea.seabreeze_set_integration_time_microsec(self.specnum, self.err, micsec)


            # print "Int time set result is %s at %d" % ( self.sea.seabreeze_get_error_string(self.err),
            #    time_msec)
            #print "Scans to avg is : %d" % self.scans_avg


    # note that outarray is a double * numpy array
    def getSpectrum (self, outarray) :
        outarray.fill(0.)
        temparr = outarray*0.
        #print "Scans to avg is : %d " %self.scans_avg
        self.sea.seabreeze_get_formatted_spectrum.argtypes = [c_int, POINTER(c_int), 
            ndpointer(numpy.float64, flags="C_CONTIGUOUS"), c_int]
        self.sea.seabreeze_get_formatted_spectrum (self.specnum, self.err, outarray, 2048)
        #print self.sea.seabreeze_get_error_string(self.err)
        #for i in range(self.scans_avg) :
        #    self.sea.seabreeze_get_formatted_spectrum (self.specnum, self.err, temparr, 2048)
        #    outarray += temparr * (1./self.scans_avg)
        self.lastData.emit()
        

    def startFocus (self,outdata) :
        t=Thread (target=self.focus, args=(outdata,))
        t.start()

    def focus (self, outdata) :
        self.sea.seabreeze_get_formatted_spectrum.argtypes = [c_int, POINTER(c_int),
                                                              ndpointer(numpy.float64, flags="C_CONTIGUOUS"), c_int]
        self.sea.seabreeze_get_formatted_spectrum(self.specnum, self.err, outdata, 2048)
        self.focusFlag = True
        collect=0

        while (self.focusFlag and collect < 100) :
          self.sea.seabreeze_get_formatted_spectrum(self.specnum, self.err, outdata, 2048)
          self.newData.emit()
          time.sleep (1)
          collect = collect + 1

        self.lastData.emit()

    def stopFocus (self) :
        self.focusFlag = False

    def closeSpec (self) :
        self.sea.seabreeze_close_spectrometer.argtypes = [c_int, POINTER(c_int)] 
        self.sea.seabreeze_close_spectrometer (self.specnum, byref(self.err)) 
    


    
#print "done"

