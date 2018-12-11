#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 16:22:10 2017

@author: Tredence
"""

from collections import Counter
from config import *
from token_properties import *
__STYPE_DG__ = 'degenerate'
__STYPE_SV__ = 'singleverb'
__STYPE_MV__ = 'multiverb'

DEGEN_CONJUNCTIONS = set(['but', 'yet'])
def degenerateClauseAnalysis(chunklist, hr, logger = None):
    """
    degenerate clause breakdown so as to localize the polarity for entities.
    #1. we can break degen clauses on conjunctions.
        for eg., 
        clause = [NP(5/$ bars/N), NONE(,/,), NP(3g/$ sign/N), NONE(n/&), ADVP(yet/R), NONE(-/,), NP(no/D internet_NG_connection/N), NONE(./,)]
        can be broken to list of conj clause lists
        conjClause = [[NP(5/$ bars/N), NONE(,/,), NP(3g/$ sign/N), NONE(n/&)], [ADVP(yet/R), NONE(-/,), NP(no/D internet_NG_connection/N), NONE(./,)]]
    #2. with such conj clauses break down on conjunctions.    
        [NP(no/D service/N aboveground/N), PP(at/P), NP(the/D jamba/^ juice/^), NONE(,/,), NONE(but/&), ADJP(underground/A), PP(on/P), NP(the/D subway/N platform/N solid/A coverage/N), NONE(./,)]
        -->cc [NP(no/D service/N aboveground/N), PP(at/P), NP(the/D jamba/^ juice/^), NONE(,/,)]
        -->-->pp [NP(no/D service/N aboveground/N)]
        -->-->pp [PP(at/P), NP(the/D jamba/^ juice/^), NONE(,/,)]
        -->cc [NONE(but/&), ADJP(underground/A), PP(on/P), NP(the/D subway/N platform/N solid/A coverage/N), NONE(./,)]
        -->-->pp [NONE(but/&), ADJP(underground/A), PP(on/P), NP(the/D subway/N platform/N solid/A coverage/N), NONE(./,)]        
    
    retval 
    dga = list of conjclauses
    conjclauses = list of pp clauses.
    for conjclause in dga:
        for ppclause in conjclause
    """
    ignoreThis = len(chunklist) == 1 and len(chunklist[0].tokens) == 1
    if logger and not ignoreThis:
        logger('%s\n' % ' '.join(['%s' % ch for ch in chunklist]))
        
    conjIdxs = [idx for idx, ch in enumerate(chunklist) 
        if ch.chunkType in ('NONE', 'ADVP') and ch.tags[0] in ('&', 'R') 
        and ch.tokens[0] in DEGEN_CONJUNCTIONS]
    
    conjClauses = [chunklist[i:j] for i, j in zip([0]+conjIdxs, conjIdxs+[None])]    
    
    dga = []
    for cc, conjClause in enumerate(conjClauses):
        chpat = [ch.chunkType for ch in conjClause]
        ppIdxs = [idx for idx, ch in enumerate(conjClause) 
            if ch.chunkType == 'PP' and ch.tokens[0] not in ('of', 'for') and 'NP' in chpat[:idx]]
        ppClauses = [conjClause[i:j] for i, j in zip([0]+ppIdxs, ppIdxs+[None])]        
        dga.append(ppClauses)
    
        if logger and not ignoreThis:        
            logger('CC-->: %s\n' % conjClause)
            for ppc in ppClauses:
                logger('PP---->: %s\n' % ppc)           

    if logger and not ignoreThis:    
        logger('---\n')
    
    return dga
   
def clauseVPAnalysis(listOfChunks):
    """ clause is a list of chunks """
    
    clause = listOfChunks
    vpChunks = [(ch, idx) for idx, ch in enumerate(clause) if ch.chunkType == 'VP']

    n_vp = len(vpChunks)
    #no VPs
    if not vpChunks:
        return (n_vp, 0, None, clause, [], [])
        #return __STYPE_DG__  
        
    #if the VP chunk contains atleast one finite token then split on it
    vpfinite = []
    for ch, idx in vpChunks:
        for tprop in ch.tprops:
            if tprop[TLP_V_FINITE]:
                vpfinite.append((ch, idx))
                break
    n_vpfinite = len(vpfinite)

    #single VP    
    if len(vpChunks) == 1:
        vpidx = vpChunks[0][1] #vpChunks is a list of (ch, idx) tuples
        lhs = clause[:vpidx]
        rhs = clause[(vpidx+1):]
        vp  = clause[vpidx]
        return (n_vp, n_vpfinite, vpidx, lhs, vp, rhs)
    
    if not n_vpfinite:
        vpidx = vpChunks[0][1]
        lhs = clause[:vpidx]
        rhs = clause[(vpidx+1):]
        vp  = clause[vpidx]
        return (n_vp, n_vpfinite, vpidx, lhs, vp, rhs)

    elif n_vpfinite == 1:
        vpidx = vpfinite[0][1]
        lhs = clause[:vpidx]
        rhs = clause[(vpidx+1):]
        vp  = clause[vpidx]
        return (n_vp, n_vpfinite, vpidx, lhs, vp, rhs)
        
    elif n_vpfinite > 1:
                    
        lhs = [] #clause[:vpidx]
        rhs = [] #clause[(vpidx+1):]
        vp  = [] #clause[vpidx]
        if n_vpfinite == 0:
            vpp = vpChunks
        else:
            vpp = vpfinite
        return (n_vp, n_vpfinite, vpp, lhs, vp, rhs)
    else:
        print 'duh'
        
    return 0     
        

