# -*- coding: utf-8 -*-
__author__ = 'Yadavito'

# external #
from stats.pyper import R, Str4R
from numpy import append, array, zeros

# own #
from utility.const import Models, r_packages

# forecast iterations
steps_default = 20

def initRLibraries(r):
    for package in r_packages:
        r('library( %s )' % package)

# Holt-Winters
def hwProcess(data, r, options):
    gamma = False
    nonSeasonalHw = lambda data, gamma: \
        r('hw <- HoltWinters( %s, gamma = %s )' % (Str4R(data), Str4R(gamma)))
    try:
        r('hw <- HoltWinters( ts( %s, frequency = %s ), seasonal = %s, gamma = %s )' %
           (Str4R(data), Str4R(options['hw_period']),
            Str4R(options['hw_model']),
            Str4R(options['hw_gamma'])))
    except Exception:
        nonSeasonalHw(data, gamma)
#    print r.hw['SSE']   # <- do something with it
    return r.hw['fitted'][:,0]

def hwPredict(data, r, steps=steps_default, options=None):
    hwProcess(data, r, options)
    r('pred <- predict(hw, %s, prediction.interval = TRUE)' % Str4R(steps))
    diff = abs(len(r.hw['fitted']) - len(data))
    r('fit <- c( array(0, %s), %s )' % (Str4R(diff), Str4R(r.hw['fitted'][:,0])))
    if options['append_fit']:
        return append(r.fit, r.pred[:,0])
    else:
        return append(zeros(len(data)), r.pred[:,0])

# Least Squares Fit
def lsfProcess(data, r, options):
    try:
        if options['lsf_aic']:
            r('lsf <- ar.ols( %s, aic = %s )' % (Str4R(data), Str4R(options['lsf_aic'])))
        else:
            r('lsf <- ar.ols( %s, order.max = %s )' % (Str4R(data), Str4R(options['lsf_order'])))
    except Exception, e:
         r('lsf <- ar.ols( %s )' % Str4R(data))
    return []

def lsfPredict(data, r, steps=steps_default, options=None):
    lsfProcess(data, r, options)
    r('pred <- predict( lsf, n.ahead = %s ) ' % Str4R(steps) )
    if options['append_fit']:
        return append(data, r.pred['pred'])
    else:
        return append(zeros(len(data)), r.pred['pred'])

# ARIMA
def arimaProcess(data, r, options=None):
    try:
        if options['arima_auto']:
            r('amafit <- auto.arima( %s )' % Str4R(data))
        elif options['arima_seas'] and options['arima_nons']:
            r('amafit <- arima(%s, order = %s, seasonal = list(order= %s ))' %
              (Str4R(data),
               Str4R(options['arima_nons_order']),
               Str4R(options['arima_seas_order'])))
        elif options['arima_nons']:
            r('amafit <- arima(%s, seasonal = list(order= %s ))' %
              (Str4R(data),
               Str4R(options['arima_nons_order'])))
        elif options['arima_seas']:
            r('amafit <- arima(%s, order = %s )' %
              (Str4R(data),
               Str4R(options['arima_nons_order'])))
    except Exception, e:
        r.d = 1; r.p = 0; r.q = 1
        r('amafit <- arima(%s, order = c(d, p ,q))' % Str4R(data) )
    return []

def arimaPredict(data, r, steps=steps_default, options=None):
    arimaManual = lambda steps: \
        r('pred <- predict(amafit, n.ahead = %s)' % Str4R(steps))

    arimaProcess(data, r, options)
    try:
        if options['arima_auto']:
            r('pred <- forecast(amafit, %s)' % Str4R(steps))
            return append(r.pred['fitted'], r.pred['mean'])
        else:
            arimaManual(steps)
    except Exception, e:
        arimaManual(steps)
    if options['append_fit']:
        return append(data, r.pred['pred'])
    else:
        return append(zeros(len(data)), r.pred['pred'])

# Harmonic Regression
def arProcess(data, r, options):
    try:
        if options['ar_aic']:
            r('afit <- ar( %s, aic = %s, method = %s )' %
              (Str4R(data), Str4R(options['ar_aic']), Str4R(options['ar_method'])))
        else:
            r('afit <- ar( %s, order.max = %s, method = %s )' %
              (Str4R(data), Str4R(options['ar_order']), Str4R(options['ar_method'])))
    except Exception:
        r('afit <- ar( %s )' % Str4R(data) )
    return []

