# -*- coding=utf-8 -*-
__author__ = 'Yadavito'


# external #
import matplotlib.pyplot as plt
import numpy as np
from scipy.fftpack import fft, ifft, fftshift

class MotherWavelet(object):
    """Class for MotherWavelets.

    Contains methods related to mother wavelets.  Also used to ensure that new
    mother wavelet objects contain the minimum requirements to be used in the
    cwt related functions.

    """

    @staticmethod
    def get_coefs(self):
        """Raise error if method for calculating mother wavelet coefficients is
        missing!

        """

        raise NotImplementedError('get_coefs needs to be implemented for the mother wavelet')

    @staticmethod
    def get_coi_coef(sampf):
        """Raise error if Cone of Influence coefficient is not set in
        subclass wavelet. To follow the convention in the literature, please define your
        COI coef as a function of period, not scale - this will ensure
        compatibility with the  method.

        """

        raise NotImplementedError('coi_coef needs to be implemented in subclass wavelet')

    #add methods for computing cone of influence and mask
    def get_coi(self):
        """Compute cone of influence."""

        y1 =  self.coi_coef * np.arange(0, self.len_signal / 2)
        y2 = -self.coi_coef * np.arange(0, self.len_signal / 2) + y1[-1]
        coi = np.r_[y1, y2]
        self.coi = coi
        return coi

    def get_mask(self):
        """Get mask for cone of influence.

        Sets self.mask as an array of bools for use in np.ma.array('', mask=mask)

        """

        mask = np.ones(self.coefs.shape)
        masks = self.coi_coef * self.scales
        for s in range(0, len(self.scales)):
            if (s != 0) and (int(np.ceil(masks[s])) < mask.shape[1]):
                mask[s,np.ceil(int(masks[s])):-np.ceil(int(masks[s]))] = 0
        self.mask = mask.astype(bool)
        return self.mask

class SDG(MotherWavelet):
    """Class for the SDG MotherWavelet (a subclass of MotherWavelet).

    SDG(self, len_signal = None, pad_to = None, scales = None, sampf = 1,
        normalize = True, fc = 'bandpass')

    Parameters
    ----------
    len_signal : int
        Length of time series to be decomposed.

    pad_to : int
        Pad time series to a total length `pad_to` using zero padding (note,
        the signal will be zero padded automatically during continuous wavelet
        transform if pad_to is set). This is used in the fft function when
        performing the convolution of the wavelet and mother wavelet in Fourier
        space.

    scales : array
        Array of scales used to initialize the mother wavelet.

    sampf : float
        Sample frequency of the time series to be decomposed.

    normalize : bool
        If True, the normalized version of the mother wavelet will be used (i.e.
        the mother wavelet will have unit energy).

    fc : string
        Characteristic frequency - use the 'bandpass' or 'center' frequency of
        the Fourier spectrum of the mother wavelet to relate scale to period
        (default is 'bandpass').

    Returns
    -------
    Returns an instance of the MotherWavelet class which is used in the cwt and
    icwt functions.

    Examples
    --------
    Create instance of SDG mother wavelet, normalized, using 10 scales and the
    center frequency of the Fourier transform as the characteristic frequency.
    Then, perform the continuous wavelet transform and plot the scalogram.

    # x = numpy.arange(0,2*numpy.pi,numpy.pi/8.)
    # data = numpy.sin(x**2)
    # scales = numpy.arange(10)
    #
    # mother_wavelet = SDG(len_signal = len(data), scales = np.arange(10),normalize = True, fc = 'center')
    # wavelet = cwt(data, mother_wavelet)
    # wave_coefs.scalogram()

    Notes
    -----
    None

    References
    ----------
    Addison, P. S., 2002: The Illustrated Wavelet Transform Handbook.  Taylor
      and Francis Group, New York/London. 353 pp.

    """

    def __init__(self,len_signal=None,pad_to=None,scales=None,sampf=1,normalize=True, fc = 'bandpass'):
        """Initilize SDG mother wavelet"""

        self.name='second degree of a Gaussian (mexican hat)'
        self.sampf = sampf
        self.scales = scales
        self.len_signal = len_signal
        self.normalize = normalize

        #set total length of wavelet to account for zero padding
        if pad_to is None:
            self.len_wavelet = len_signal
        else:
            self.len_wavelet = pad_to

        #set admissibility constant
        if normalize:
            self.cg = 4 * np.sqrt(np.pi) / 3.
        else:
            self.cg = np.pi

        #define characteristic frequency
        if fc is 'bandpass':
            self.fc = np.sqrt(5./2.) * self.sampf/(2 * np.pi)
        elif fc is 'center':
            self.fc = np.sqrt(2.) * self.sampf / (2 * np.pi)
        else:
            raise CharacteristicFrequencyError("fc = %s not defined"%(fc,))

        # coi_coef defined under the assumption that period is used, not scale
        self.coi_coef = 2 * np.pi * np.sqrt(2. / 5.) * self.fc # Torrence and
                                                               # Compo 1998

        # compute coefficients for the dilated mother wavelet
        self.coefs = self.get_coefs()

    def get_coefs(self):
        """Calculate the coefficients for the SDG mother wavelet"""

        # Create array containing values used to evaluate the wavelet function
        xi=np.arange(-self.len_wavelet / 2., self.len_wavelet / 2.)

        # find mother wavelet coefficients at each scale
        xsd = -xi * xi / (self.scales[:,np.newaxis] * self.scales[:,np.newaxis])

        if self.normalize is True:
            c=2. / (np.sqrt(3) * np.power(np.pi, 0.25))
        else:
            c=1.

        mw = c * (1. + xsd) * np.exp(xsd / 2.)

        self.coefs = mw

        return mw

