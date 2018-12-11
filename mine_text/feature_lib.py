#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 16:22:10 2017

@author: Tredence
"""

from featureFuncs_core import *
from featureFuncs_domain import *
from featureFuncs_ngrams import *
#from featureFuncs_shallowparse import *
from featureFuncs_chunk import *
#from chunkAnalysis import countPolarChunks, netPolarChunks #,lastpolarity
#from chunkPol import countPolarChunks, netPolarChunks, countPosteriorPolarChunks, netPosteriorPolarChunks #,lastpolarity
from clause_pol import countPolarChunks, netPolarChunks, countPosteriorPolarChunks, netPosteriorPolarChunks
from profanityAnalysis import txtContainsProfanity, positiveinterjection, negativeinterjection
from utils_features import discVar2Feature
from clause_pol import countPolarChunksInClausedSentences
from clause_pol import TPC_CHUNKTYPES, TPC_POLTYPES

def countSmileyFeature(tokTag, hr, featureVals = {}):
    """
    count Smiley Feature Encoding
    3 level discretization for
    """
    csname = 'countSmiley'
    nsname = 'negative smiley'
    psname = 'positive smiley'

    featureVals = countSmiley(tokTag, hr, featureVals)
    np, nn = featureVals[csname]
    nfdict = discVar2Feature(featureVals[csname][0], nsname, lims = [1,1]) #negative smiley
    pfdict = discVar2Feature(featureVals[csname][1], psname, lims = [1,1]) #positive smiley
    featureSets = {}
    featureSets.update(pfdict.items())
    featureSets.update(nfdict.items())

    return (featureVals, featureSets)

def countPolarPOSFeature(tokTag, hr, featureVals = {}):
    """
    count Polar POS Feature Encoding
    5 level discretization
    """
    featureVals = countPolarPOS(tokTag, hr, featureVals)
    cnt = featureVals['countPolarPOS']

    #work on this should not have to deal with labels here....
    senlbls = ['negative', 'positive']
    POSLbls = ['adjective', 'adverb', 'verb'] #,'noun','interjection']
    retdict = dict()
    for pos in POSLbls:
        for sen in senlbls:
            retdict.update(discVar2Feature(cnt[sen][pos], sen +' '+ pos, lims = [1,3], collapse = [False, True]))
            #retdict.update(discVar2Feature(cnt[sen][pos], sen +' '+ pos, lims = [1,5], collapse = [False, True]))

    featureSets = {}
    featureSets.update(retdict)
    return (featureVals, featureSets)

def hasURLFeature(tokTag, hr, featureVals = {}):
    """
    net POS Polarity URL Encoding
    Binary feature
    """

    featureVals = hasURL(tokTag, hr, featureVals)
    retval = featureVals['hasURL']

    featureSets = {}
    featureSets.update({"hasurl":retval})
    return featureVals, featureSets
def netPOSPolarityURLFeature(tokTag, hr, featureVals = {}):
    """
    net POS Polarity URL Encoding
    Binary feature
    """
    urlmaxpos = 'contains a url with max of positive words'
    urlmaxneg = 'contains a url with max of negative words'
    urlmaxneu = 'contains a url with max of neutral words'
    url_pol='contains a url with polar words'

    featureVals = netPOSPolarityURL(tokTag, hr, featureVals)
    netpolurl = featureVals['netPOSPolarityURL']

    featureSets = {}
    featureSets[urlmaxpos] = netpolurl['url with max of positive words']
    featureSets[urlmaxneg] = netpolurl['url with max of negative words']
    featureSets[urlmaxneu] = netpolurl['url with max of neutral words']
    featureSets[url_pol] = netpolurl['url with polar words']

    return featureVals, featureSets

def totalPolarityFeature(tokTag, hr, featureVals = {}):
    """
    net POS Polarity URL Encoding
    Binary feature
    """
#    urlmaxpos = 'contains a url with max of positive words'
#    urlmaxneg = 'contains a url with max of negative words'
#    urlmaxneu = 'contains a url with max of neutral words'

    featureVals = totalPolarity(tokTag, hr, featureVals)
    totpol = featureVals['totalPolarity']

    featureSets = {}
    featureSets.update(totpol)

#    featureSets[urlmaxpos] = netpolurl['url with max of positive words']
#    featureSets[urlmaxneg] = netpolurl['url with max of negative words']
#    featureSets[urlmaxneu] = netpolurl['url with max of neutral words']

    return featureVals, featureSets

def netPOSPolarityLenFeature(tokTag, hr, featureVals = {}):
    """
    net POS Polarity Len Encoding
    Binary feature
    Can be further simplified.
    """
    #feature names.
    ssmaxpos = 'short sentence with max of positive words'
    ssmaxneg = 'short sentence with max of negative words'
    ssmaxneu = 'short sentence with max of neutral words'

    featureSets[ssmaxpos] = False;
    featureSets[ssmaxneg] = False;
    featureSets[ssmaxneu] = False

    featureVals = netPOSPolarityLen(tokTag, hr, featureVals)
    netpollen = featureVals['netPOSPolarityLen']

    featureSets = {}
    featureSets[ssmaxpos] = netpollen[ssmaxpos] #['short sentence with max of positive words']
    featureSets[ssmaxneg] = netpollen[ssmaxneg] #['short sentence with max of negative words']
    featureSets[ssmaxneu] = netpollen[ssmaxneu] #['short sentence with max of neutral words']

    return featureVals, featureSets

def countNGInTelecomDictFeature(tokTag, hr, featureVals = {}):
    """
    Telecom Dict feature
    """

    #featureVals = countNGInTelecomDict(tokTag, hr, featureVals)
    featureVals = countNGInDomainDict(tokTag, hr, featureVals)
    ncount = featureVals['countNGInDomainDict']

    ngname = 'NG In TELCOM Dict'
    lims = [1,3]
    collapse = [False, True]
    featureSets = {}
    for k in ncount:
        tdict = discVar2Feature(len(ncount[k]), k + ngname, lims = lims, collapse = collapse) #negative smiley
        featureSets.update(tdict.items())

    return (featureVals, featureSets)

def containsPolarNGFeature(tokTag, hr, featureVals = {}):
    """
    NG feature
    """
    featureVals = containsPolarNG(tokTag, hr, featureVals)
    ncount = featureVals['containsPolarNG']

    retval = dict()
    keystr = 'has %s Polar NG'
    for k in ncount:
        key = keystr % (k)
        retval[key] = ncount[k]

    featureSets = {}
    featureSets.update(retval)

    return (featureVals, featureSets)

def containsPolar2GFeature(tokTag, hr, featureVals = {}):
    """
    2G feature
    """
    featureVals = containsPolar2G(tokTag, hr, featureVals)
    ncount = featureVals['containsPolar2G']

    retval = dict()
    keystr = 'has %s Polar 2G'
    for k in ncount:
        key = keystr % (k)
        retval[key] = ncount[k]

    featureSets = {}
    featureSets.update(retval)

    return (featureVals, featureSets)

def containsPolar3GFeature(tokTag, hr, featureVals = {}):
    """
    2G feature
    """
    featureVals = containsPolar3G(tokTag, hr, featureVals)
    ncount = featureVals['containsPolar3G']

    retval = dict()
    keystr = 'has %s Polar 3G'
    for k in ncount:
        key = keystr % (k)
        retval[key] = ncount[k]

    featureSets = {}
    featureSets.update(retval)

    return (featureVals, featureSets)

def hasHapenningVerbsFeature(tokTag, hr, featureVals = {}):
    featureVals = hasHapenningVerbs(tokTag, hr, featureVals)
    fv = featureVals['hasHapenningVerbs']
    retval = {}
    retval['hasHapenningVerbs'] = fv

    featureSets = {}
    featureSets.update(retval)
    return (featureVals, featureSets)

def hasSoftVerbsFeature(tokTag, hr, featureVals = {}):
    featureVals = hasSoftVerbs(tokTag, hr, featureVals)
    fv = featureVals['hasSoftVerbs']
    retval = {}
    retval['hasSoftVerbs'] = fv

    featureSets = {}
    featureSets.update(retval)
    return (featureVals, featureSets)

def hasProbNounFeature(tokTag, hr, featureVals = {}):
    featureVals = hasProbNoun(tokTag, hr, featureVals)
    fv = featureVals['hasProbNoun']
    retval = {}
    retval['hasProbNoun'] = fv

    featureSets = {}
    featureSets.update(retval)
    return (featureVals, featureSets)

############################inserted by shardul
def notHapenningVerbsFeature(tokTag, hr, featureVals = {}):
    featureVals = notHapenningVerbs(tokTag, hr, featureVals)
    fv = featureVals['notHapenningVerbs']
    retval = {}
    retval['notHapenningVerbs'] = fv

    featureSets = {}
    featureSets.update(retval)
    return (featureVals, featureSets)

def PhrasalVerbsFeature(tokTag, hr, featureVals = {}):
    featureVals = PhrasalVerbs(tokTag, hr, featureVals)
    fv = featureVals['PhrasalVerbs']
    retval = {}
    retval['PhrasalVerbs'] = fv

    featureSets = {}
    featureSets.update(retval)
    return (featureVals, featureSets)

def act_behaveFeature(tokTag, hr, featureVals = {}):
    featureVals = act_behave(tokTag, hr, featureVals)
    fv = featureVals['act_behave']
    retval = {}
    retval['act_behave'] = fv

    featureSets = {}
    featureSets.update(retval)
    return (featureVals, featureSets)

def adDetectionFeature(procTxt, hr, featureVals = {}):
    retval = {}
    featureVals = adDetection(procTxt, hr, featureVals)
    fv = featureVals['adDetection']
    retval['isAd'] = fv

    featureSets = {}
    featureSets.update(retval)
    return (featureVals, featureSets)
    
###############################33
def isAdFeature(procTxt, hr, featureVals = {}):
    retval = {}
    featureVals = isPolAd(procTxt, hr, featureVals)
    retval = featureVals['isPolAd']

#    featureVals = netPosteriorPolarChunks(procTxt, hr, featureVals)
#    cnt = featureVals['netPosteriorPolarChunks']
#    isad = procTxt['isAd'][0]
#    #print cnt, isad
#    retval['isAdPOS'] = False
#    if cnt > 0 and isad:
#        retval['isAdPOS'] = True
#    retval['isAdNEG'] = False
#    if cnt < 0 and isad:
#        retval['isAdNEG'] = True

    featureSets = {}
    featureSets.update(retval)
    return (featureVals, featureSets)

def exclamationFeature(tokTag, hr, featureVals = {}):
    featureVals = exclamation(tokTag, hr, featureVals)
    fv = featureVals['exclamation']
    retval = {}
    retval['exclamation'] = fv

    featureSets = {}
    featureSets.update(retval)
    return (featureVals, featureSets)

_DF_KEY = 'dollar'
def dollarFeature(tokTag, hr, featureVals = {}):
    featureVals = dollar(tokTag, hr, featureVals)
    fv = featureVals[_DF_KEY]
    retval = {}
    retval[_DF_KEY] = fv

    featureSets = {}
    featureSets.update(retval)
    return (featureVals, featureSets)

def periodFeature(tokTag, hr, featureVals = {}):
    featureVals = period(tokTag, hr, featureVals)
    fv = featureVals['period']
    retval = {}
    retval['period'] = fv

    featureSets = {}
    featureSets.update(retval)
    return (featureVals, featureSets)

def questionFeature(tokTag, hr, featureVals = {}):
    featureVals = question(tokTag, hr, featureVals)
    fv = featureVals['question']
    retval = {}
    retval['question'] = fv

    featureSets = {}
    featureSets.update(retval)
    return (featureVals, featureSets)

def probnounapproxFeature(tokTag, hr, featureVals = {}):
    featureVals = probnounapprox(tokTag, hr, featureVals)
    fv = featureVals['probnounapprox']
    retval = {}
    retval['probnounapprox'] = fv

    featureSets = {}
    featureSets.update(retval)
    return (featureVals, featureSets)


def act_behaveapproxFeature(tokTag, hr, featureVals = {}):
    featureVals = act_behaveapprox(tokTag, hr, featureVals)
    fv = featureVals['act_behaveapprox']
    retval = {}
    retval['act_behaveapprox'] = fv

    featureSets = {}
    featureSets.update(retval)
    return (featureVals, featureSets)

def phrasalapproxFeature(tokTag, hr, featureVals = {}):
    featureVals = phrasalapprox(tokTag, hr, featureVals)
    fv = featureVals['phrasalapprox']
    retval = {}
    retval['phrasalapprox'] = fv

    featureSets = {}
    featureSets.update(retval)
    return (featureVals, featureSets)

def domainwordFeature(tokTag, hr, featureVals = {}):
    featureVals = domainword(tokTag, hr, featureVals)
    fv = featureVals['domainword']
    retval = {}
    retval['domainword'] = fv

    featureSets = {}
    featureSets.update(retval)
    return (featureVals, featureSets)
##############################################################################

def degenerate_sentFeature(tokTag, hr, featureVals = {}):
    featureVals = degenerate_sent(tokTag, hr, featureVals)
    fv = featureVals['degenerate_sent']
    retval = {}
    retval.update(discVar2Feature(fv, 'degeneratesentences', lims = [1,1], collapse = [False, True]))
    #retval['degenerate_sent'] = fv

    featureSets = {}
    featureSets.update(retval)

    return (featureVals, featureSets)


def singleword_sentFeature(tokTag, hr, featureVals = {}):
    featureVals = singleword_sent(tokTag, hr, featureVals)
    fv = featureVals['singleword_sent']
    retval = {}
    retval.update(discVar2Feature(fv, 'singleverbsentences', lims = [1,1], collapse = [False, True]))
    #retval['singleword_sent'] = fv

    featureSets = {}
    featureSets.update(retval)

    return (featureVals, featureSets)


def multiverb_sentFeature(tokTag, hr, featureVals = {}):
    featureVals = multiverb_sent(tokTag, hr, featureVals)
    fv = featureVals['multiverb_sent']
    retval = {}
    retval.update(discVar2Feature(fv, 'multiverbsentences', lims = [1,1], collapse = [False, True]))
    #retval['multiverb_sent'] = fv

    featureSets = {}
    featureSets.update(retval)
    return (featureVals, featureSets)

from ppd import hasNegatedDomainNouns
def txtContainsNegatedDomainNounFeature(procTxt, hr, featureVals = {}):
    featureVals = hasNegatedDomainNouns(procTxt, hr, featureVals)
    retVal = featureVals['hasNegatedDomainNouns']

    rv = 0
    if retVal:
        rv = 1
    featureSets = {}
    featureSets.update({'negatedDomainNoun':rv})
    return (featureVals, featureSets) 
    
    
from problem_phrases import problemPhraseBases
def problemPhraseBasesFeature(procTxt, hr, featureVals = {}):
    featureVals = problemPhraseBases(procTxt, hr, featureVals)
    retVal = featureVals['problemPhraseBases']

    featureSets = {}
    featureSets.update(retVal)
    return (featureVals, featureSets) 
    
def countPolarChunksInClausedSentencesFeature(procTxt, hr, featureVals = {}):
    featureVals = countPolarChunksInClausedSentences(procTxt, hr, featureVals)
    cnt = featureVals['countPolarChunksInClausedSentences']

    retdict = dict()
    for key, val in cnt.iteritems():
        retdict.update(discVar2Feature(val, key, lims = [1,3], collapse = [False, True]))

    featureSets = {}
    featureSets.update(retdict)
    return (featureVals, featureSets)

def countPosteriorPolarChunksFeature(procTxt, hr, featureVals = {}):
    featureVals = countPosteriorPolarChunks(procTxt, hr, featureVals)
    cnt = featureVals['countPosteriorPolarChunks']

    retdict = dict()
    for key, val in cnt.iteritems():
        retdict.update(discVar2Feature(val, key, lims = [1,3], collapse = [False, True]))

    featureSets = {}
    featureSets.update(retdict)
    return (featureVals, featureSets)

def netPosteriorPolarChunksFeature(procTxt, hr, featureVals = {}):
    featureVals = netPosteriorPolarChunks(procTxt, hr, featureVals)
    cnt = featureVals['netPosteriorPolarChunks']

    #print cnt
    retdict = dict()
    retdict.update(discVar2Feature(cnt, 'netPosteriorPolarChunks', lims = [-1,3], collapse = [False, True]))

    featureSets = {}
    featureSets.update(retdict) #{'NPP':cnt})
    return (featureVals, featureSets)


def countPolarChunksFeature(procTxt, hr, featureVals = {}):
    featureVals = countPolarChunks(procTxt, hr, featureVals)
    cnt = featureVals['countPolarChunks']

    retdict = dict()
    for chtype in TPC_CHUNKTYPES:
        for pol in TPC_POLTYPES:
            key = chtype+pol
            retdict.update(discVar2Feature(cnt[key], key, lims = [1,3], collapse = [False, True]))

    featureSets = {}
    featureSets.update(retdict)
    return (featureVals, featureSets)

def netPolarChunksFeature(procTxt, hr, featureVals = {}):
    featureVals = netPolarChunks(procTxt, hr, featureVals)
    cnt = featureVals['netPolarChunks']

    #print cnt
    retdict = dict()
    retdict.update(discVar2Feature(cnt, 'netPolarChunks', lims = [-1,1], collapse = [False, True]))

#    for chtype in TPC_CHUNKTYPES:
#        for pol in TPC_POLTYPES:
#            key = chtype+pol
#            retdict.update(discVar2Feature(cnt[key], key, lims = [1,3], collapse = [False, True]))

    featureSets = {}
    featureSets.update(retdict)
    return (featureVals, featureSets)

#def periodFeature(tokTag, hr, featureVals = {}):
#    featureVals = period(tokTag, hr, featureVals)
#    fv = featureVals['period']
#    retval = {}
#    retval['period'] = fv
#
#    featureSets = {}
#    featureSets.update(retval)
#    return (featureVals, featureSets)

def txtContainsProfanityFeature(procTxt, hr, featureVals = {}):
    featureVals = txtContainsProfanity(procTxt, hr, featureVals)
    retVal = featureVals['txtContainsProfanity']

    featureSets = {}
    featureSets.update({'HasProfanity':retVal})
    return (featureVals, featureSets)
###########################################################
def hasIntensifierFeature(procTxt, hr, featureVals = {}):
    featureVals = hasIntensifier(procTxt, hr, featureVals)
    intense_value = featureVals['hasIntensifier']
    featureSets = {}
    intensifierdict ={}
    intensifierdict.update(discVar2Feature(intense_value, 'hasIntensifier', lims = [1,1],collapse = [False, True]))
    featureSets.update(intensifierdict)
    return (featureVals, featureSets)


#############################################################
def positiveinterjectionFeature(procTxt, hr, featureVals = {}):
    featureVals = positiveinterjection(procTxt, hr, featureVals)
    retVal = featureVals['positiveinterjection']

    featureSets = {}
    featureSets.update({'positiveinterjection':retVal})
    return (featureVals, featureSets)

def negativeinterjectionFeature(procTxt, hr, featureVals = {}):
    featureVals = negativeinterjection(procTxt, hr, featureVals)
    retVal = featureVals['negativeinterjection']

    featureSets = {}
    featureSets.update({'negativeinterjection':retVal})
    return (featureVals, featureSets)

#########################################

def hashtag_calcFeature(procTxt, hr, featureVals = {}):


    featureVals = hashtag_calc(procTxt, hr, featureVals)
    retVal = featureVals['hashtag_calc']

    hashmaxpos = 'positivehashtag'
    hashmaxneg = 'negativehashtag'
    hashpol = 'negposhashtag'
    hashneu='neuhashtag'

    featureSets = {}
    neg_cou=retVal[0]
    pos_cou=retVal[1]


    if(neg_cou>0 and pos_cou==0):
        featureSets['hashtag'] = -1
    elif(neg_cou==0 and pos_cou>0):
        featureSets['hashtag']= 1
    elif(neg_cou>0 and pos_cou>0):
        featureSets['hashtag']= 2
    else:
        featureSets['hashtag']= 0

    return (featureVals, featureSets)

