# -*- coding: utf-8 -*-
__author__ = 'Yadavito'

# external #
from stats.pyper import R, Str4R
from numpy import append, array

# own #
from utils.const import Models

# forecast iterations
steps_default = 20

# Holt-Winters
def hwProcess(data, r, gamma = False):
    r( 'hw <- HoltWinters( %s, gamma = %s )' % (Str4R(data), Str4R(gamma)) )
    print r.hw['SSE']
    return r.hw['fitted'][:,0]

def hwPredict(data, r, steps = steps_default):
    hwProcess(data, r)
    r( 'pred <- predict(hw, %s, prediction.interval = TRUE)' % Str4R(steps) )
    return append(r.hw['fitted'][:,0], r.pred[:,0])

# Least Squares Fit
def lsfProcess(data, r):
    r( 'lsf <- ar.ols(%s)' % Str4R(data) )
    return []

def lsfPredict(data, r, steps = steps_default):
    lsfProcess(data, r)
    r( 'pred <- predict( lsf, n.ahead = %s ) ' % Str4R(steps) )
    return append(data, r.pred['pred'])

# ARIMA
def arimaProcess(data, r):
    r.d = 1; r.p = 0; r.q = 1   #temporary
    r( 'amafit <- arima(%s, order = c(d, p ,q))' % Str4R(data) )
#    r( 'amafit <- arima(%s, order = c(1, 0 , 1))' % Str4R(data) )
    return []

def arimaPredict(data, r, steps = steps_default):
    arimaProcess(data, r)
    r( 'pred <- predict(amafit, n.ahead = %s)' % Str4R(steps) )
    return append(data, r.pred['pred'])

# Harmonic Regression
def arProcess(data, r):
    #NB: Yule-Walker by default (optional: method='burg', 'ols')
    r( 'afit <- ar( %s )' % Str4R(data) )
    return []

def arPredict(data, r, steps = steps_default):
    arProcess(data, r)
    r( 'pred <- predict( afit, n.ahead = %s )' % Str4R(steps) )
    return append(data, r.pred['pred'])

# methods dicts
model_process_methods = { Models.Holt_Winters : hwProcess,  Models.Least_Squares_Fit : lsfProcess,
                          Models.ARIMA : arimaProcess, Models.Harmonic_Regression : arProcess }
model_predict_methods = { Models.Holt_Winters : hwPredict, Models.Least_Squares_Fit : lsfPredict,
                          Models.ARIMA : arimaPredict, Models.Harmonic_Regression : arPredict }

# interface methods
def processModel(model, data, r):
    return model_process_methods[model](data, r)

def calculateForecast(model, data, r, steps = steps_default):
    return model_predict_methods[model](data, r, steps)