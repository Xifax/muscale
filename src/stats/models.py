# -*- coding: utf-8 -*-
__author__ = 'Yadavito'

# external #
from stats.pyper import R, Str4R
from numpy import append, array

# own #
from utility.const import Models

# forecast iterations
steps_default = 20

# Holt-Winters
def hwProcess(data, r, options, gamma=False):
    r( 'hw <- HoltWinters( %s, gamma = %s )' % (Str4R(data), Str4R(gamma)) )
#    print r.hw['SSE']
    return r.hw['fitted'][:,0]

def hwPredict(data, r, steps=steps_default, options=None):
    hwProcess(data, r, options)
    r( 'pred <- predict(hw, %s, prediction.interval = TRUE)' % Str4R(steps) )
    diff = abs(len(r.hw['fitted']) - len(data))
    r( 'fit <- c( array(0, %s), %s )' % ( Str4R(diff), Str4R(r.hw['fitted'][:,0]) ) )
    return append(r.fit, r.pred[:,0])

# Least Squares Fit
def lsfProcess(data, r, options):
    r( 'lsf <- ar.ols(%s)' % Str4R(data) )
    return []

def lsfPredict(data, r, steps=steps_default, options=None):
    lsfProcess(data, r, options)
    r( 'pred <- predict( lsf, n.ahead = %s ) ' % Str4R(steps) )
    return append(data, r.pred['pred'])

# ARIMA
def arimaProcess(data, r, options=None):
    r.d = 1; r.p = 0; r.q = 1   #temporary
    r( 'amafit <- arima(%s, order = c(d, p ,q))' % Str4R(data) )
#    r( 'amafit <- arima(%s, order = c(1, 0 , 1))' % Str4R(data) )
    return []

def arimaPredict(data, r, steps=steps_default, options=None):
    arimaProcess(data, r, options)
    r( 'pred <- predict(amafit, n.ahead = %s)' % Str4R(steps) )
    return append(data, r.pred['pred'])

# Harmonic Regression
def arProcess(data, r, options):
    #NB: Yule-Walker by default (optional: method='burg', 'ols')
    r( 'afit <- ar( %s )' % Str4R(data) )
    return []

def arPredict(data, r, steps=steps_default, options=None):
    arProcess(data, r, options)
    r( 'pred <- predict( afit, n.ahead = %s )' % Str4R(steps) )
    return append(data, r.pred['pred'])

# methods dicts
model_process_methods = { Models.Holt_Winters : hwProcess,  Models.Least_Squares_Fit : lsfProcess,
                          Models.ARIMA : arimaProcess, Models.Harmonic_Regression : arProcess }
model_predict_methods = { Models.Holt_Winters : hwPredict, Models.Least_Squares_Fit : lsfPredict,
                          Models.ARIMA : arimaPredict, Models.Harmonic_Regression : arPredict }

# interface methods
def processModel(model, data, r, options=None):
    return model_process_methods[model](data, r, options)

def calculateForecast(model, data, r, steps = steps_default, options=None):
    return model_predict_methods[model](data, r, steps, options)