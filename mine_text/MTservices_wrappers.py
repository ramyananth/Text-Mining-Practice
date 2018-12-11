#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 16:22:10 2017

@author: Tredence
"""

__MTAPI_RESULT__ = 'result'
__MTAPI_ISAD__ = 'isAd'
__PPKEY_PC__ = 'context'
__MTAPI_ASPECT__ = 'entities'
__MTAPI_TEXT__ = 'text'
__PPKEY_PCDM__ = 'contextDomainNoun'

from mine_text import getProbPredictions, MTKEY_LABEL
from extractKeywords import extractKeywords
from ppd import problemPhraseDetector
from problem_phrases import probPhrasePretty
from problem_phrases import probleMTontextDetector
#from polar_clauses import entity_sentiment
from appDefs import PTKEY_TOKENS
from adDetect import adDetection
from surface_properties import charCounts
from w2vutils import proctxt2tt
from phrase_analysis import phraseAnalysis
from phrase_analysis2 import entity_sentiment
from escalation import escalation
from text_sentiment_lenovo import text_sentiment_lenovo

def MTserviceswrapper_tokstags(proctxt, hres, model=None, computedFeatures=None, featureVals={}):
    """Output formating for Sentiment"""
    
    result = {__MTAPI_RESULT__:proctxt2tt(proctxt)}
    return result
    
def MTserviceswrapper_phraseanalysis(proctxt, hres, model=None, computedFeatures=None, featureVals={}):
    """Output formating for Sentiment"""
    
    result = {__MTAPI_RESULT__:phraseAnalysis(proctxt, hres)}
    return result    


def MTserviceswrapper_sentiment(proctxt, hres, model, computedFeatures=None, featureVals={}):
    """Output formating for Sentiment"""
    tsl = text_sentiment_lenovo(proctxt, hres[0])
    #print "TSL",tsl
    result = getProbPredictions(proctxt, hres[0], model[0], computedFeatures)
    #print "TSL2",result
    if result["label"] == "negative":
        result[__MTAPI_RESULT__] = result.pop(MTKEY_LABEL)
        #print "TSL3",result
        return result
    else:    
        result = {"result" :tsl["result"]}
        result["scores"] = tsl["scores"]
        #print "TSL3",result
        return result

def MTserviceswrapper_problem(proctxt, hres, model, computedFeatures=None, featureVals={}):
    """Output formating for Problem Text and Context Detection"""
    result = getProbPredictions(proctxt, hres[0], model[0], computedFeatures)
    result[__MTAPI_RESULT__] = int(result.pop(MTKEY_LABEL))
    #result[__PPKEY_PC__] = probPhrasePretty(proctxt, hres[0])

    if result[__MTAPI_RESULT__] == 1:
        #result[__PPKEY_PC__] = probPhrasePretty(proctxt, hres[0]) #problemPhraseDetector(proctxt, hres[0])
        #result[__PPKEY_PC__] = problemPhraseDetector(proctxt, hres[0])
        problem_context_dm,problem_context = probleMTontextDetector(proctxt, hres[0])
        result[__PPKEY_PCDM__] = problem_context_dm
        result[__PPKEY_PC__] = problem_context
    else:
        result[__PPKEY_PCDM__] = []
        result[__PPKEY_PC__] = []
    return result

def MTserviceswrapper_keywords(proctxt, hres, model=None, computedFeatures=None, featureVals={}):
    """Output formating for Keywords"""
    result = {__MTAPI_RESULT__:extractKeywords(proctxt, hres[0])}
    return result

    
def MTserviceswrapper_escalation(proctxt, hres, model=None, computedFeatures=None, featureVals={}):
    """Output formating for escalation"""
    result = {__MTAPI_RESULT__:escalation(proctxt, hres[0])}
    return result
    
def MTserviceswrapper_text_sentiment_lenovo(proctxt, hres, model=None, computedFeatures=None, featureVals={}):
    """Output formating for escalation"""
    tsl = text_sentiment_lenovo(proctxt, hres[0])
    result = {"label" :tsl["result"]}
    result["scores"] = tsl["scores"]          
    return result
    
    
def MTserviceswrapper_counts(proctxt, hres, model=None, computedFeatures=None, featureVals={}):
    """Output formating for Keywords"""
    result = {__MTAPI_RESULT__:charCounts(proctxt)}
    return result
    
def MTserviceswrapper_ads(proctxt, hres=None, model=None, computedFeatures=None, featureVals={}):
    """Output formating for Ad Detection"""
    if not 'adDetection' in featureVals:
        featureVals = adDetection(proctxt, hres, featureVals)
        
    result = {__MTAPI_RESULT__: featureVals['adDetection']} #proctxt[__MTAPI_ISAD__]}
    return result

def MTserviceswrapper_entity(proctxt, hres=None, model=None, computedFeatures=None, featureVals={}):
    """Output formating for Entity based Sentiment"""
    result = {__MTAPI_RESULT__:entity_sentiment(proctxt, hres[0], sentiment_flag=1)}
    return result

from processText import sentenceSplitProcTxts
def MTserviceswrapper_sentenceLevelSentiment(procTxt, hres, model, computedFeatures=None, featureVals={}):
    """Output formating for Sentiment"""
    sprocTxtLst = sentenceSplitProcTxts(procTxt)
    result = []
    for sprocTxt in sprocTxtLst:
        sprocTxt[__MTAPI_ISAD__] = procTxt[__MTAPI_ISAD__]
        tresult = getProbPredictions(sprocTxt, hres[0], model[0])
        tresult[__MTAPI_RESULT__] = tresult.pop(MTKEY_LABEL)
        tresult[__MTAPI_ASPECT__] = entity_sentiment(sprocTxt, hres[0], sentiment_flag=1)
        tresult[__MTAPI_TEXT__] = ' '.join(sprocTxt[PTKEY_TOKENS])
        result.append(tresult)
    return result
    
    
