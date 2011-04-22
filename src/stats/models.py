# -*- coding: utf-8 -*-
__author__ = 'Yadavito'

# external #
from stats.pyper import R, Str4R
from numpy import append

# own #
from utils.const import Models

def hwProcess(data, r):
    r.i_data = data
    r('hw <- HoltWinters( i_data, gamma = FALSE )')
    print r.hw['SSE']
    return r.hw['fitted'][:,0]

def hwPredict(data, r):
    hwProcess(data, r)
    r.steps_ahead = 50  #TODO: implement variable in r query
    r( 'pred <- predict(hw, 50, prediction.interval = TRUE)')
    return append(r.hw['fitted'][:,0], r.pred[:,0])

model_process_methods = { Models.Holt_Winters : hwProcess }
model_predict_methods = { Models.Holt_Winters : hwPredict }

def processModel(model, data, r):
    return model_process_methods[model](data, r)

def calculateForecast(model, data, r):
    return model_predict_methods[model](data, r)