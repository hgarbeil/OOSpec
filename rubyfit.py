from lmfit.models import LinearModel, PseudoVoigtModel
import numpy as np
from SpeFile import *
import matplotlib.pyplot as plt


class RubyFit () :

    def __init__(self):
        self.mydata = SpeFile ('Ruby.spe')
        self.wave = self.mydata.x_calibration
        self.ydata = self.mydata.img [18,:]

    def setXY (self, x, y) :
        self.wave = x.copy()
        self.ydata = y.copy()

    def analyze (self) :
        x = self.wave
        y = self.ydata
        self.npts = y.size
        self.maxval = np.max(y)
        self.minval = np.min(y)
        loc = np.argmax (y)
        self.sample_position = self.wave[loc]

    def fitXY (self) :
        self.analyze ()
        amplitude = self.maxval - self.minval
        peak1 = PseudoVoigtModel (prefix='p1_')
        peak2 = PseudoVoigtModel (prefix='p2_')
        basef = LinearModel ()
        model = peak1 + peak2 + basef
        params = model.make_params(
            p1_center = self.sample_position,
            p2_center = self.sample_position - 1.5,
            p1_amplitude = amplitude,
            p2_amplitude = amplitude * 0.6,
            p1_sigma = 0.25,
            p2_sigma = 0.25,
            p1_fraction = 0.8,
            p2_fraction = 0.8,
            slope = 0,
            intercept = self.minval
        )
        result = model.fit (self.ydata, x=self.wave, **params)
        self.modelFit = result.best_fit






rf = RubyFit ()
rf.fitXY ()
plt.plot (rf.wave, rf.ydata)
plt.plot (rf.wave, rf.modelFit)
plt.show()

