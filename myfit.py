from PyQt5 import QtCore
import numpy as np
from gaussfitter import * 


class MyFit(QtCore.QObject) :

    refined_fit = QtCore.pyqtSignal()
    def __init__(self):
        QtCore.QObject.__init__(self)
        self.npts = 2048
        self.x = np.zeros (2048, dtype=np.float32)
        self.y = self.x.copy()
        self.peakLoc0 = 1024
        self.maxval = -100
        self.minval = 1E6
        self.dataFlag = False
        self.break10ind = 0
        self.width0 = 0
        self.xmax0=0
        self.amp0=0
        self.params0 = []
        self.width1 = 0.
        self.xmax1 = 0.
        self.amp1 = 0.
        self.params1 = []

    def set_x_y (self, xarr, yarr) :
        self.dataFlag = True
        
        
        self.x = xarr.copy()
        self.y = yarr.copy()

        print 'data has been copied'

        # we make a guess of the params by analyzing the x and y
        # note that the 0 peak is the higher longer wavelength located peak, the smaller peak to the
        # shorter wavelengths is termed peak1
        self.peakLoc0 = np.argmax (self.y)
        self.maxval = self.y[self.peakLoc0]
        self.minval = np.min (self.y)
        self.amp0 = self.maxval - self.minval
        self.base10 = self.minval+.1 * self.amp0
        base25 = self.minval+.25 * self.amp0
        self.xmax0 = self.x[self.peakLoc0]
         # get the approximate width of peak by searching from peakloc
        for ind,val in np.ndenumerate (self.y) :
            if ind[0] <= self.peakLoc0 : continue
            if val < self.base10 :
                
                self.width0 = abs(self.xmax0 - self.x[ind[0]]) /2.
                break 
        
        
        self.params0 =[]
        self.params0.append (self.base10)
        self.params0.append (self.amp0)
        self.params0.append (self.xmax0)
        self.params0.append (self.width0)
        
        
        
        # Reset end1
        #find the left peak now by doing a search from peak to the shorter wavelengths
        #first create a sub array going from shortest wavelength to start of second peak, omitting second peak
        end1 = yarr.size - 1
        for i in range (self.peakLoc0,0,-1):
            yval = yarr[i]
            if yval < base25 :
                end1 = i
                break
        xsub = xarr[0:end1]
        ysub = yarr[0:end1]
        self.peakLoc1 = np.argmax (ysub)
        self.amp1 = np.max(ysub) - self.minval
        self.xmax1 = xsub[self.peakLoc1]
        maxval = np.max(ysub)
        for i in range (self.peakLoc1,0,-1) :
            val = ysub[i]
            if val < self.base10 :
                
                self.break10ind = i
                self.width1 = abs(self.xmax1 - xsub[i]) / 2.
                break 
       
        

        strval = "found max at : %f   val is : %f"%(self.xmax1, maxval)
        self.params1=[]
        self.params1.append(self.base10)
        self.params1.append (self.amp1)
        self.params1.append (self.xmax1)
        self.params1.append (self.width1)
        


       
            
        
        
        print "width guess is ",self.width1
        #mpp = onedgaussfit (self.x, self.y, params=[self.base10, self.maxval, xmax, self.width0])
        #mpp = onedgaussfit (self.x, self.y, params=[1170,8900,695,.5])
         
        #print mpp[0]
        #myarr = mpp[1]
        
        
        #fout= open ('C:/Users/harold/fity.txt','w')
        #for ind,val in np.ndenumerate (myarr):
        #    str = "%f\n"%val
        #   fout.write (str)
        #fout.close()
    
    
    def do_fit (self, peaknum):
        mpp = onedgaussfit (self.x, self.y, params=self.params0)
        self.params0 = mpp[0]
        self.refined_fit.emit ()
        