class Morlet(MotherWavelet):
    """Class for the Morlet MotherWavelet (a subclass of MotherWavelet).

    Morlet(self, len_signal = None, pad_to = None, scales = None,
           sampf = 1, f0 = 0.849)

    Parameters
    ----------
    len_signal : int
        Length of time series to be decomposed.

    pad_to : int
        Pad time series to a total length `pad_to` using zero padding (note,
        the signal will be zero padded automatically during continuous wavelet
        transform if pad_to is set). This is used in the fft function when
        performing the convolution of the wavelet and mother wavelet in Fourier
        space.

    scales : array
        Array of scales used to initialize the mother wavelet.

    sampf : float
        Sample frequency of the time series to be decomposed.

    f0 : float
        Central frequency of the Morlet mother wavelet.  The Fourier spectrum of
        the Morlet wavelet appears as a Gaussian centered on f0.  f0 defaults
        to a value of 0.849 (the angular frequency would be ~5.336).

    Returns
    -------
    Returns an instance of the MotherWavelet class which is used in the cwt
    and icwt functions.

    Examples
    --------
    Create instance of Morlet mother wavelet using 10 scales, perform the
    continuous wavelet transform, and plot the resulting scalogram.

    # x = numpy.arange(0,2*numpy.pi,numpy.pi/8.)
    # data = numpy.sin(x**2)
    # scales = numpy.arange(10)
    #
    # mother_wavelet = Morlet(len_signal=len(data), scales = np.arange(10))
    # wavelet = cwt(data, mother_wavelet)
    # wave_coefs.scalogram()

    Notes
    -----
    * Morlet wavelet is defined as having unit energy, so the `normalize` flag
      will always be set to True.

    * The Morlet wavelet will always use f0 as it's characteristic frequency, so
      fc is set as f0.

    References
    ----------
    Addison, P. S., 2002: The Illustrated Wavelet Transform Handbook.  Taylor
      and Francis Group, New York/London. 353 pp.

    """

    def __init__(self, len_signal=None, pad_to=None, scales=None, sampf=1,
                 normalize=True, f0=0.849):
        """Initilize Morlet mother wavelet."""

        from scipy.integrate import trapz

        self.sampf = sampf
        self.scales = scales
        self.len_signal = len_signal
        self.normalize = True
        self.name = 'Morlet'

        # set total length of wavelet to account for zero padding
        if pad_to is None:
            self.len_wavelet = len_signal
        else:
            self.len_wavelet = pad_to

        # define characteristic frequency
        self.fc = f0

        # Cone of influence coefficient
        self.coi_coef = 2. * self.sampf / (self.fc + np.sqrt(2. + self.fc**2) *
                        np.sqrt(2)); #Torrence and Compo 1998 (in code)

        # set admissibility constant
        # based on the simplified Morlet wavelet energy spectrum
        # in Addison (2002), eqn (2.39) - should be ok for f0 >0.84
        f = np.arange(0.001, 50, 0.001)
        y = 2. * np.sqrt(np.pi) * np.exp(-np.power((2. * np.pi * f -
            2. * np.pi * self.fc), 2))
        self.cg =  trapz(y[1:] / f[1:]) * (f[1]-f[0])

        # compute coefficients for the dilated mother wavelet
        self.coefs = self.get_coefs()

    def get_coefs(self):
        """Calculate the coefficients for the Morlet mother wavelet."""

        # Create array containing values used to evaluate the wavelet function
        xi=np.arange(-self.len_wavelet / 2., self.len_wavelet / 2.)

        # find mother wavelet coefficients at each scale
        xsd = xi / (self.scales[:,np.newaxis])

        mw = np.power(np.pi,-0.25) * \
                     (np.exp(np.complex(1j) * 2. * np.pi * self.fc * xsd) - \
                     np.exp(-np.power((2. * np.pi * self.fc), 2) / 2.)) *  \
                     np.exp(-np.power(xsd, 2) / 2.)

        self.coefs = mw

        return mw

