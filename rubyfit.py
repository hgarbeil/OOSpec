from lmfit.models import LinearModel, PseudoVoigtModel
import numpy as np
from SpeFile import *
import matplotlib.pyplot as plt


class RubyFit () :
    DEWAELE_SCALE = 0
    HYDROSTATIC_SCALE = 1
    NONHYDROSTATIC_SCALE = 2

    def __init__(self):
        self.mydata = SpeFile ('Ruby.spe')
        self.wave = self.mydata.x_calibration
        self.ydata = self.mydata.img [18,:]
        self.fitParams =[]
        self.sampleTemp = 298.
        self._reference_position = 298.

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
        bfd = result.best_values
        self.fitParams = [bfd['p1_amplitude'], bfd['p1_center'], bfd['p1_sigma'], bfd['p1_fraction'],bfd['p2_amplitude'], bfd['p2_center'], bfd['p2_sigma'], bfd['p2_fraction'],bfd['slope'],bfd['intercept']]

    def setTemperature (self, temp) :
        self.sampleTemp = temp

    def get_ruby_pressure(self):
        line_pos = self.fitParams[0]
        temperature = self.sampleTemp
        self.reference_position = line_pos
        k = 0.46299
        l = 0.0060823
        m = 0.0000010264
        reftemp = self._reference_temperature
        if temperature is None:
            temp = reftemp
        else:
            temp = temperature
        lam0 = self.reference_position
        lam = line_pos

        if self._ruby_scale == RubyFit.DEWAELE_SCALE:
            B = 9.61
            A = 1920
        elif self._ruby_scale == RubyFit.HYDROSTATIC_SCALE:
            B = 7.665
            A = 1904
        elif self._ruby_scale == RubyFit.NONHYDROSTATIC_SCALE:
            B = 5
            A = 1904

        Acorr = A + (k * (temp - reftemp))
        lam0corr = lam0 + (l * (temp - reftemp)) + (m * ((temp - reftemp) * (temp - reftemp)))

        if temp <= 80:
            lam0corr = lam0
            Acorr = A
            lam = lam + 0.92
        elif temp > 80 and temp < 298:
            lam0corr = lam0
            Acorr = A
            deltaT = temp - 298
            corr3 = deltaT ** 3 * -0.0000000337
            corr2 = deltaT ** 2 * 0.0000046231
            corr1 = deltaT * 0.0068259498
            lam = lam + 0.00003547 - corr1 - corr2 - corr3
        try:
            rat = (lam / lam0corr) ** B
        except ValueError:
            return np.NaN
        P = (Acorr / B) * rat - (Acorr / B)
        P = (P * 100) / 100.
        return P


rf = RubyFit ()
rf.fitXY ()
plt.plot (rf.wave, rf.ydata)
plt.plot (rf.wave, rf.modelFit)
plt.show()

