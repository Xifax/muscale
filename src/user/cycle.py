# -*- coding: utf-8 -*-
from numpy.lib.function_base import append

__author__ = 'Yadavito'

# external #
from stats.pyper import R, Str4R
import pywt
#from numpy import *
import matplotlib.pyplot as plt

# own #
from stats.wavelets import iswt

def modelling_cycle():

    initial_data = [ 22.9, 13.8, 31.4, 30.1, 31.8, 31.0, 18.3, 23.8, 31.6, 18.9
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
, 55.6, 54.2, 52.5, 52.4, 44.9, 40.9, 41.1, 44.8, 46.7, 49.4]

    fig_init = plt.figure()
    fig_init.canvas.manager.set_window_title('Initial data')
    plt.plot(initial_data, color='g')
#--------------- wavelet decomposition -------------------#
    decomposition_level = 2
    wavelet_families = pywt.families()
    wavelet_family = wavelet_families[0]
    selected_wavelet = pywt.wavelist(wavelet_family)[0]

    wavelet = pywt.Wavelet(selected_wavelet)  #NB: taking first variant of wavelet (e.g. haar1)
    # discrete (non stationary) multilevel decomposition
    wCoefficients_Discrete = pywt.wavedec(initial_data, wavelet, level=decomposition_level) #NB: output length also depends on wavelet type
    # stationary (Algorithme à trous ~ does not decimate coefficients at every transformation level) multilevel decomposition
    wCoefficients_Stationary = pywt.swt(initial_data, wavelet, level=decomposition_level)

    fig_discrete = plt.figure(); n_coeff = 1
    fig_discrete.canvas.manager.set_window_title('Discrete decomposition [ ' + str(decomposition_level) + ' level(s) ]') 
    for coeff in wCoefficients_Discrete:
#        print coeff
        fig_discrete.add_subplot(len(wCoefficients_Discrete), 1, n_coeff); n_coeff += 1
        plt.plot(coeff)

    fig_stationary = plt.figure(); n_coeff = 1; rows = 0
    fig_stationary.canvas.manager.set_window_title('Stationary decomposition [ ' + str(decomposition_level) + ' level(s) ]')
    for item in wCoefficients_Stationary: rows += len(item)
    i = 0; j = 0    # tree coeffs
    for coeff in wCoefficients_Stationary:
        for subcoeff in coeff:
            print i, j
#            print subcoeff
            fig_stationary.add_subplot(rows, 1, n_coeff); n_coeff += 1
            plt.plot(subcoeff)
            j += 1
        i += 1

    plt.show()

    fig_stat_sum = plt.figure(); n_coeff = 1; rows = 0
    fig_stat_sum.canvas.manager.set_window_title('SWT sum by levels [ ' + str(decomposition_level) + ' level(s) ]')
    for coeff in wCoefficients_Stationary:
        sum = coeff[0] + coeff[1]
        fig_stat_sum.add_subplot(len(wCoefficients_Discrete), 1, n_coeff); n_coeff += 1
        plt.plot(sum)
        
#    plt.show()

#------------------ modelling by level -------------------#

    r = R()
    r.i_data = initial_data     # or r['i_data'] = initial_data

    ### Holt-Winters ###
    # non-seasonal Holt-Winters
    print r('hw <- HoltWinters( i_data, gamma = FALSE )')

    # seasonal Holt-Winters
    r.freq = 4  #series sampling (month, days, years, etc)
#    print r( 'hw <- HoltWinters( ts ( %s, frequency = %s ) )' % ( Str4R(r.i_data), Str4R(r.freq) ) )
#    print r( 'hw <- HoltWinters( ts ( %s, frequency = %s, start = c(1,1) ) )' % ( Str4R(r.i_data), Str4R(r.freq) ) )

    # resulting Square Estimation Sum
    print r.hw['SSE']

    # bruteforce frequency search
#    print 'test ahead:'
#    sse_dict = {}
#    for i in xrange(2, 50):
#        r.freq = i
##        r( 'hw <- HoltWinters( ts ( %s, frequency = %s, start = c(1,1) ) )' % ( Str4R(r.i_data), Str4R(r.freq) ) )
#        r( 'hw <- HoltWinters( ts ( %s, frequency = %s ) )' % ( Str4R(r.i_data), Str4R(r.freq) ) )
#        print r.hw['SSE']
#        sse_dict[r.hw['SSE']] = i; i += 1
#    print 'Resulting:'
#    m = min(sse_dict.keys())
#    print sse_dict[m], m

    fig = plt.figure()
    fig.canvas.manager.set_window_title('Holt-winters model')
    ax = fig.add_subplot(111)
#    ax.plot(r.hw['fitted'][:,0])   # the colums are: xhat, level, trend
#    plt.show()

    # forecast length
    r.steps_ahead = 50
#    print r('pred <- predict(%s, %s, prediction.interval = TRUE)' % ( Str4R(r.hw), Str4R(r.steps_ahead)) )
#    print r( 'pred <- predict(hw, %s, prediction.interval = TRUE)', Str4R(r.steps_ahead) )
    print r( 'pred <- predict(hw, 50, prediction.interval = TRUE)')
#    plt.plot(r.pred)
    ax.plot(initial_data)
    ax.plot(append(r.hw['fitted'][:,0], r.pred[:,0]))   # concatenating reconstructed model and resulting forecast

#    plt.show()

#------------------ reconstruction -------------------#
    # multilevel idwt
    reconstructed_Discrete = pywt.waverec(wCoefficients_Discrete, selected_wavelet)
    fig_dis_r = plt.figure()
    fig_dis_r.canvas.manager.set_window_title('DWT reconstruction')
    plt.plot(reconstructed_Discrete)
#    plt.show()

    # multilevel stationary
    reconstructed_Stationary = iswt(wCoefficients_Stationary, selected_wavelet)

    fig_sta_r = plt.figure()
    fig_sta_r.canvas.manager.set_window_title('SWT reconstruction')
    plt.plot(reconstructed_Stationary)
    plt.show()
    print 'end'

if __name__ == '__main__':
    try:
        modelling_cycle()
    except Exception, e:
        print e