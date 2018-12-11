# -*- coding: utf-8 -*-
"""
Data-types and functionality to handle n-grams
class ngDictionaries
class ngToken
function checkMembership(ng, ngdict)

"""
from  ngdict import isngToken,ngToken, parseAsNgrams #
from utils_features import haskey, discVar2Feature
from config import *
from Resources import RESKEY_POLAR_NGRAMS, RESKEY_NEGATORS
#from chunkAnalysis import chunkPolarityUpdate
from clause_pol import clausePolarity
#from token_properties import tokenLexicalProps, updateTokenLexicalProperties

def ngramize(procTxt, hr, featureVals = {}, FKEY = 'ngramize'):
    """
    procTxt = [('this', 'O'), ('is', 'V'), ('not', 'A'), ('awesome', 'A'), (':)', 'E')]

    """
    if haskey(featureVals, FKEY): return featureVals
    #S = [t[0] for t in procTxt]
    ngramizedS = parseAsNgrams(hr.resources[RESKEY_POLAR_NGRAMS],procTxt) #hr.resources['priorPolarityDicts'].

    featureVals[FKEY] = ngramizedS
    return featureVals

def ngSimpleNegate(procTxt, hr, featureVals = {}, FKEY = 'ngSimpleNegate'):
    """
    """
    if haskey(featureVals, FKEY): return featureVals

    if featureVals.has_key('ngramize') == False:
        featureVals = ngramize(procTxt, hr, featureVals)

    ngramizedS = featureVals['ngramize']

    aPostNgramizedS =list()
    for k, ng in enumerate(ngramizedS):
        if isngToken(ng) == False:
            aPostNgramizedS.append(ng)
        else:
            negationWindow = ngramizedS[k-2:k]
            negationWindow.reverse()
            flip = False
            for tok in negationWindow:
                if tok in hr.resources[RESKEY_NEGATORS].getDicts(1, KEY_NEGATION): #hr.resources['negation']:
                    flip = True
                    break
            if flip:
                if ng.polarity == KEY_POLARITY_POSITIVE:
                    newToken = ngToken(ng.n,KEY_POLARITY_NEGATIVE)
                    newToken.saveContext(ng.val, ng.S, ng.bidx, ng.eidx)
                else:
                    newToken = ngToken(ng.n,KEY_POLARITY_POSITIVE)
                    newToken.saveContext(ng.val, ng.S, ng.bidx, ng.eidx)
            else:
                newToken = ng

            aPostNgramizedS.append(newToken)

    featureVals[FKEY] = aPostNgramizedS
    return featureVals


__NumToPol__ = {-1:KEY_POLARITY_NEGATIVE, 1:KEY_POLARITY_POSITIVE, 0:KEY_POLARITY_NEUTRAL}

def countPolarNGrams(procTxt, hr, featureVals = {}, FKEY = 'countPolarNGrams'):
    if haskey(featureVals, FKEY): return featureVals

    try:
        procTxt[PTKEY_CHUNKEDCLAUSES][0][0][0].tprops
    except:
        procTxt = updateTokenLexicalProperties(procTxt, hr)

    count = {KEY_POLARITY_POSITIVE: {}, KEY_POLARITY_NEGATIVE: {}, KEY_POLARITY_NEUTRAL: {}}

    for k in count:
        for n in hr.resources[RESKEY_POLAR_NGRAMS].availableNgrams:
            count[k][n] = 0

    negation = hr.resources[RESKEY_NEGATORS].getDicts(1, KEY_NEGATION)


    for sentence in procTxt[PTKEY_CHUNKEDCLAUSES]:
        for clause in sentence:
            for chunk in clause:
                chPat, pols, negn, negtd = clausePolarity(clause, hr)
                for k, tok in enumerate(chunk.tokens):
                    pol = pols[k]
                    if negtd[k]:
                        pol = pol*-1
                    pkey = __NumToPol__[pol]
                    n = len(tok.split('_NG_'))
                    count[pkey][n] += 1
#    for ng in aposng:
#        if isngToken(ng):
#            count[ng.polarity][ng.n] += 1

    featureVals[FKEY] = count
    return featureVals

def containsPolarNG(procTxt, hr, featureVals = {}, FKEY = 'containsPolarNG'):

    #print featureVals

    if haskey(featureVals, FKEY): return featureVals
    if featureVals.has_key('countPolarNGrams') == False:
        featureVals = countPolarNGrams(procTxt, hr, featureVals)
    count = featureVals['countPolarNGrams']

    has = {k:False for k in count}

    for k in count:
        if any(count[k].values()):
            has[k] = True

    featureVals[FKEY] = has
    return featureVals

def containsPolar2G(procTxt, hr, featureVals = {}, FKEY = 'containsPolar2G'):

    if haskey(featureVals, FKEY): return featureVals
    if featureVals.has_key('countPolarNGrams') == False:
        featureVals = countPolarNGrams(procTxt, hr, featureVals)
    count = featureVals['countPolarNGrams']

    has = {k:False for k in count}

    for k in count:
        if count[k][2] > 0:
            has[k] = True

    featureVals[FKEY] = has
    return featureVals

def containsPolar3G(procTxt, hr, featureVals = {}, FKEY = 'containsPolar3G'):

    if haskey(featureVals, FKEY): return featureVals
    if featureVals.has_key('countPolarNGrams') == False:
        featureVals = countPolarNGrams(procTxt, hr, featureVals)
    count = featureVals['countPolarNGrams']

    has = {k:False for k in count}

    for k in count: #iterate over positive and negative
        relkeys = count[k].keys()[2:] #3G and up
        for n in relkeys: #iterate over 3G and up
            if count[k][n] > 0:
                has[k] = True
                break

    featureVals[FKEY] = has
    return featureVals


