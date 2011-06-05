# -*- coding: utf-8 -*-
__author__ = 'Michael Marino, Yadavito'

# internal #
import math
import re
import collections

# external #
import pywt
import numpy
import matplotlib.pyplot as plt
from numpy import array, vstack, zeros, copy

# own #
from utility.const import RES, WV, LINE_WITH
from stats.models import entropy

def apply_threshold(output, scaler=1., input=None):
    """
        output
          approx and detail coefficients, arranged in level value
          exactly as output from swt:
          e.g. [(cA1, cD1), (cA2, cD2), ..., (cAn, cDn)]
        scaler
          float to allow runtime tuning of thresholding
        input
          vector with length len(output).  If not None, these values are used for thresholding
          if None, then the vector applies a calculation to estimate the proper thresholding
          given this waveform.
    """
    for j in range(len(output)):
        cA, cD = output[j]
        if input is None:
            dev = numpy.median(numpy.abs(cD - numpy.median(cD)))/0.6745
            thresh = math.sqrt(2*math.log(len(cD)))*dev*scaler
        else: thresh = scaler*input[j]
        cD = pywt.thresholding.hard(cD, thresh)
        output[j] = (cA, cD)

def measure_threshold(output, scaler=1.):
    """
        output
          approx and detail coefficients, arranged in level value
          exactly as output from swt:
          e.g. [(cA1, cD1), (cA2, cD2), ..., (cAn, cDn)]
        scaler
          float to allow runtime tuning of thresholding
        returns vector of length len(output) with treshold values
    """
    measure = []
    for j in range(len(output)):
        cA, cD = output[j]
        dev = numpy.median(numpy.abs(cD - numpy.median(cD)))/0.6745
        thresh = math.sqrt(2*math.log(len(cD)))*dev*scaler
        measure.append(thresh)
    return measure 

## Inverse Stationary Wavelet Transform.
#  @param coefficients Wavelet coefficients in tuples arrangement.
#  @param wavelet Wavelet used in initial SWT.
#  @return Reconstructed data.
def iswt(coefficients, wavelet):
    """
      Input parameters:

        coefficients
          approx and detail coefficients, arranged in level value
          exactly as output from swt:
          e.g. [(cA1, cD1), (cA2, cD2), ..., (cAn, cDn)]

        wavelet
          Either the name of a wavelet or a Wavelet object

    """
    output = coefficients[0][0].copy() # Avoid modification of input data

    #num_levels, equivalent to the decomposition level, n
    num_levels = len(coefficients)
    for j in range(num_levels,0,-1):
        step_size = int(math.pow(2, j-1))
        last_index = step_size
        _, cD = coefficients[num_levels - j]
        for first in range(last_index): # 0 to last_index - 1

            # Getting the indices that we will transform
            indices = numpy.arange(first, len(cD), step_size)

            # select the even indices
            even_indices = indices[0::2]
            # select the odd indices
            odd_indices = indices[1::2]

            # perform the inverse dwt on the selected indices,
            # making sure to use periodic boundary conditions
            x1 = pywt.idwt(output[even_indices], cD[even_indices], wavelet, 'per')
            x2 = pywt.idwt(output[odd_indices], cD[odd_indices], wavelet, 'per')

            # perform a circular shift right
            x2 = numpy.roll(x2, 1)

            # checking x1,x2 shapes
            if len(x1) != len(x2):
                new_length = max(len(x1), len(x2))
                _x1, _x2 = copy(x1), copy(x2)
                _x1.resize(new_length, refcheck = False)
                _x2.resize(new_length, refcheck = False)
            else:
                _x1, _x2 = x1, x2

            # average and insert into the correct indices
            output[indices] = (_x1 + _x2)/2.

    return output

## Selects node coefficients from initial SWT.
#  @param coeffs SWT coefficients as list of (Aa, Ab), ... tuples.
#  @return Node coefficients in matrix.
def select_node_levels_from_swt(coeffs):
    # rearrange coeffs tuples into matrix
    by_rows = vstack(coeffs)
    # pre-allocating rearranged matrix
    nodes = zeros(shape = (len(by_rows)/2 + 1, len(by_rows[0])))
    # selecting node coefficients (starting with 2nd node)
    index = len(by_rows) - 2; r_index = 0
    while True:
        if index > 1:
            nodes[r_index] = by_rows[index]
            index -= 2
        else: break
        r_index += 1

    return nodes

## Rearranges coefficients resulting from SWT for optimal use.
#  @param coeffs SWT coefficients as list of (Aa, Ab), ... tuples.
#  @return Selected coefficients in matrix.
def select_levels_from_swt(coeffs):
    '''Selects appropriate levels from resulting WT coeff tree
        For SWT in pyWavelets:
                 0
                /  \
             {0} <- {1} <- last levels
             / \
        {0,0}  {0,1) <- penultimate
        /   \
        .....   <- first

        May also go backwards, conceptually not important
        N.B: coeffs should be in pywt [ [( ) , ( )], ... ] format
    '''
    # rearrange coeffs tuples into matrix
    by_rows = vstack(coeffs)
    # pre-allocating rearranged matrix
    rearranged = zeros(shape = (len(by_rows)/2 + 1, len(by_rows[0])))
    # inserting row by row (more effective than iterative appending)
    index = len(by_rows) - 1; r_index = 0
    while True:
        if index > 1:
            rearranged[r_index] = by_rows[index]
            index -= 2
        elif index >= 0:
            # inserting two last levels
            rearranged[r_index] = by_rows[index]
            index -= 1
        else: break
        r_index += 1

    return rearranged

