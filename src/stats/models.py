# -*- coding: utf-8 -*-
__author__ = 'Yadavito'

# external #
from stats.pyper import Str4R
from numpy import append, zeros, delete

# own #
from utility.const import Models, r_packages
from utility.tools import arrayIndex

# forecast iterations
steps_default = 20

def initRLibraries(r):
    for package in r_packages:
        r('library( %s )' % package)

## Holt-Winters.
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
    diff = abs(len(r.hw['fitted']) - len(data))
    r('fit <- c( array(0, %s), %s )' % (Str4R(diff), Str4R(r.hw['fitted'][:,0])))
    return r.fit

def hwPredict(data, r, steps=steps_default, options=None):
    hwProcess(data, r, options)
    r('pred <- predict(hw, %s, prediction.interval = TRUE)' % Str4R(steps))
    diff = abs(len(r.hw['fitted']) - len(data))
    r('fit <- c( array(0, %s), %s )' % (Str4R(diff), Str4R(r.hw['fitted'][:,0])))
    if options['append_fit']:
        return append(r.fit, r.pred[:,0])
    else:
        return append(zeros(len(data)), r.pred[:,0])

## Least Squares Fit.
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

## ARIMA.
def arimaProcess(data, r, options=None):
    try:
        #TODO: add conversion to ts()
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

## Harmonic Regression.
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

## ETS.
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

## Cubic Splines.
def qsplineProcess(data, r, options):
    return []

def qsplinePredict(data, r, steps=steps_default, options=None):
    r('spln <- splinef( %s, %s )' % (Str4R(data), Str4R(steps)))
    if options['append_fit']:
        return append(data, r.spln['mean'])
    else:
        return append(zeros(len(data)), r.spln['mean'])

## StructTS.
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

## Methods for models.
model_process_methods = {Models.Holt_Winters: hwProcess,  Models.Least_Squares_Fit: lsfProcess,
                          Models.ARIMA: arimaProcess, Models.Harmonic_Regression: arProcess,
                          Models.ETS: etsProcess, Models.Cubic_Splines: qsplineProcess,
                          Models.StructTS: stsProcess}
model_predict_methods = {Models.Holt_Winters: hwPredict, Models.Least_Squares_Fit: lsfPredict,
                          Models.ARIMA: arimaPredict, Models.Harmonic_Regression: arPredict,
                          Models.ETS: etsPredict, Models.Cubic_Splines: qsplinePredict,
                          Models.StructTS: stsPredict}

## Perform model fit using specified model.
def processModel(model, data, r, options=None):
    return model_process_methods[model](data, r, options)

## Perform forecast using specified model.
def calculateForecast(model, data, r, steps = steps_default, options=None):
    return model_predict_methods[model](data, r, steps, options)

## Calculate series entropy.
def entropy(data, r, simple=False, dwt=False):
    if simple:
        r('e <- entropy( %s )' % Str4R(data))
        return r.e
    else:
        ent = []
        for lvl in data:
            r('e <- entropy( %s )' % Str4R(lvl[0]))
            ent.append(r.e)
    # average entropy
    return sum(ent, 0.0) / len(ent)

## Classify levels by models.
def auto_model(data, r, options, ts=None):
    models = {}
    if options['fractal']:
        dimensions = []
        for lvl in data:
            r('d <- fd.estimate( %s )' % Str4R(lvl))
            dimensions.append(r.d['fd'][0][0])

        lvl_indices = dimensions[:]
        while len(dimensions) > 1:
            hires = max(dimensions)
            trend = min(dimensions)
            models[lvl_indices.index(hires)] = Models.Harmonic_Regression
            models[lvl_indices.index(trend)] = Models.Holt_Winters

            dimensions.remove(hires)
            dimensions.remove(trend)

        if dimensions:
            models[lvl_indices.index(dimensions.pop())] = Models.ARIMA
        del lvl_indices

        return  models

    elif options['ljung']:
        xsquared = []
        for lvl in data:
            r('b <- Box.test( %s, type="Ljung" )' % Str4R(lvl))
            xsquared.append(r.b['statistic'])

        lvl_indices = xsquared[:]
        while len(xsquared) > 1:
            auto_correl = min(xsquared)
            no_correl = max(xsquared)
            models[lvl_indices.index(auto_correl)] = Models.Harmonic_Regression
            models[lvl_indices.index(no_correl)] = Models.ARIMA

            xsquared.remove(auto_correl)
            xsquared.remove(no_correl)

        if xsquared:
            models[lvl_indices.index(xsquared.pop())] = Models.Least_Squares_Fit
        del lvl_indices

        return models

    elif options['multi']:
        tmp_lvls = list(data[:])

        # ~ dispersion: trend
        dispersion = []
        for lvl in data:
            if len(lvl) >= 32:
                r('sd <- dispersion( %s )$sd' % Str4R(lvl))
                r('d <- mean(sd[1:length(sd) - 1])')
                dispersion.append(r.d)

        trend_lvl = dispersion.index(max(dispersion))

        # ~ Hurst Coefficient (spectral density): non-stationarity
        if data is not None:
            r('hc_ts <- FDWhittle( %s )' % Str4R(ts))
            r('hc_lvl <- FDWhittle( %s )' % Str4R(data[trend_lvl]))
            if r.hc_ts > r.hc_lvl:
                models[trend_lvl] = Models.ETS
            else:
                models[trend_lvl] = Models.Holt_Winters

        # ~ fluctuation: outliers, trend/decomposition limit
        fluctuation = []
        for lvl in data:
            r.lvl = lvl
            r('h <- DFA( lvl )')
            fluctuation.append(r.h)

        # ~ time lag
        hires_lvl = fluctuation.index(min(fluctuation))
        r('tl <- timeLag( %s )[1]' % Str4R(data[hires_lvl]))
        if r.tl > 2:
            models[hires_lvl] = Models.Least_Squares_Fit
        else:
            models[hires_lvl] = Models.Harmonic_Regression

        tmp_lvls.pop(trend_lvl)
        if hires_lvl != 0:
            tmp_lvls.pop(hires_lvl - 1)
        else:
            tmp_lvls.pop(hires_lvl - 1)

        # ~ autocorrelation
        r('bts <- Box.test( %s, type="Ljung" )$statistic' % Str4R(ts))
        for lvl in tmp_lvls:
            r('lb <- Box.test( %s, type="Ljung" )$statistic' % Str4R(lvl))
            if r.lb < r.bts:
                models[arrayIndex(data, lvl)] = Models.ARIMA
            else:
                models[arrayIndex(data, lvl)] = Models.StructTS

        return models

## Calculate model error.
def model_error(data, new_data, r):
    errors = {}

#    r('diff <- abs( length(%s) - length(%s) )' % (Str4R(data), Str4R(new_data)))
#    r('e <- c( %s, array(0, diff) ) - c( array(0, diff), %s )' % (Str4R(data), Str4R(new_data)))
    r('len <- length( %s )' % Str4R(data))
    r('e <- %s - %s[1:len]' % (Str4R(data), Str4R(new_data)))

    r('mse <- sum((e - mean(e)) ^ 2) / length(e)')
    r('sse <- sum(e ^ 2)')

    try:
        errors['mse'] = r.mse
        errors['sse'] = r.sse
    except Exception:
        pass
    return errors
