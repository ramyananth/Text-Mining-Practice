#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 11:43:19 2017

@author: Tredence
"""

import sys, os, time, json, warnings
import cPickle as pickle
from itertools import imap, repeat
from collections import OrderedDict, Sequence, defaultdict
#from pkg_resources import resource_string, resource_filename
        
from Resources import makeDefaultResources
from MTNormalize import ptNormalize as MTNormalizer
from MTNormalize import clean_tags
#from MThttp_tagger import Tagger
from MTTagger import Tagger
#from MTTagger_zmq import Tagger

from processText import sentencifyAndChunk, sentenceSplitProcTxts 
from processText import updateTokenAndChunkProperties 

import MTservices_wrappers
from mine_text import computeFeatures, MTKEY_FEATURES

import re
__MT_PROD_HR__ = None
__MT_SERVICES__ = []
__MT_PYHOME__ = None
__MT_PKGNAME__ = None
__MT_CONFIG__ = None
_MT_TAGGER = None

MTCFG_NAME = 'name'
MTCFG_HR = 'hr'
MTCFG_RESFILES = 'resfiles'
MTCFG_CALL = 'call'
MTCFG_RESOURCES = 'resources'

def _getService(serviceName, logger=None): #it comes here
    """ Extract the service config for service name
    """
    for service in __MT_SERVICES__:
        if serviceName == service[MTCFG_NAME]:
            return service
    return None
    
def mtInit(pkgName = 'mine_text', pyPath = None, logger=None):
    """
    """
    if logger:
        logger('Initiliazing ...\n')
        st = time.time() 
        
    global __MT_PROD_HR__
    global __MT_SERVICES__
    global __MT_PYHOME__
    global __MT_PKGNAME__
    global __MT_CONFIG__
    global _MT_TAGGER

    pyPath = '/'.join(os.path.abspath(__file__).split('/')[:-1])
    os.environ['MINE_TEXT_HOME'] = pyPath
        
    if logger: logger('%s\n' % os.environ['MINE_TEXT_HOME'])

    __MT_PYHOME__ = os.environ['MINE_TEXT_HOME']    
    __MT_PKGNAME__ = pkgName

    #load resources:
    MTConfig = json.load(open(os.path.join(__MT_PYHOME__,'prod/MTservices_config.json'), 'r'))
    
    __MT_PROD_HR__ = [makeDefaultResources(__MT_PYHOME__)]
    print "PROD_HR__"
    print __MT_PROD_HR__
    
    
    for k, item in enumerate(MTConfig):
        resources = []
        if item.has_key(MTCFG_RESFILES) and item[MTCFG_RESFILES]:
            for r, resfile in enumerate(item[MTCFG_RESFILES]):
                fname = os.path.join(__MT_PYHOME__,resfile)
                res = pickle.load(open(fname, 'r'))
                resources.append(res)
        else:
            MTConfig[k][MTCFG_RESFILES] = []

        MTConfig[k][MTCFG_RESOURCES] = resources

        if item.has_key(MTCFG_CALL):
            MTConfig[k][MTCFG_CALL] = getattr(MTservices_wrappers, MTConfig[k][MTCFG_CALL])

#        if item[MTCFG_NAME] == MTCFG_HR:
#            __MT_PROD_HR__ = MTConfig[k][MTCFG_RESOURCES]
#        else:
#            __MT_SERVICES__.append(MTConfig[k])

        __MT_SERVICES__.append(MTConfig[k])
         
    __MT_CONFIG__ = MTConfig
    
    if not _MT_TAGGER:
        _MT_TAGGER = Tagger()

    if logger:
        logger('Done. (%5.4fs)\n' % (time.time()-st))
    
    return 1

def mtGetServiceNames():
    """ 
    List all available mine_text services.
    """
    if not __MT_CONFIG__:
        warnings.warn('mine_text is not initialized')
        return None
        
    return [service[MTCFG_NAME] for service in __MT_SERVICES__]
    
def mtPrintConfig(logger=None):
    """
    Print the status of the MTservices configuration.
    """
    if not logger:
        logger = sys.stdout.write
      
    if not __MT_CONFIG__:
        logger('\nmeta.classifier not initialized.\n')
        return -1
        
    logger('%s' % '='*80); logger('\n')
    logger('Package Name: %s\n' % __MT_PKGNAME__)
    logger('Location: %s\n' % __MT_PYHOME__)
    logger('Resources & Models:\n')
        
    for k, item in enumerate(__MT_CONFIG__):
        if item[MTCFG_NAME] == 'hr':
            if __MT_PROD_HR__ == item[MTCFG_RESOURCES]:
                for r, resfile in enumerate(item[MTCFG_RESFILES]):
                    fname = os.path.join(__MT_PYHOME__,resfile)
                    stats = os.stat(fname)
                    logger('%-30s LOADED: %-8d bytes, %s, %s\n' %
                    (item[MTCFG_NAME], stats.st_size, time.asctime(time.localtime(stats.st_mtime)), resfile))

    for k, item in enumerate(__MT_SERVICES__):
        if item.has_key(MTCFG_RESFILES) and item[MTCFG_RESFILES]:
            for r, resfile in enumerate(item[MTCFG_RESFILES]):
                fname = os.path.join(__MT_PYHOME__,resfile)
                stats = os.stat(fname)
                try:
                    ctime = item[MTCFG_RESOURCES][r]['createdon']
                except:
                    ctime = time.asctime(time.localtime(stats.st_mtime))

                logger('%-30s LOADED: %-8d bytes, %s, %s\n' %
                (item[MTCFG_NAME], stats.st_size, ctime, resfile))
        else:
            logger('%-30s No Models\n' % item[MTCFG_NAME])

        if item[MTCFG_NAME] == MTCFG_HR:
            logger('HR in Services')

    logger('%s' % '='*80); logger('\n')
    return 0


def mtNormTxt(txt):
    """
        Normalized token and tags
    """    
    if not isinstance(txt, basestring):
        raise TypeError('MTPipeline: Input must be a string.\n Input:%s ' % txt)
        
    if not txt:
        return {}
        
    txt = MTNormalizer([txt])
    if not txt[0]:
        return {}
        
    normTxt = _MT_TAGGER.getTags(txt[0]) 
    clean_tags(normTxt)

    return normTxt

def mtProcTxt(normtxt):
    procTxt = sentencifyAndChunk([normtxt], __MT_PROD_HR__[0])[0]
    procTxt = updateTokenAndChunkProperties(procTxt, __MT_PROD_HR__[0])
    return procTxt   
    
def _mtNLPipeline(txt): #it comes here
    """
    """    
    if not isinstance(txt, basestring):
        raise TypeError('MTPipeline: Input must be a string.\n Input:%s ' % txt)
        
    if not txt:
        return {}
    
    #print "Original",txt
    txt = MTNormalizer([txt])
    #print "Normalized",txt
    if not txt[0]:
        return {}
        
    procTxt = _MT_TAGGER.getTags(txt[0]) 
    #print "First",procTxt
    clean_tags(procTxt)
    #print "Second",procTxt
    procTxt = sentencifyAndChunk([procTxt], __MT_PROD_HR__[0])[0]
    #print "Third",procTxt
    procTxt = updateTokenAndChunkProperties(procTxt, __MT_PROD_HR__[0])
    #print "Fourth",procTxt
    return procTxt    
    
def _mtPipeline(procTxt, reqServices):
    """
    """
    if not procTxt:
        return {}
        
    allFeatures = set()
    for service in reqServices:
        #print "reqServices" ,reqServices
        for serRes in service[MTCFG_RESOURCES]:
            allFeatures = allFeatures.union(serRes[MTKEY_FEATURES])
    #print "FEATURES",allFeatures

    computedFeatures, featureVals = computeFeatures(procTxt, __MT_PROD_HR__[0], allFeatures, True)
    #print "COMPUTEFEATURES",computedFeatures
    #print "AAAAAAAAAAAAAAA",featureVals
    results = {}
    for service in reqServices:
        sname = service[MTCFG_NAME]
        scall = service[MTCFG_CALL] #scall = globals()[service[MTCFG_CALL]]
        smdl = service[MTCFG_RESOURCES]
        #print "PROD_HR__"
        #print __MT_PROD_HR__[0]
        result = scall(procTxt, __MT_PROD_HR__, smdl, computedFeatures, featureVals)
        results[sname] = result

    return results
    
def _getServicesConfig(snames): #it comes here
    """
    """
    #print snames
    if snames:
        if isinstance(snames, basestring):
            snames = [snames]
        elif not hasattr(snames, '__iter__'): 
            raise TypeError('Service names must be a string or iterable. \n Input:%s ' % snames)

        snames = list(OrderedDict.fromkeys(snames)) #unique order preserving list (removes duplicate service names)
        services = [_getService(sname) for sname in snames]
        if not all(services):
            badServiceNames = ['%s' % snames[k] for k, service in enumerate(services) if not service]
            raise Exception("MTRunServices: Unknown Service requested: %s" % badServiceNames)
    else: # collect config of all availables services.
        services = [_getService(service[MTCFG_NAME]) for service in __MT_SERVICES__ if service['defaultService']]
    return services
    
def mtRunServices(txts, serviceNames=None): #it comes here
    """ 
    """
    retval = []
    if isinstance(txts, basestring):
        txts = [txts]
    elif not isinstance(txts, Sequence):
        raise TypeError('MTRunServices: Input must be a string or iterable. \n Input:%s ' % txts)
    
    services = _getServicesConfig(serviceNames)
    #print "SEERVICES"
    #print services
    
    ntxt = txts.__len__()
    #print "TEEEXT"
    #print txts
    procTxts = imap(_mtNLPipeline, txts)
    #print "Proooc"
    #print list(procTxts)    
    MTp = imap(_mtPipeline, procTxts, repeat(services, ntxt))
    #print "MTTP"
    #print list(MTp)  
    retval = [m for m in MTp]
    #print "RETVAL"
    #print retval
    return retval

def mtSentences(txt, serviceNames = None):
    """
    Analyse text by sentences.
    
    """
    retval = []
    if not isinstance(txt, basestring):
        raise TypeError('MTSentences: txt must be a string \n Input:%s ' % txt)
    
    services = _getServicesConfig(serviceNames)
    
    procTxt = _mtNLPipeline(txt)
    sprocTxts = sentenceSplitProcTxts(procTxt)
    ntxt = sprocTxts.__len__()
    MTp = imap(_mtPipeline, sprocTxts, repeat(services, ntxt))
    retval = [m for m in MTp]
    return retval    
    
