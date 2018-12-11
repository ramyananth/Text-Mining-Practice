#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 16:20:34 2017

@author: Tredence
"""
#from ngdict import ngDictionaries #, checkMembership #, ngToken, isngToken 
from  ngdict import isngToken, parseAsNgrams #,ngToken ngtok
from utils_features import haskey, discVar2Feature
from config import *  
from Resources import RESKEY_DOMAINMEMDICTS

def NGramizeFromDomainDict(procTxt, hr, featureVals = {}, FKEY = 'NGramizeFromDomainDict'):
    """
    """
    if haskey(featureVals, FKEY): return featureVals
    #S = [t[0] for t in procTxt]
    #ngd = ngDictionaries('dbg/dicts/telcomDicts/')
    retval = parseAsNgrams(hr.resources[RESKEY_DOMAINMEMDICTS], procTxt) 
   
    featureVals[FKEY] = retval            
    return featureVals

def countNGInDomainDict(procTxt, hr, featureVals = {}, FKEY = 'countNGInDomainDict'):
    """
    """
    if haskey(featureVals, FKEY): return featureVals
    
    featureVals = NGramizeFromDomainDict(procTxt, hr, featureVals)
    ngtoks = featureVals['NGramizeFromDomainDict']

    retval = {KEY_POLARITY_POSITIVE: [], KEY_POLARITY_NEGATIVE: [], KEY_POLARITY_NEUTRAL: []}    
    for tok in ngtoks:
        if isngToken(tok) and not tok.isNull():
            ng = tok.n
            pol = tok.polarity
            
#            if ncount.has_key(pol) == False:
#                ncount[pol] = list()
            retval[pol].append(ng)

    featureVals[FKEY] = retval            
    return featureVals
                           
    

