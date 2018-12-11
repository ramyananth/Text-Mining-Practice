#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 16:20:34 2017

@author: Tredence
"""

from ptdatatypes import *
def proctxt2tt(proctxt):
    '''
    '''
    tt = []
    for s, sentence in enumerate(proctxt['chunksInClauses']):
        for c, clause in enumerate(sentence):
            for h, chunk in enumerate(clause):
                for tok, tag in zip(chunk.tokens, chunk.tags):
                    tt.append('%s/%s' % (tok, tag))

    tt = ' '.join(tt)                   
    return tt
    