## Reconstructs coefficients list based on initial and updated data.
#  @param inital_coeffs Data right after SWT.
#  @param selected_coeffs Updated data in matrix.
#  @return All coefficients in list of tuples.
def update_selected_levels_swt(initial_coeffs, selected_coeffs):
    '''Restores tree structure for further ISWT'''
    # resulting max dimension
    new_dimension = calculate_new_dimension(initial_coeffs, selected_coeffs)
        
    # rearranging back to how it was
    by_rows = vstack(copy(initial_coeffs))
    by_rows.resize(len(by_rows), new_dimension, refcheck = False)
    new_coeffs = copy_non_uniform_shape(selected_coeffs)
    new_coeffs.resize(len(new_coeffs), new_dimension, refcheck = False)

    index = len(by_rows) - 1; s_index = 0
    while True:
        if index > 1:
            by_rows[index] = new_coeffs[s_index]
            index -= 2
        elif index >= 0:
            by_rows[index] = new_coeffs[s_index]
            index -= 1
        else: break
        s_index += 1
    # tupling and listing
    all_of_coeffs = []; element = 0
    while element <= len(by_rows) - 2:
        all_of_coeffs.append((copy(by_rows[element]),  copy(by_rows[element + 1])))
        element += 2
    return all_of_coeffs

## Updates initial coefficients with new data from nodes only.
#  @param inital_coeffs Data right after SWT.
#  @param selected_coeffs Updated node coefficients in matrix.
#  @return All coefficients in list of tuples.
def update_node_levels_swt(initial_coeffs, node_coeffs):
    new_dimension = calculate_new_dimension(initial_coeffs, node_coeffs)

    # rearranging back to how it was
    by_rows = vstack(copy(initial_coeffs))
    by_rows.resize(len(by_rows), new_dimension, refcheck = False)
    new_coeffs = copy_non_uniform_shape(node_coeffs)
    new_coeffs.resize(len(new_coeffs), new_dimension, refcheck = False)

    index = len(by_rows) - 2; s_index = 0
    while True:
        if index > 1:
            by_rows[index] = new_coeffs[s_index]
            index -= 2
        else: break
        s_index += 1
    # tupling and listing
    all_of_coeffs = []; element = 0
    while element <= len(by_rows) - 2:
        all_of_coeffs.append((copy(by_rows[element]),  copy(by_rows[element + 1])))
        element += 2
    return all_of_coeffs

## Reconstructs coefficients list based on initial data, selected coefficients plus updated nodes
def update_swt(initial_coeffs, selected_coeffs, updated_nodes):
    new_dimension = calculate_new_dimension(initial_coeffs, selected_coeffs)

    by_rows = vstack(copy(initial_coeffs))
    by_rows.resize(len(by_rows), new_dimension, refcheck = False)

    new_coeffs = copy_non_uniform_shape(selected_coeffs)
    new_coeffs.resize(len(selected_coeffs), new_dimension, refcheck = False)

    new_nodes = copy_non_uniform_shape(updated_nodes)
    new_nodes.resize(len(updated_nodes), new_dimension, refcheck = False)

    index = len(by_rows) - 1; sel_index = 0; nodes_index = 0
    while True:
        if index > 1:
            by_rows[index] = new_coeffs[sel_index]
            index -= 1
            by_rows[index] = new_nodes[nodes_index]
            index -= 1
            sel_index += 1
            nodes_index += 1
        elif index >= 0:
            by_rows[index] = new_coeffs[sel_index]
            sel_index += 1
            index -= 1
        else: break

    all_of_the_coeffs = []; element = 0
    # total items (in dyads) count - 1 (first in dyad) - 1 (counting from zero)
    while element <= len(by_rows) - 2:
        all_of_the_coeffs.append((copy(by_rows[element]),  copy(by_rows[element + 1])))
        element += 2
    return all_of_the_coeffs

## Calculates new horizontal dimension for resulting data.
#  @param initial_data Source data.
#  @param new_data Partially updated data.
#  @return Appropriate horizontal matrix/array dimension.
def calculate_new_dimension(initial_data, new_data):
    # resulting max dimension
    try:
        new_dimension = max(len(a) for a in new_data if not isinstance(a, int))
    except Exception:
        if len(new_data) > 0:
            new_dimension = len(new_data)
        else:
            new_dimension = len(initial_data[0][0])

    old_dimension = len(initial_data[0][0])    # first array in first tuple in list
    if new_dimension < old_dimension:
        new_dimension = old_dimension

    return new_dimension

