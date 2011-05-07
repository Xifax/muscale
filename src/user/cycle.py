# -*- coding: utf-8 -*-
from numpy.lib.function_base import append

__author__ = 'Yadavito'

# external #
from stats.pyper import R, Str4R
import pywt
import matplotlib.pyplot as plt

# own #
from stats.wavelets import iswt
from user.test import test_data

def modelling_cycle():

    initial_data = test_data

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

    fig_stat_sum = plt.figure(); n_coeff = 1
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