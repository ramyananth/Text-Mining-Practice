#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue May 16 19:03:09 2017

@author: Tredence
"""


from mine_text_utils import computeFeatures
from nltk.tokenize import word_tokenize
import pickle


import sys
import os
from subprocess import check_output

home = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


#importing the models temporarily here
base_path = "/".join((home,"mine_text/models/"))
dictionary = pickle.load(open("".join((base_path,"dictionary.pickle")),"rb"))
classifier = pickle.load(open("".join((base_path,"NB_model_combined.pickle")),"rb"))




allFeatures = {'act_behaveapproxFeature',
 'countPosteriorPolarChunksFeature',
 'countSmileyFeature',
 'dollarFeature',
 'exclamationFeature',
 'hasIntensifierFeature',
 'hashtag_calcFeature',
 'isAdFeature',
 'negativeinterjectionFeature',
 'netPosteriorPolarChunksFeature',
 'periodFeature',
 'phrasalapproxFeature',
 'positiveinterjectionFeature',
 'problemPhraseBasesFeature',
 'probnounapproxFeature',
 'questionFeature',
 'txtContainsNegatedDomainNounFeature',
 'txtContainsProfanityFeature'}
 

def text_sentiment_lenovo(proctxt, hr):

    features = computeFeatures(proctxt,hr,allFeatures,False)  
    bases = {}
    for feature in allFeatures:
        bases.update(features[feature])
        
    t = [{word: word in word_tokenize(x) for word in dictionary} for x in [proctxt["sentences"][0].tokString()]]
    t[0].update(bases)  
    result = {}
    result["result"] = classifier.classify(t[0])
    prob = classifier.prob_classify(t[0])
    result["scores"] = {"positive":prob.prob("positive"),"neutral":prob.prob("neutral"),"negative":prob.prob("negative")}    
    return result
    
    
    