def arPredict(data, r, steps=steps_default, options=None):
    arProcess(data, r, options)
    r('pred <- predict( afit, n.ahead = %s )' % Str4R(steps))
    if options['append_fit']:
        return append(data, r.pred['pred'])
    else:
        return append(zeros(len(data)), r.pred['pred'])

def etsProcess(data, r, options):
    etsAuto = lambda data: \
        r('efit <- ets( %s )' % Str4R(data))
    try:
        if not options['ets_auto']:
            r('efit <- ets( ts( %s, frequency = %s ), model = %s )' %
              (Str4R(data), Str4R(options['ets_period']),
               Str4R(options['ets_random_model'] +
              options['ets_trend_model'] +
              options['ets_seasonal_model'])))
        else:
            etsAuto(data)
    except Exception, e:
        etsAuto(data)
    return r['efit$fitted']

def etsPredict(data, r, steps=steps_default, options=None):
    etsProcess(data, r, options)
    r('pred <- forecast( efit, %s )' % Str4R(steps))
    if options['append_fit']:
        return append(r['efit$fitted'], r['pred$mean'])
    else:
        return append(zeros(len(data)), r['pred$mean'])

def qsplineProcess(data, r, options):
    return []

def qsplinePredict(data, r, steps=steps_default, options=None):
    r('spln <- splinef( %s, %s )' % (Str4R(data), Str4R(steps)))
    if options['append_fit']:
        return append(data, r.spln['mean'])
    else:
        return append(zeros(len(data)), r.spln['mean'])

#def garchProcess(data, r, options):
#    # order=c(1,0)
#    r('g <- garch( %s )' % Str4R(data))
##    return r.g['fitted.values'][:,0]
#    return[]
#
#def garchPredict(data, r, steps=steps_default, options=None):
#    garchProcess(data, r, options)
#    r('pred <- predict( g, %s )' % steps)
#    if options['append_fit']:
#        return append(data, r.pred[:,0])
#    else:
#        return append(zeros(len(data)), r.pred[:,0])

def stsProcess(data, r, options):
    r('sfit <- StructTS( %s, %s )' % (Str4R(data), Str4R(options['sts_type'])))
    return r.sfit['fitted']

def stsPredict(data, r, steps=steps_default, options=None):
    stsProcess(data, r, options)
    r('pred <- forecast( %s, %s )' % (Str4R(data), Str4R(steps)))
    if options['append_fit']:
        return append(r['pred$fitted'], r['pred$mean'])
    else:
        return append(zeros(len(data)), r.pred['mean'])

# methods dicts
model_process_methods = {Models.Holt_Winters: hwProcess,  Models.Least_Squares_Fit: lsfProcess,
                          Models.ARIMA: arimaProcess, Models.Harmonic_Regression: arProcess,
                          Models.ETS: etsProcess, Models.Cubic_Splines: qsplineProcess,
                          Models.StructTS: stsProcess}
#                          Models.GARCH: garchProcess, Models.StructTS: stsProcess}
model_predict_methods = {Models.Holt_Winters: hwPredict, Models.Least_Squares_Fit: lsfPredict,
                          Models.ARIMA: arimaPredict, Models.Harmonic_Regression: arPredict,
                          Models.ETS: etsPredict, Models.Cubic_Splines: qsplinePredict,
                          Models.StructTS: stsPredict}
#                          Models.GARCH: garchPredict, Models.StructTS: stsPredict}

# interface methods
def processModel(model, data, r, options=None):
    return model_process_methods[model](data, r, options)

def calculateForecast(model, data, r, steps = steps_default, options=None):
    return model_predict_methods[model](data, r, steps, options)

def entropy(data, r, simple=False):
    if simple:
        r('e <- entropy( %s )' % Str4R(data))
        return r.e
    else:
        ent = []
        for lvl in data:
            r('e <- entropy( %s )' % Str4R(lvl[0]))
            ent.append(r.e)
    return min(ent)