class Wavelet(object):
    """Class for Wavelet object.

    The Wavelet object holds the wavelet coefficients as well as information on
    how they were obtained.

    """

    def __init__(self, wt, wavelet, weighting_function, signal_dtype, deep_copy=True):
        """Initialization of Wavelet object.

        Parameters
        ----------
        wt : array
            Array of wavelet coefficients.

        wavelet : object
            Mother wavelet object used in the creation of `wt`.

        weighting_function : function
            Function used in the creation of `wt`.

        signal_dtype : dtype
            dtype of signal used in the creation of `wt`.

        deep_copy : bool
            If true (default), the mother wavelet object used in the creation of
            the wavelet object will be fully copied and accessible through
            wavelet.motherwavelet; if false, wavelet.motherwavelet will be a
            reference to the motherwavelet object (that is, if you change the
            mother wavelet object, you will see the changes when accessing the
            mother wavelet through the wavelet object - this is NOT good for
            tracking how the wavelet transform was computed, but setting
            deep_copy to False will save memory).

        Returns
        -------
        Returns an instance of the Wavelet class.

        """

        from copy import deepcopy
        self.coefs = wt[:,0:wavelet.len_signal]

        if wavelet.len_signal !=  wavelet.len_wavelet:
            self._pad_coefs = wt[:,wavelet.len_signal:]
        else:
            self._pad_coefs = None
        if deep_copy:
            self.motherwavelet = deepcopy(wavelet)
        else:
            self.motherwavelet = wavelet

        self.weighting_function = weighting_function
        self._signal_dtype = signal_dtype

    def get_gws(self):
        """Calculate Global Wavelet Spectrum.

        References
        ----------
        Torrence, C., and G. P. Compo, 1998: A Practical Guide to Wavelet
          Analysis.  Bulletin of the American Meteorological Society, 79, 1,
          pp. 61-78.

        """

        gws = self.get_wavelet_var()

        return gws


    def get_wes(self):
        """Calculate Wavelet Energy Spectrum.

        References
        ----------
        Torrence, C., and G. P. Compo, 1998: A Practical Guide to Wavelet
          Analysis.  Bulletin of the American Meteorological Society, 79, 1,
          pp. 61-78.

        """

        from scipy.integrate import trapz

        coef = 1. / (self.motherwavelet.fc * self.motherwavelet.cg)

        wes = coef * trapz(np.power(np.abs(self.coefs), 2), axis = 1);

        return wes

    def get_wps(self):
        """Calculate Wavelet Power Spectrum.

        References
        ----------
        Torrence, C., and G. P. Compo, 1998: A Practical Guide to Wavelet
          Analysis.  Bulletin of the American Meteorological Society, 79, 1,
          pp. 61-78.

        """

        wps =  (1./ self.motherwavelet.len_signal) * self.get_wes()

        return wps

    def get_wavelet_var(self):
        """Calculate Wavelet Variance (a.k.a. the Global Wavelet Spectrum of
        Torrence and Compo (1998)).

        References
        ----------
        Torrence, C., and G. P. Compo, 1998: A Practical Guide to Wavelet
          Analysis.  Bulletin of the American Meteorological Society, 79, 1,
          pp. 61-78.

        """

        coef =  self.motherwavelet.cg * self.motherwavelet.fc

        wvar = (coef / self.motherwavelet.len_signal) * self.get_wes()

        return wvar

    def scalogram(self, show_coi=False, show_wps=False, ts=None, time=None,
                  use_period=True, ylog_base=None, xlog_base=None,
                  origin='top', figname=None):
        """ Scalogram plotting routine.

        Creates a simple scalogram, with optional wavelet power spectrum and
        time series plots of the transformed signal.

        Parameters
        ----------
        show_coi : bool
            Set to True to see Cone of Influence

        show_wps : bool
            Set to True to see the Wavelet Power Spectrum

        ts : array
            1D array containing time series data used in wavelet transform.  If set,
            time series will be plotted.

        time : array of datetime objects
            1D array containing time information

        use_period : bool
            Set to True to see figures use period instead of scale

        ylog_base : float
            If a log scale is desired, set `ylog_base` as float. (for log 10, set
            ylog_base = 10)

        xlog_base : float
            If a log scale is desired, set `xlog_base` as float. (for log 10, set
            xlog_base = 10) *note that this option is only valid for the wavelet power
            spectrum figure.

        origin : 'top' or 'bottom'
            Set origin of scale axis to top or bottom of figure

        Returns
        -------
        None

        Examples
        --------
        Create instance of SDG mother wavelet, normalized, using 10 scales and the
        center frequency of the Fourier transform as the characteristic frequency.
        Then, perform the continuous wavelet transform and plot the scalogram.

        # x = numpy.arange(0,2*numpy.pi,numpy.pi/8.)
        # data = numpy.sin(x**2)
        # scales = numpy.arange(10)
        #
        # mother_wavelet = SDG(len_signal = len(data), scales = np.arange(10), normalize = True, fc = 'center')
        # wavelet = cwt(data, mother_wavelet)
        # wave_coefs.scalogram(origin = 'bottom')

        """

        import matplotlib.pyplot as plt
        import matplotlib.cm as cm
        from pylab import poly_between

        if ts is not None:
            show_ts = True
        else:
            show_ts = False

        if not show_wps and not show_ts:
            # only show scalogram
            figrow = 1
            figcol = 1
        elif show_wps and not show_ts:
            # show scalogram and wps
            figrow = 1
            figcol = 4
        elif not show_wps and show_ts:
            # show scalogram and ts
            figrow = 2
            figcol = 1
        else:
            # show scalogram, wps, and ts
            figrow = 2
            figcol = 4

        if time is None:
            x = np.arange(self.motherwavelet.len_signal)
        else:
            x = time

        if use_period:
            y = self.motherwavelet.scales / self.motherwavelet.fc
        else:
            y = self.motherwavelet.scales

        fig = plt.figure(figsize=(16, 12), dpi=160)
        ax1 = fig.add_subplot(figrow, figcol, 1)

        # if show wps, give 3/4 space to scalogram, 1/4 to wps
        if show_wps:
            # create temp axis at 3 or 4 col of row 1
            axt = fig.add_subplot(figrow, figcol, 3)
            # get location of axtmp and ax1
            axt_pos = axt.get_position()
            ax1_pos = ax1.get_position()
            axt_points = axt_pos.get_points()
            ax1_points = ax1_pos.get_points()
            # set axt_pos left bound to that of ax1
            axt_points[0][0] = ax1_points[0][0]
            ax1.set_position(axt_pos)
            fig.delaxes(axt)

        if show_coi:
            # coi_coef is defined using the assumption that you are using
            #   period, not scale, in plotting - this handles that behavior
            if use_period:
                coi = self.motherwavelet.get_coi() / self.motherwavelet.fc / self.motherwavelet.sampf
            else:
                coi = self.motherwavelet.get_coi()

            coi[coi == 0] = y.min() - 0.1 * y.min()
            xs, ys = poly_between(np.arange(0, len(coi)), np.max(y), coi)
            ax1.fill(xs, ys, 'k', alpha=0.4, zorder = 2)

        contf=ax1.contourf(x,y,np.abs(self.coefs)**2)
        fig.colorbar(contf, ax=ax1, orientation='vertical', format='%2.1f')

        if ylog_base is not None:
            ax1.axes.set_yscale('log', basey=ylog_base)

        if origin is 'top':
            ax1.set_ylim((y[-1], y[0]))
        elif origin is 'bottom':
            ax1.set_ylim((y[0], y[-1]))
        else:
            raise OriginError('`origin` must be set to "top" or "bottom"')

        ax1.set_xlim((x[0], x[-1]))
        ax1.set_title('scalogram')
        ax1.set_ylabel('time')
        if use_period:
            ax1.set_ylabel('period')
            ax1.set_xlabel('time')
        else:
            ax1.set_ylabel('scales')
            if time is not None:
                ax1.set_xlabel('time')
            else:
                ax1.set_xlabel('sample')

        if show_wps:
            ax2 = fig.add_subplot(figrow,figcol,4,sharey=ax1)
            if use_period:
                ax2.plot(self.get_wps(), y, 'k')
            else:
                ax2.plot(self.motherwavelet.fc * self.get_wps(), y, 'k')

            if ylog_base is not None:
                ax2.axes.set_yscale('log', basey=ylog_base)
            if xlog_base is not None:
                ax2.axes.set_xscale('log', basey=xlog_base)
            if origin is 'top':
                ax2.set_ylim((y[-1], y[0]))
            else:
                ax2.set_ylim((y[0], y[-1]))
            if use_period:
                ax2.set_ylabel('period')
            else:
                ax2.set_ylabel('scales')
            ax2.grid()
            ax2.set_title('wavelet power spectrum')

        if show_ts:
            ax3 = fig.add_subplot(figrow, 2, 3, sharex=ax1)
            ax3.plot(x, ts)
            ax3.set_xlim((x[0], x[-1]))
            ax3.legend(['time series'])
            ax3.grid()
            # align time series fig with scalogram fig
            t = ax3.get_position()
            ax3pos=t.get_points()
            ax3pos[1][0]=ax1.get_position().get_points()[1][0]
            t.set_points(ax3pos)
            ax3.set_position(t)
            if (time is not None) or use_period:
                ax3.set_xlabel('time')
            else:
                ax3.set_xlabel('sample')

        if figname is None:
            plt.show()
        else:
            plt.savefig(figname)
            plt.close('all')

