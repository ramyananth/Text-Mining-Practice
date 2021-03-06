#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Script to benchmark a model against available data sets.
Usage:
Set the [modelname] to approriate model in inst/python/model/
modelname = 'newdbg'
Run script

#!/usr/bin/env python2
# -*- coding: utf-8 -*-
Created on Mon Mar 20 16:22:10 2017

@author: Tredence


"""
import sys, time
from collections import defaultdict
import operator
import cPickle as pickle

import utils_gen as ug
from config import DEFAULT_HR_FILE, MT_DATA_HOME, MT_MODELS_HOME, MT_LOGS_HOME
from config import PTKEY_CHUNKEDCLAUSES
from mine_text import getProbPredictions, MTKEY_LABEL, MTKEY_SCORES
from mine_text_utils import computeFeatures

from processText import PTKEY_TOKENS, PTKEY_TAGS
from processText import updateTokenAndChunkProperties
from chunk_pols import getChunkPolarity #, updateChunkPolarities
from clause_props import questionsInProcTxt
from clause_pol import clausePolarity
from cm import ClassifierMetrics

benchmarkSA = 1

if benchmarkSA:
    tst_data_names = ['evaldata/data_semeval_6399_train']
    tst_data_names = ['evaldata/data_merged_2854_test']
    #tst_data_names = ['cmpdata/TrainingData2']
    #tst_data_names = ['AttensityTestData']
    #tst_data_names = ['data_merged_2854_test', 'AttensityTestData'] #'data_semeval_1009_test',
    modelname = 'SAModel042_RTRN_BestModel' #NLTK Model
#    modelname = 'SALR_SEMEVAL_NB2' #SKLEARN Model
#    modelname = 'SA_NewMTTrain_ChunkSKLR'
    modelname = 'SA_ChunkNew2SKLR'
    #modelname = 'SAModel041ChunkAndCoreTstSmiley'
    #modelname = 'SAModel042_ChunkTest2' #'SAModel042_Test'
    #modelname = 'SAModel042_TestCoreAndChunk'
    if len(tst_data_names) > 1:
        elogfile = open(MT_LOGS_HOME + 'errchlog_sat' + '.txt','w') # + strftime("_%y%m%d_%H%M%S")
    else:
        elogfile = open(MT_LOGS_HOME + 'errchlog_sat'+ tst_data_names[0].split('/')[-1] + '.txt','w') # + strftime("_%y%m%d_%H%M%S")
else:
    tst_data_names = ['ptd/data_ptd_test']
    tst_data_names = ['ptd/coechatsamples25']
    modelname = 'PD_VPAnalysis4SKLR' #'PDModelOnlyNewCU'
#    modelname = 'PD_New2ChunksNewNoMV2SKLR'
    elogfile = open(MT_LOGS_HOME + 'errlog_pa'+ '.txt','w')

##############################################################################
elogprint = elogfile.write

def printErrorLogs(truLabels, MTPrd, procTxts, computedFeatures, truLbl=None, prdLbl=None, printer = sys.stdout.write):
    
    hr = pickle.load(open(DEFAULT_HR_FILE))    
    if not printer:
        printer = sys.stdout.write

    prdLabels  = [MTp[MTKEY_LABEL] for MTp in MTPrd]
    prdScores = [MTp[MTKEY_SCORES] for MTp in MTPrd]

    if truLbl and (not prdLbl):
        errIdx = [k for k, tru in enumerate(truLabels)
                    if tru == truLbl and prdLabels[k] != truLbl]
    elif (not truLbl) and (prdLbl):
        errIdx = [k for k, tru in enumerate(truLabels)
                    if prdLabels[k] == prdLbl and tru != prdLbl]
    else:
        errIdx = [k for k, prd in enumerate(prdLabels) if truLabels[k] == truLbl and prd != truLbl]

    errLog = [(k, truLabels[k], prdLabels[k]) for k in errIdx]
    errLog.sort(key = operator.itemgetter(1, 2))

    for item in errLog:
        k = item[0]
        printer('ID:%d\tTru:%s\tPrd:%s\n' % (item[0], item[1], item[2]))
        for key, val in prdScores[k].iteritems():
            printer('%s:%6.5f ' % (key, val))
        printer('\n')

        procTxt = procTxts[k]
        eb = computedFeatures[k]
        for tok, tag in zip(procTxt[PTKEY_TOKENS], procTxt[PTKEY_TAGS]):
            printer('%s/%s ' % (tok, tag))
        printer('\n')

        isq = questionsInProcTxt(procTxt, hr)
#        print isq

        chunkedSentences = procTxt[PTKEY_CHUNKEDCLAUSES]
        for s, chunkedSentence in enumerate(chunkedSentences):
            for c, clause in enumerate(chunkedSentence):
                chPat, pols, negn, negtd = clausePolarity(clause, hr, printer)
                printer('CLAUSE: %s\n' % clause)
                printer('POLS: %s\n' % pols)
                printer('NEGN: %s\n' % negn)
                printer('NEGTD: %s\n' % negtd)
                printer('isQ:%s\n' % isq[s])
                printer('-\n')

        for featureFuncName, features in eb.iteritems():
            for feature, val in features.iteritems():
                if val:
                    printer('%s %s\n' % (feature, val))
        printer('\n')

##############################################################################

### Load model
model = pickle.load(open(MT_MODELS_HOME + modelname + '.msmdl'))
featureNames = model['features']
### Load Resources
hr = pickle.load(open(DEFAULT_HR_FILE))
cm = ClassifierMetrics(model['prdLabels']) #initialize metrics object

sys.stdout.write('Model\t%s\n'% (modelname))

for tst_data_name in tst_data_names:
    trusents = [sent.lower()
            for sent in ug.readlines(MT_DATA_HOME + tst_data_name + '.lbls')]
    procTxtLst = pickle.load(open(MT_DATA_HOME + tst_data_name+'.proctxts'))

    sys.stdout.write('Computing...\t')

    tt = time.time()
    MTPredictions = []
    computedFeaturesArray = []
    for procTxt in procTxtLst:
        procTxt = updateTokenAndChunkProperties(procTxt, hr)
        computedFeatures = computeFeatures(procTxt, hr, featureNames)
        MTp = getProbPredictions(procTxt, hr, model, computedFeatures)
        MTPredictions.append(MTp)
        computedFeaturesArray.append(computedFeatures)

    print('%f secs\n' % float(time.time() - tt))

    prdsents  = [MTp[MTKEY_LABEL] for MTp in MTPredictions]
#    prdScores = [MTp[MTKEY_SCORES] for MTp in MTPredictions]
#
#    for i, prdsent in enumerate(prdsents):
#        if procTxtLst[i]['isAd'][0] and prdsent != 'neutral':
#            prdsents[i] = 'neutral'

#    plbls = [ '%s\t%s' % (tr, pr) for tr, pr in zip(trusents, prdsents)]
##    ug.writelines(plbls, MT_DATA_HOME + modelname +'_'+ tst_data_name + '.res')
#
    cm.computeMetrics(trusents, prdsents)
    cm.printMetrics()
#
    printErrorLogs(trusents, MTPredictions, procTxtLst,
                   computedFeaturesArray, truLbl = '1', prdLbl = '1', printer = elogprint)

elogfile.close()





