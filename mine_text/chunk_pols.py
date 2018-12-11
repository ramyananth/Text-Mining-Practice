#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 16:22:10 2017

@author: Tredence
"""

#from token_properties import tokenLexicalProps, updateTokenLexicalProperties
from token_properties import TLP_INTENSIFIER, TLP_REDUCER, TLP_NEGATOR
from token_properties import TLP_NINTENSIFIER
from Resources import RESKEY_SMILEYS
from appDefs import *
from collections import defaultdict

def defaultChunkPolarity(chunk, hr, logger=None):
    """
    """
    props = chunk.tprops #tokenLexicalProps(chunk, hr)
    toks = chunk.tokens
    tags = chunk.tags
    pols = chunk.pols

    intensifier = [tokpr[TLP_INTENSIFIER] for tokpr in props] #lexprop['intensifier']
    reducer = [tokpr[TLP_REDUCER] for tokpr in props] #lexprop['reducer']
    negator = [tokpr[TLP_NEGATOR] for tokpr in props] #lexprop['negator']

    chunkPol = 0
    for k, tok in reversed(list(enumerate(toks))):
        tag = tags[k]
        if not (intensifier[k] or reducer[k] or negator[k]):
            chunkPol += pols[k]
        elif intensifier[k]:
            if intensifier[k] == 1:
                chunkPol = 2*chunkPol
            elif intensifier[k] == 2:
                if chunkPol > 0:
                    chunkPol = -2*chunkPol
                elif chunkPol == 0:
                    chunkPol = -1
                else:
                    chunkPol = 2*chunkPol
            elif intensifier[k] == 3:
                if chunkPol >= 0:
                    chunkPol = 2*chunkPol

        elif reducer[k]:
            chunkPol = 0.5*chunkPol
        elif negator[k]:
            #print toks
            chunkPol = -1*chunkPol

    ## if only intensifiers then consider their prior-pols.
    iidx = [i for i, val in enumerate(intensifier) if val]
    nidx = [i for i, val in enumerate(negator) if val]
    if iidx and chunkPol == 0:
        ipols = [pols[i] for i in iidx]
        chunkPol = sum(ipols)

    negatorF = False
    if nidx:
        negatorF = True
    #print nidx, negator, negatorF
    if logger:
        logger('%s %s %s\n' % (chunk, chunkPol, negatorF))

    chunkProps = {'pol': chunkPol, 'negn': negatorF} #, 'tokProps': props}
    return chunkProps #{'pol': chunkPol, 'negn': negatorF}

def __nounChunkPolarity(chunk, hr, logger=None):
    """
    """
    props = chunk.tprops #tokenLexicalProps(chunk, hr)
    toks = chunk.tokens
    tags = chunk.tags
    pols = chunk.pols

    intensifier = [tokpr[TLP_INTENSIFIER] for tokpr in props] #lexprop['intensifier']
    reducer = [tokpr[TLP_REDUCER] for tokpr in props] #lexprop['reducer']
    negator = [tokpr[TLP_NEGATOR] for tokpr in props] #lexprop['negator']
    nintensifier = [tokpr[TLP_NINTENSIFIER] for tokpr in props]
    
    chunkPol = 0
    for k, tok in reversed(list(enumerate(toks))):
        tag = tags[k]

        conflictFlag = False
        if abs(chunkPol) > 0 and abs(pols[k]) > 0 and chunkPol != pols[k]: #polar opposites
            conflictFlag = True
            if tag in POSKEY_ADJ and nintensifier[k]:
                #print 'gets here'
                intensifier[k] += 1

        if not (intensifier[k] or reducer[k] or negator[k]):
            if conflictFlag:
                if tag in POSKEY_ADJ and pols[k]:
                    chunkPol = pols[k]
                else: #tag in 'N' disaster prevention
                    chunkPol = chunkPol
            else:
                chunkPol += pols[k]
        elif intensifier[k]:
            if intensifier[k] == 1:
                chunkPol = 2*chunkPol
            elif intensifier[k] == 2:
                if chunkPol > 0:
                    chunkPol = -2*chunkPol
                elif chunkPol == 0:
                    chunkPol = -1
                else:
                    chunkPol = 2*chunkPol
            elif intensifier[k] == 3:
                if chunkPol >= 0:
                    chunkPol = 2*chunkPol

        elif reducer[k]:
            chunkPol = 0.5*chunkPol
        elif negator[k]:
            #print toks
            chunkPol = -1*chunkPol

    ## if only intensifiers then consider their prior-pols.
    iidx = [i for i, val in enumerate(intensifier) if val]
    nidx = [i for i, val in enumerate(negator) if val]
    if iidx and chunkPol == 0:
        ipols = [pols[i] for i in iidx]
        chunkPol = sum(ipols)

    negatorF = False
    if nidx:
        negatorF = True

    if logger:
        logger('%s %s %s\n' % (chunk, chunkPol, negatorF))
    #return {'pol': chunkPol, 'negn': negatorF}
    chunkProps = {'pol': chunkPol, 'negn': negatorF} #, 'tokProps': props}
    return chunkProps #{'pol': chunkPol, 'negn': negatorF}

def getNONEChunkPolarity(chunk, hr, logger=None):
    hrr = hr.resources
    pols = []
    smiley = hrr[RESKEY_SMILEYS]
    smileyNeg = smiley.getDicts(1,KEY_POLARITY_NEGATIVE)
    smileyPos = smiley.getDicts(1,KEY_POLARITY_POSITIVE)

    for k, tok in enumerate(chunk.tokens):
        tag = chunk.tags[k]
        if tag in ['E']:
            if tok in smileyNeg:
                pols.append(-1)
            elif tok in smileyPos:
                pols.append(1)
    if logger:
        logger('%s %s %s\n' % (chunk, sum(pols), False))
    return {'pol': sum(pols), 'negn': False} #, 'tokProps':[defaultdict(int)]}


def __verbChunkPolarity(chunk, hr, logger=None): #i need to come back here

    rv = defaultChunkPolarity(chunk, hr, logger)
    if 'please' in chunk.tokens and rv['pol'] > 0:
        rv['pol'] = 0
    if 'if' in chunk.tokens and rv['pol'] > 0:
        rv['pol'] = 0

    return rv


def getChunkPolarity(chunk, hr,logger=None):

    chType = chunk.chunkType
    if chType == 'NONE':
        rv = getNONEChunkPolarity(chunk, hr, logger)
    elif chType == 'NP':
        rv = __nounChunkPolarity(chunk, hr, logger)
    elif chType == 'VP':
        rv =  __verbChunkPolarity(chunk, hr, logger) #__defaultChunkPolarity(chunk, hr, logger)
    elif chType == 'ADJP':
        rv = defaultChunkPolarity(chunk, hr, logger)
    elif chType == 'ADVP':
        rv = defaultChunkPolarity(chunk, hr,logger)
    else:
        rv = defaultChunkPolarity(chunk, hr, logger)
        
    chunk.chPol = rv['pol']
    chunk.hasNegator = rv['negn']
    return chunk
        
        

