# -*- coding: utf-8 -*-
__author__ = 'Yadavito'

# external #
from stats.pyper import R, Str4R
from numpy import append

# own #
from utils.const import Models

def hwProcess(data, r, gamma = False):
#    r.i_data = data
#    r.seasonal = gamma
#    r('hw <- HoltWinters( i_data, gamma = FALSE )')
#    r('hw <- HoltWinters( %s, gamma = %s )' % (Str4R(r.i_data), Str4R(r.seasonal)))
    r('hw <- HoltWinters( %s, gamma = %s )' % (Str4R(data), Str4R(gamma)))
    print r.hw['SSE']
    return r.hw['fitted'][:,0]

def hwPredict(data, r, steps = 20):
    hwProcess(data, r)
#    r.steps_ahead = steps
#    r( 'pred <- predict(hw, 50, prediction.interval = TRUE)')
#    r( 'pred <- predict(hw, %s, prediction.interval = TRUE)' % Str4R(r.steps_ahead))
    r( 'pred <- predict(hw, %s, prediction.interval = TRUE)' % Str4R(steps))
    return append(r.hw['fitted'][:,0], r.pred[:,0])

model_process_methods = { Models.Holt_Winters : hwProcess }
model_predict_methods = { Models.Holt_Winters : hwPredict }

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