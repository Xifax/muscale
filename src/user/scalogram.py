# -*- coding=utf-8 -*-
__author__ = 'Yadavito'


# external #
import matplotlib.pyplot as plt
import numpy as np

def scalogram(scales, data, show_coi=False, show_wps=False, ts=None, time=None,
                  use_period=False, ylog_base=None, xlog_base=None,
                  origin='top', figname=None):

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