def cwt(x, wavelet, weighting_function=lambda x: x**(-0.5), deep_copy=True):
    """Computes the continuous wavelet transform of x using the mother wavelet
    `wavelet`.

    This function computes the continuous wavelet transform of x using an
    instance a mother wavelet object.

    The cwt is defined as:

        T(a,b) = w(a) integral(-inf,inf)(x(t) * psi*{(t-b)/a} dt

    which is a convolution.  In this algorithm, the convolution in the time
    domain is implemented as a multiplication in the Fourier domain.

    Parameters
    ----------
    x : 1D array
        Time series to be transformed by the cwt

    wavelet : Instance of the MotherWavelet class
        Instance of the MotherWavelet class for a particular wavelet family

    weighting_function:  Function used to weight
        Typically w(a) = a^(-0.5) is chosen as it ensures that the
        wavelets at every scale have the same energy.

    deep_copy : bool
        If true (default), the mother wavelet object used in the creation of
        the wavelet object will be fully copied and accessible through
        wavelet.motherwavelet; if false, wavelet.motherwavelet will be a
        reference to the motherwavelet object (that is, if you change the
        mother wavelet object, you will see the changes when accessing the
        mother wavelet through the wavelet object - this is NOT good for
        tracking how the wavelet transform was computed, but setting
        deep_copy to False will save memory).

    Returns
    -------
    Returns an instance of the Wavelet class.  The coefficients of the transform
    can be obtain by the coefs() method (i.e.  wavelet.coefs() )

    Examples
    --------
    Create instance of SDG mother wavelet, normalized, using 10 scales and the
    center frequency of the Fourier transform as the characteristic frequency.
    Then, perform the continuous wavelet transform and plot the scalogram.

    # x = numpy.arange(0,2*numpy.pi,numpy.pi/8.)
    # data = numpy.sin(x**2)
    # scales = numpy.arange(10)
    #
    # mother_wavelet = SDG(len_signal = len(data), scales = np.arange(10), normalize = True, fc = 'center')
    # wavelet = cwt(data, mother_wavelet)
    # wave_coefs.scalogram()

    References
    ----------
    Addison, P. S., 2002: The Illustrated Wavelet Transform Handbook.  Taylor
      and Francis Group, New York/London. 353 pp.

    """

    signal_dtype = x.dtype

    if len(x) < wavelet.len_wavelet:
        n = len(x)
        x = np.resize(x, (wavelet.len_wavelet,))
        x[n:] = 0

    # Transform the signal and mother wavelet into the Fourier domain
    xf=fft(x)
    mwf=fft(wavelet.coefs.conj(), axis=1)

    # Convolve (multiply in Fourier space)
    wt_tmp=ifft(mwf*xf[np.newaxis,:], axis=1)

    # shift output from ifft and multiply by weighting function
    wt = fftshift(wt_tmp,axes=[1]) * weighting_function(wavelet.scales[:, np.newaxis])

    # if mother wavelet and signal are real, only keep real part of transform
    wt=wt.astype(np.lib.common_type(wavelet.coefs, x))

    return Wavelet(wt,wavelet,weighting_function,signal_dtype,deep_copy)

