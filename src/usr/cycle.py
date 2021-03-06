# -*- coding: utf-8 -*-
from numpy.lib.function_base import append

__author__ = 'Yadavito'

# external #
from stats.pyper import R, Str4R
import pywt
import matplotlib.pyplot as plt

# own #
from stats.wavelets import iswt, \
    select_levels_from_swt, update_selected_levels_swt, \
    select_node_levels_from_swt, update_node_levels_swt, update_swt, \
    measure_threshold, apply_threshold
from stats.models import *
from usr.test import test_data, test_data_one

def plot_initial_updated(initial_data, updated_data, matrix=False):
    init_fig = plt.figure(); n_coeff = 1
    init_fig.canvas.manager.set_window_title('Initial data')
    for dyad in initial_data:
        init_fig.add_subplot(len(initial_data) * 2, 1, n_coeff); n_coeff += 1
        plt.plot(dyad[0])
        init_fig.add_subplot(len(initial_data) * 2, 1, n_coeff); n_coeff += 1
        plt.plot(dyad[1])

    upd_fig = plt.figure(); n_coeff = 1
    upd_fig.canvas.manager.set_window_title('Updated data')

    if not matrix:
        for dyad in updated_data:
            upd_fig.add_subplot(len(updated_data) * 2, 1, n_coeff); n_coeff += 1
            plt.plot(dyad[0])
            upd_fig.add_subplot(len(updated_data) * 2, 1, n_coeff); n_coeff += 1
            plt.plot(dyad[1])
    else:
        for level in updated_data:
            upd_fig.add_subplot(len(updated_data), 1, n_coeff); n_coeff += 1
            plt.plot(level)

    plt.show()

def modelling_cycle():

#--------------- initialization -------------------#
#    initial_data = test_data
    initial_data = test_data_one

#    fig_init = plt.figure()
#    fig_init.canvas.manager.set_window_title('Initial data')
#    plt.plot(initial_data, color='g')

    wavelet_families = pywt.families()
    print 'Wavelet families:', ', '.join(wavelet_families)
    wavelet_family = wavelet_families[4]
    selected_wavelet = pywt.wavelist(wavelet_family)[0]
    wavelet = pywt.Wavelet(selected_wavelet)
    print 'Selected wavelet:', selected_wavelet

    max_level = pywt.swt_max_level(len(initial_data))
#    decomposition_level = max_level / 2
    decomposition_level = 3
    print 'Max level:', max_level, '\t Decomposition level:', decomposition_level

#--------------- decomposition -------------------#
    w_initial_coefficients = pywt.swt(initial_data, wavelet, level=decomposition_level)
    w_selected_coefficiets = select_levels_from_swt(w_initial_coefficients)
    w_node_coefficients = select_node_levels_from_swt(w_initial_coefficients)      #something terribly wrong here, yet the rest works!

#------------------ threshold --------------------#

    threshold = measure_threshold(w_initial_coefficients)

    w_threshold_coeff = w_initial_coefficients[:]
    apply_threshold(w_threshold_coeff)
    plot_initial_updated(w_initial_coefficients, w_threshold_coeff)

#    plt.figure()
#    for coeff in w_selected_coefficiets:
#        plt.plot(coeff)
#    plt.figure()
#    for coeff in w_node_coefficients:
#        plt.plot(coeff)
#    plt.show()

#--------------- modification -------------------#
    r = R()

    w_new_coefficients = [0] * len(w_selected_coefficiets)
    for index in range(0, len(w_selected_coefficiets)):
        r.i_data = w_selected_coefficiets[index]

        r('hw <- HoltWinters( ts(i_data, frequency = 12), gamma = TRUE )')
        r('pred <- predict(hw, 50, prediction.interval = TRUE)')

        w_new_coefficients[index] = append(w_selected_coefficiets[index], r.pred[:,0])
        index += 1

    w_new_node_coefficients = [0] * len(w_node_coefficients)
    for index in range(0, len(w_node_coefficients)):
        r.i_data = w_node_coefficients[index]

        r('hw <- HoltWinters( ts(i_data, frequency = 12), gamma = TRUE )')
        r('pred <- predict(hw, 50, prediction.interval = TRUE)')

        w_new_node_coefficients[index] = append(w_node_coefficients[index], r.pred[:,0])
        index += 1
#----

#    plt.figure()
#    for coeff in w_new_coefficients:
#        plt.plot(coeff)
#    plt.figure()
#    for coeff in w_new_node_coefficients:
#        plt.plot(coeff)
#    plt.show()

#--------------- reconstruction  -------------------#
#    wInitialwithUpdated_Nodes = update_node_levels_swt(w_initial_coefficients, w_new_node_coefficients)

#    plot_initial_updated(w_initial_coefficients, w_new_node_coefficients, True)
#    plot_initial_updated(w_initial_coefficients, wInitialwithUpdated_Nodes) (!)

#    plt.figure()
#    for dyad in wInitialwithUpdated_Nodes:
#        plt.plot(dyad[0])
#        plt.plot(dyad[1])
#
#    plt.figure()
#    for dyad in w_initial_coefficients:
#        plt.plot(dyad[0])
#        plt.plot(dyad[1])
#
#    plt.show()

#    w_updated_coefficients = update_selected_levels_swt(w_initial_coefficients, w_selected_coefficiets)
#    w_updated_coefficients = update_selected_levels_swt(w_initial_coefficients, w_new_coefficients)


#----
#    w_updated_coefficients = update_swt(w_initial_coefficients, w_selected_coefficiets, w_node_coefficients)

    w_updated_coefficients_nodes = update_swt(w_initial_coefficients, w_new_coefficients, w_new_node_coefficients)
    w_updated_coefficients = update_selected_levels_swt(w_initial_coefficients, w_new_coefficients)

    plot_initial_updated(w_initial_coefficients, w_updated_coefficients_nodes)
    plot_initial_updated(w_initial_coefficients, w_updated_coefficients)

    reconstructed_Stationary_nodes = iswt(w_updated_coefficients_nodes, selected_wavelet)
    reconstructed_Stationary = iswt(w_updated_coefficients, selected_wavelet)

    fig_sta_r = plt.figure()
    fig_sta_r.canvas.manager.set_window_title('SWT reconstruction')
    plt.plot(reconstructed_Stationary)

    fig_sta_r_n = plt.figure()
    fig_sta_r_n.canvas.manager.set_window_title('SWT reconstruction (nodes)')
    plt.plot(reconstructed_Stationary_nodes)

    plt.show()

def __modelling_cycle():

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