# -*- coding: utf-8 -*-
__author__ = 'Yadavito'

# external #
from stats.pyper import R, Str4R
from numpy import append

# own #
from utils.const import Models

steps_default = 20

def hwProcess(data, r, gamma = False):
    r( 'hw <- HoltWinters( %s, gamma = %s )' % (Str4R(data), Str4R(gamma)) )
    print r.hw['SSE']
    return r.hw['fitted'][:,0]

def hwPredict(data, r, steps = steps_default):
    hwProcess(data, r)
    r( 'pred <- predict(hw, %s, prediction.interval = TRUE)' % Str4R(steps) )
    return append(r.hw['fitted'][:,0], r.pred[:,0])

def lsfProcess(data, r):
    pass

def lsfPredict(data, r, steps = steps_default):
    pass

def armaProcess(data, r):
    pass

def armaPredict(data, r, steps = steps_default):
    pass

model_process_methods = { Models.Holt_Winters : hwProcess,  Models.Least_Squares_Fit : lsfProcess,  Models.ARMA : armaProcess }
model_predict_methods = { Models.Holt_Winters : hwPredict, Models.Least_Squares_Fit : lsfPredict,  Models.ARMA : armaPredict }

def processModel(model, data, r):
    return model_process_methods[model](data, r)

def calculateForecast(model, data, r):
    return model_predict_methods[model](data, r)

#r = R()
#r.test = 5
#print Str4R(r.test)
#r('hw <- HoltWinters(c(1,2,3,4,5,6), gamma=FALSE)')
##r('a <- c(%s, 1, 2)' % Str4R(r.test))
#r('a <- predict(hw, %s)' % Str4R(r.test))
#print r.a