#def ccwt(x1, x2, wavelet):
#    """Compute the continuous cross-wavelet transform of 'x1' and 'x2' using the
#    mother wavelet 'wavelet', which is an instance of the MotherWavelet class.
#
#    Parameters
#    ----------
#    x1,x2 : 1D array
#        Time series used to compute cross-wavelet transform
#
#    wavelet : Instance of the MotherWavelet class
#        Instance of the MotherWavelet class for a particular wavelet family
#
#    Returns
#    -------
#    Returns an instance of the Wavelet class.
#
#    """
#
#    xwt = cwt(x1,wavelet) * np.conjugate(cwt(x2, wavelet))
#
#    return xwt

#def icwt(wavelet):
#    """Compute the inverse continuous wavelet transform.
#
#    Parameters
#    ----------
#    wavelet : Instance of the MotherWavelet class
#        instance of the MotherWavelet class for a particular wavelet family
#
#    Examples
#    --------
#    Use the Morlet mother wavelet to perform wavelet transform on 'data', then
#    use icwt to compute the inverse wavelet transform to come up with an estimate
#    of data ('data2').  Note that data2 is not exactly equal data.
#
#    # import matplotlib.pyplot as plt
#    # from scipy.signal import SDG, Morlet, cwt, icwt, fft, ifft
#    # import numpy as np
#    #
#    # x = np.arange(0,2*np.pi,np.pi/64)
#    # data = np.sin(8*x)
#    # scales=np.arange(0.5,17)
#    #
#    # mother_wavelet = Morlet(len_signal = len(data), scales = scales)
#    # wave_coefs=cwt(data, mother_wavelet)
#    # data2 = icwt(wave_coefs)
#    #
#    # plt.plot(data)
#    # plt.plot(data2)
#    # plt.show()
#
#    References
#    ----------
#    Addison, P. S., 2002: The Illustrated Wavelet Transform Handbook.  Taylor
#      and Francis Group, New York/London. 353 pp.
#
#    """
#    from scipy.integrate import trapz
#
#    # if original wavelet was created using padding, make sure to include
#    #   information that is missing after truncation (see self.coefs under __init__
#    #   in class Wavelet.
#    if wavelet.motherwavelet.len_signal !=  wavelet.motherwavelet.len_wavelet:
#        full_wc = np.c_[wavelet.coefs,wavelet._pad_coefs]
#    else:
#        full_wc = wavelet.coefs
#
#    # get wavelet coefficients and take fft
#    wcf = fft(full_wc,axis=1)
#
#    # get mother wavelet coefficients and take fft
#    mwf = fft(wavelet.motherwavelet.coefs,axis=1)
#
#    # perform inverse continuous wavelet transform and make sure the result is the same type
#    #  (real or complex) as the original data used in the transform
#    x = (1. / wavelet.motherwavelet.cg) *
#        trapz(fftshift(ifft(wcf * mwf,axis=1),axes=[1]) /
#        (wavelet.motherwavelet.scales[:,np.newaxis]**2),
#        dx = 1. / wavelet.motherwavelet.sampf, axis=0)
#
#
#    return x[0:wavelet.motherwavelet.len_signal].astype(wavelet._signal_dtype)