## Copies list of arrays reshaping it to maximum possible dimension.
#  @param coeffs Values in list of arrays.
#  @return Copy of initial values in matrix.
def copy_non_uniform_shape(coeffs):
    '''Copy array resizing to uniform shape'''
    try:
        dimension = max(len(a) for a in coeffs if not isinstance(a, int))
    except Exception:
        dimension = len(coeffs)
    new_coeffs = zeros(shape=(len(coeffs), dimension)); i = 0
    for element in coeffs:
        new_element = array(element, copy = True)
        new_element.resize(dimension, refcheck = False)
        if isinstance(new_element, str):
            if new_element.strip() == '':
                new_element = 0
        new_coeffs[i] = new_element; i += 1 #Exception!
    return copy(new_coeffs)

## Rearranges list of DWT coefficients into matrix.
#  @param coeffs DWT coefficients in list of arrays.
#  @return Matrix of DWT coefficients (reshaped with zeroes fill).
def normalize_dwt_dimensions(coeffs):
    '''Resize to uniform shape'''
    new_dimension = len(coeffs[-1])
    by_rows = zeros(shape=(len(coeffs), new_dimension)); i = 0
    for element in coeffs:
        new_element = copy(element)
        new_element.resize(new_dimension, refcheck = False)
        by_rows[i] = new_element; i += 1
    return copy(by_rows)

## Restores dwt coefficients structure.
def update_dwt(coeffs, wavelet, mode='sym'):
    new_coeffs = [0] * len(coeffs)
    resized_coeffs = []

    # parse coeffs into approximation and details
    a, ds = coeffs[0], coeffs[1:]

    for d in ds:
        if isinstance(d, collections.Iterable):
            d_copy = copy([float(e) for e in d if e != ''])
#            d_copy = copy([float(e) for e in d])
            if len(a) != len(d):
                d_copy.resize(len(a), refcheck = False)

            a = pywt.idwt(a, d_copy, wavelet, mode, 1)
            resized_coeffs.append(d_copy)

    new_coeffs[0] = coeffs[0]
    new_coeffs[1:] = resized_coeffs

    return new_coeffs

## Saves wavelet approximations to /res/wv folder.
#  @param all Plot every possible wavelet.
def _plot_wavelet_families(all=False):
    '''Plotting waveletes approximations'''
    lvl = 4 # because!
    for name in pywt.families():
        if not all:
            _plot_wavelet(pywt.wavelist(name)[0], lvl)
        else:
            for wv in pywt.wavelist(name):
                _plot_wavelet(wv, lvl, True)

## Plots and saves one wavelet approximation.
#  @param wavelet Wavelet to plot.
#  @param level Approximation level.
#  @param all Use of full wavelet name (instead of just family).
def _plot_wavelet(wavelet, level=4, all=False):
    '''Plot and save wavelet to specified folder'''
    try:
        # [phi, psi, x] (not for every wavelet, hence the 'values')
        values = pywt.Wavelet(wavelet).wavefun(level=level)
        plt.figure(figsize=(1, 1))
        plt.axis('off')
        # plotting x, psi
        plt.plot(values[-1], values[-2], color='w', linewidth=LINE_WITH)  # color = 'w'(white) for black tooltips
        # full wavelet name
        if all: plt.savefig('../' + RES + WV + wavelet + '.png', transparent=True)
        # family name
        else: plt.savefig('../' + RES + WV + re.sub('[0-9. ]+', '', wavelet) + '.png', transparent=True)
    except Exception, e:
        print e, wavelet

## Gets optimal decomposition level.
#  @param data Time series array.
#  @param wv Wavelet type.
#  @param r PypeR reference.
#  @param swt Use SWT decomposition.
#  @return Number of decomposition levels.
def calculate_suitable_lvl(data, wv, r, swt=True):
    # stationary
    if swt:
        max_lvl = pywt.swt_max_level(len(data))

        lvl = 1
        ent = []
        pre_e = entropy(pywt.swt(data, wv, lvl), r)
        ent.append(pre_e)
        lvl += 1
        while True:
            new_e = entropy(pywt.swt(data, wv, lvl), r)
            ent.append(new_e)
            if lvl < max_lvl:
                lvl += 1
            else:
                break

        e_sorted = sorted(ent[:])
        median = e_sorted[len(e_sorted) / 2]
        lvl = ent.index(median) + 1
    # discrete
    else:
        lvl = 1
        data_e = entropy(data, r, True)
        max_lvl = pywt.dwt_max_level(len(data), wv)

        while True:
            new_e = entropy(pywt.dwt(data, wv, lvl)[lvl - 1], r, True)
            if new_e > data_e:
                break
            elif lvl == max_lvl:
                break
            else:
                lvl += 1

    if lvl == max_lvl:
        pass

    return lvl

## Selects suitable wavelet from all possible families and variations.
#  @param data Data for wavelet decomposition.
#  @param r PypeR reference.
#  @return Wavelet family and name.
def select_wavelet(data, r):
    pass

if __name__ == '__main__':
    _plot_wavelet_families(True)