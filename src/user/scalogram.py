# -*- coding=utf-8 -*-
__author__ = 'Yadavito'


# external #
import matplotlib.pyplot as plt
import numpy as np

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

class arr(object):
    @staticmethod
    def mylog2(x):
        lx = 0
        while x > 1:
            x >>= 1
            lx += 1
        return lx
    def __init__(self, array):
        self.array = array
    def __getitem__(self, index):
        return self.array[arr.mylog2(index+1)]
    def __len__(self):
        return 1 << len(self.array)

def main():
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
    
    import numpy as np
    from scipy.signal import SDG, Morlet, cwt

    # create data array - number of tropical cyclones per year (1970-2006) in the
    #   Northwest Australian region
    data = np.array([5,6,8,8,11,6,4,4,2,6,7,9,4,8,10,8,4,14,5,5,2,2,7,3,7,5,5,7,9,5,3,6,5,5,7])

    # remove mean
    data = (data - data.mean())

    # create the scales at which you wish to do the analysis
    scales = np.arange(1,15,0.1)

    # initialize the mother wavelet
    mother_wavelet = SDG(len_signal = len(data), pad_to = np.power(2,10),
    scales = scales)

    # perform continuous wavelet transform on `data` using `mother_wavelet`
    wavelet=cwt(data, mother_wavelet)

    # plot scalogram, wavelet power spectrum, and time series
    wavelet.scalogram(ts = data, show_coi = True, show_wps = True,
    use_period = True, ylog_base = 2)

if __name__ == '__main__':
    main()