def scalogram(scales, data, show_coi=False, show_wps=False, ts=None, time=None,
                  use_period=False, ylog_base=None, xlog_base=None,
                  origin='top', figname=None):
        """ Scalogram plotting routine.

        Creates a simple scalogram, with optional wavelet power spectrum and
        time series plots of the transformed signal.

        Parameters
        ----------
        show_coi : bool
            Set to True to see Cone of Influence

        show_wps : bool
            Set to True to see the Wavelet Power Spectrum

        ts : array
            1D array containing time series data used in wavelet transform.  If set,
            time series will be plotted.

        time : array of datetime objects
            1D array containing time information

        use_period : bool
            Set to True to see figures use period instead of scale

        ylog_base : float
            If a log scale is desired, set `ylog_base` as float. (for log 10, set
            ylog_base = 10)

        xlog_base : float
            If a log scale is desired, set `xlog_base` as float. (for log 10, set
            xlog_base = 10) *note that this option is only valid for the wavelet power
            spectrum figure.

        origin : 'top' or 'bottom'
            Set origin of scale axis to top or bottom of figure

        Returns
        -------
        None

        Examples
        --------
        Create instance of SDG mother wavelet, normalized, using 10 scales and the
        center frequency of the Fourier transform as the characteristic frequency.
        Then, perform the continuous wavelet transform and plot the scalogram.

        # x = numpy.arange(0,2*numpy.pi,numpy.pi/8.)
        # data = numpy.sin(x**2)
        # scales = numpy.arange(10)
        #
        # mother_wavelet = SDG(len_signal = len(data), scales = np.arange(10), normalize = True, fc = 'center')
        # wavelet = cwt(data, mother_wavelet)
        # wave_coefs.scalogram(origin = 'bottom')

        """

        import matplotlib.pyplot as plt
        import matplotlib.cm as cm
        from pylab import poly_between

        if ts is not None:
            show_ts = True
        else:
            show_ts = False

        if not show_wps and not show_ts:
            # only show scalogram
            figrow = 1
            figcol = 1
        elif show_wps and not show_ts:
            # show scalogram and wps
            figrow = 1
            figcol = 4
        elif not show_wps and show_ts:
            # show scalogram and ts
            figrow = 2
            figcol = 1
        else:
            # show scalogram, wps, and ts
            figrow = 2
            figcol = 4

        if time is None:
#            x = np.arange(self.motherwavelet.len_signal)
#            x = np.arange(len(data))
            x = np.arange(len(data[0]))
        else:
            x = time

        if use_period:
            pass
#            y = self.motherwavelet.scales / self.motherwavelet.fc
        else:
#            y = self.motherwavelet.scales
            y = scales

#        fig = plt.figure(figsize=(16, 12), dpi=160)
        fig = plt.figure()
        ax1 = fig.add_subplot(figrow, figcol, 1)

        # if show wps, give 3/4 space to scalogram, 1/4 to wps
        if show_wps:
            # create temp axis at 3 or 4 col of row 1
            axt = fig.add_subplot(figrow, figcol, 3)
            # get location of axtmp and ax1
            axt_pos = axt.get_position()
            ax1_pos = ax1.get_position()
            axt_points = axt_pos.get_points()
            ax1_points = ax1_pos.get_points()
            # set axt_pos left bound to that of ax1
            axt_points[0][0] = ax1_points[0][0]
            ax1.set_position(axt_pos)
            fig.delaxes(axt)

