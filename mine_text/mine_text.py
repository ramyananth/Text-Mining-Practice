# -*- coding: utf-8 -*-
"""
@author: Tredence
@maintainer:Tredence
"""
import nltk
import sklearn
from nltk.classify.maxent import MaxentClassifier as nltkmec
from sklearn.linear_model import LogisticRegression as lr
from collections import defaultdict
import operator
from mine_text_utils import computeFeatures, makeSKFormat
MTKEY_LABEL = 'label'
MTKEY_SCORES = 'scores'
MTKEY_CLASSIFIER = 'classifier'
MTKEY_FEATURES = 'features'
MTKEY_PRDLABELS = 'prdLabels'

def _get_SKLR_ProbPredictions(bases, classifier, prdLabels):
    """
    Wrapper for SKLEARN Logistic Regression Predictions.
    Performs bases transformation to list of lists, calls appropriate method, and
    unpacks the results in the {label_1: Pr_1, label_2: Pr_2, ...} format.
    """
    #print("###############")
    global write_file
    global flag_headings
    global flag_count
    bases , basesNames= makeSKFormat([bases],returnBasisNames=True)
    #print "CCCCCCLAA"
    #print classifier
    #print "BB",bases
    #print "basesNames",basesNames
    tp = classifier.predict_proba(bases)
    #print "tp",tp
    rdict = {lbl:tp[0][k] for k, lbl in enumerate(prdLabels)}
    return rdict

def _get_ME_ProbPredictions(bases, classifier, prdLabels):
    """
    Wrapper for NLTK Maxent Predictions
    Calls appropriate method, and
    unpacks the results in the {label_1: Pr_1, label_2: Pr_2, ...} format.
    """
    classifyMethod = classifier.prob_classify
    tp = classifyMethod(bases)
    rdict = {lbl:tp.prob(lbl) for lbl in prdLabels}
    return rdict

from clause_pol import clausePolarity
import sys
from config import PTKEY_CHUNKEDCLAUSES
def getProbPredictions(procTxt, hr, model, computedFeatures = None, dbg = False):
    """
    Entry point for probabilistic classifier predictions.
    """
    
    if not procTxt:
        return ['NA']

    classifier = model[MTKEY_CLASSIFIER]
    featureNames = model[MTKEY_FEATURES]
    prdLabels = model[MTKEY_PRDLABELS]

    if not computedFeatures:
        computedFeatures = computeFeatures(procTxt, hr, featureNames)

    bases = {}
    for feature in featureNames:
        bases.update(computedFeatures[feature])

    if type(classifier) == nltk.classify.maxent.MaxentClassifier:
        rdict = _get_ME_ProbPredictions(bases, classifier, prdLabels)
    elif type(classifier) == sklearn.linear_model.logistic.LogisticRegression:
        rdict = _get_SKLR_ProbPredictions(bases, classifier, prdLabels)

    retval = {MTKEY_SCORES: rdict, MTKEY_LABEL: max(rdict, key=rdict.get)}

    return retval


