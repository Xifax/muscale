# -*- coding: utf-8 -*-
__author__ = 'Michael Marino, Yadavito'

# internal #
import math

# external #
import pywt, numpy
from numpy import array, vstack, append, zeros, resize

def apply_threshold(output, scaler = 1., input=None):
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
def measure_threshold(output, scaler = 1.):
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

            # average and insert into the correct indices
            output[indices] = (x1 + x2)/2.

    return output

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
    rearranged = zeros( shape = ( len(by_rows)/2 + 1, len(by_rows[0]) ) )
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

def update_selected_levels_swt(inital_coeffs, selected_coeffs):
    '''Restores tree structure for further ISWT'''
    # rearranging back to how it was
    by_rows = vstack(inital_coeffs)
    index = len(by_rows) - 1; s_index = 0
    while True:
        if index > 1:
            by_rows[index] = selected_coeffs[s_index]
            index -= 2
        elif index >= 0:
            by_rows[index] = selected_coeffs[s_index]
            index -= 1
        else: break
        s_index += 1
    # tupling and listing
    all_of_coeffs = []; element = 0
    while element <= len(by_rows)/2 + 1:
        all_of_coeffs.append( (by_rows[element],  by_rows[element + 1]) )
        element += 2
    return all_of_coeffs

def normalize_dwt_dimensions(coeffs):
    new_dimension = len(coeffs[-1])
    by_rows = zeros(shape=(len(coeffs), new_dimension)); i = 0
    for element in coeffs:
        by_rows[i] = resize(element, new_dimension); i += 1
    return by_rows