#        if show_coi:
#            # coi_coef is defined using the assumption that you are using
#            #   period, not scale, in plotting - this handles that behavior
#            if use_period:
#                coi = self.motherwavelet.get_coi() / self.motherwavelet.fc / self.motherwavelet.sampf
#            else:
#                coi = self.motherwavelet.get_coi()
#
#            coi[coi == 0] = y.min() - 0.1 * y.min()
#            xs, ys = poly_between(np.arange(0, len(coi)), np.max(y), coi)
#            ax1.fill(xs, ys, 'k', alpha=0.4, zorder = 2)

#        contf=ax1.contourf(x,y,np.abs(self.coefs)**2)
#        contf=ax1.contourf(x,y,np.abs(data)**2)
        contf=ax1.contourf(x,y,np.abs(data))
#        fig.colorbar(contf, ax=ax1, orientation='vertical', format='%2.1f')

        if ylog_base is not None:
            ax1.axes.set_yscale('log', basey=ylog_base)

        if origin is 'top':
            ax1.set_ylim((y[-1], y[0]))
        elif origin is 'bottom':
            ax1.set_ylim((y[0], y[-1]))
        else:
            raise OriginError('`origin` must be set to "top" or "bottom"')

        ax1.set_xlim((x[0], x[-1]))
#        ax1.set_title('scalogram')
        ax1.set_ylabel('time')
        if use_period:
            ax1.set_ylabel('period')
            ax1.set_xlabel('time')
        else:
            ax1.set_ylabel('scales')
            if time is not None:
                ax1.set_xlabel('time')
            else:
                ax1.set_xlabel('sample')

        if show_wps:
            ax2 = fig.add_subplot(figrow,figcol,4,sharey=ax1)
            if use_period:
                ax2.plot(self.get_wps(), y, 'k')
            else:
                ax2.plot(self.motherwavelet.fc * self.get_wps(), y, 'k')

            if ylog_base is not None:
                ax2.axes.set_yscale('log', basey=ylog_base)
            if xlog_base is not None:
                ax2.axes.set_xscale('log', basey=xlog_base)
            if origin is 'top':
                ax2.set_ylim((y[-1], y[0]))
            else:
                ax2.set_ylim((y[0], y[-1]))
            if use_period:
                ax2.set_ylabel('period')
            else:
                ax2.set_ylabel('scales')
            ax2.grid()
            ax2.set_title('wavelet power spectrum')

        if show_ts:
            ax3 = fig.add_subplot(figrow, 2, 3, sharex=ax1)
            ax3.plot(x, ts)
            ax3.set_xlim((x[0], x[-1]))
            ax3.legend(['time series'])
            ax3.grid()
            # align time series fig with scalogram fig
            t = ax3.get_position()
            ax3pos=t.get_points()
            ax3pos[1][0]=ax1.get_position().get_points()[1][0]
            t.set_points(ax3pos)
            ax3.set_position(t)
            if (time is not None) or use_period:
                ax3.set_xlabel('time')
            else:
                ax3.set_xlabel('sample')

        if figname is None:
            plt.show()
        else:
            plt.savefig(figname)
            plt.close('all')

#class arr(object):
#    @staticmethod
#    def mylog2(x):
#        lx = 0
#        while x > 1:
#            x >>= 1
#            lx += 1
#        return lx
#    def __init__(self, array):
#        self.array = array
#    def __getitem__(self, index):
#        return self.array[arr.mylog2(index+1)]
#    def __len__(self):
#        return 1 << len(self.array)

import pywt

data = np.array([ 22.9, 13.8, 31.4, 30.1, 31.8, 31.0, 18.3, 23.8, 31.6, 18.9
, 18.8, 31.8, 31.1, 27.0, 23.0, 19.9, 21.5, 23.8, 22.8, 24.8
, 20.4, 25.8, 24.3, 22.9, 23.2, 23.8, 19.2, 18.2, 14.5, 22.6
, 20.1, 18.6, 24.9, 25.2, 30.1, 29.4, 23.3, 20.4, 17.6, 14.7
, 24.5, 32.4, 32.0, 33.4, 37.3, 36.7, 31.3, 26.6, 23.8, 21.9
, 26.9, 25.0, 25.8, 30.5, 25.1, 21.7, 20.7, 21.2, 22.4, 24.2
, 25.8, 29.1, 35.6, 32.2, 29.9, 30.5, 32.6, 29.0, 33.2, 35.4
, 32.8, 27.4, 25.3, 27.6, 29.3, 26.7, 24.5, 23.2, 30.7, 26.5
, 23.9, 24.6, 24.4, 28.1, 26.0, 27.3, 27.7, 27.7, 27.0, 24.2
, 26.3, 25.7, 25.3, 27.9, 27.5, 25.0, 23.6, 31.6, 35.7, 35.2
, 38.8, 31.2, 32.5, 32.0, 33.1, 31.8, 35.0, 27.7, 31.1, 26.7
, 30.9, 38.7, 41.8, 45.6, 36.0, 38.5, 46.1, 46.0, 42.5, 35.3
, 36.8, 33.2, 34.5, 39.5, 38.7, 32.5, 33.0, 33.0, 30.9, 30.7
, 37.0, 36.8, 34.7, 35.7, 31.7, 32.0, 37.9, 42.4, 38.2, 35.3
, 38.4, 40.9, 39.1, 34.1, 41.9, 32.1, 41.9, 45.7, 56.5, 49.4
, 46.3, 50.9, 47.1, 50.9, 53.9, 50.9, 45.9, 43.1, 45.0, 48.3
, 48.6, 40.9, 41.6, 45.7, 40.6, 40.6, 37.0, 36.1, 33.9, 32.1
, 34.1, 34.2, 41.9, 39.8, 35.1, 31.9, 34.9, 39.8, 39.0, 42.9
, 44.4, 42.7, 45.2, 41.0, 37.0, 37.5, 41.0, 45.0, 47.9, 56.5
, 55.6, 54.2, 52.5, 52.4, 44.9, 40.9, 41.1, 44.8, 46.7, 49.4])

def wv():
    decomposition_level = 3
    wavelet_families = pywt.families()
    wavelet_family = wavelet_families[0]
    selected_wavelet = pywt.wavelist(wavelet_family)[0]

    wavelet = pywt.Wavelet(selected_wavelet)
    wCoefficients_Stationary = pywt.swt(data, wavelet, level=decomposition_level)
    return wCoefficients_Stationary

#    ax = plt.subplot(111)
#    ax.yaxis.set_ticks([2,1,0])
#    plt.axis([1, 100, 1, 4])
#    plt.imshow(wCoefficients_Stationary[0], interpolation='nearest')
#    plt.imshow(wCoefficients_Stationary[2], interpolation='nearest')
#
#    plt.show()

def main():
    x = np.arange(0,2*np.pi,np.pi/8.)
#    data = np.sin(x**2)
    from stats.wavelets import select_levels_from_swt, update_selected_levels_swt
    coeffs = select_levels_from_swt(wv())
    res = update_selected_levels_swt(wv(), coeffs)

#    scalogram(scales=np.arange(2), data=wv()[0])       #NB: scales == matrix rows (levels)
#    scalogram(scales=np.arange(6), data=np.vstack(wv()))    #NB: vstack piles all (n = 3 ~ v = 6), should extract coeffs manually
    scalogram(scales=np.arange(len(coeffs)), data=coeffs)
    pass

#    mother_wavelet = SDG(len_signal = len(data), scales = np.arange(5),normalize = True, fc = 'center')
#    wavelet = cwt(data, mother_wavelet)
#    wavelet.scalogram(show_coi=False, show_wps=True, use_period=False, ts=data)

#    test_array = np.array([[1.,2.,3.,4.,5.,6.,7.,8.,9.], [1.,2.,3.,4.,5.,6.,7.,8.,9.], [1.,2.,3.,4.,5.,6.,7.,8.,90.]])
#    test_array = np.array([1.,2.,3.,4.,5.,6.,7.,8.,9.])
#    local_reference_to_array = arr(test_array)
#
#    ax = plt.subplot(111)
#    ax.yaxis.set_ticks([16, 8, 4, 2, 1, 0])
#    plt.axis([-0.5, 4.5, 31.5, 0.5])
#    plt.imshow(local_reference_to_array, interpolation="nearest")
#    plt.imshow(test_array, interpolation="nearest")

#    plt.show()
    
#    import numpy as np
#    from scipy.signal import SDG, Morlet, cwt
#
#    # create data array - number of tropical cyclones per year (1970-2006) in the
#    #   Northwest Australian region
#    data = np.array([5,6,8,8,11,6,4,4,2,6,7,9,4,8,10,8,4,14,5,5,2,2,7,3,7,5,5,7,9,5,3,6,5,5,7])
#
#    # remove mean
#    data = (data - data.mean())
#
#    # create the scales at which you wish to do the analysis
#    scales = np.arange(1,15,0.1)
#
#    # initialize the mother wavelet
#    mother_wavelet = SDG(len_signal = len(data), pad_to = np.power(2,10),
#    scales = scales)
#
#    # perform continuous wavelet transform on `data` using `mother_wavelet`
#    wavelet=cwt(data, mother_wavelet)
#
#    # plot scalogram, wavelet power spectrum, and time series
#    wavelet.scalogram(ts = data, show_coi = True, show_wps = True,
#    use_period = True, ylog_base = 2)

if __name__ == '__main__':
    main()
#    wv()