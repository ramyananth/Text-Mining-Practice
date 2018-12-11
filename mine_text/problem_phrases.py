#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 16:22:10 2017

@author: Tredence
"""

from Resources import RESKEY_DOMAIN_NOUNS
from clause_pol import clausePolarity
from phrase_analysis2 import extract_words
from clause_properties import degenerateClauseAnalysis, clauseVPAnalysis 
from clause_props import questionsInProcTxt
from collections import defaultdict     
from processText import updateTokenAndChunkPropertiesPD   
from config import *   
from collections import OrderedDict
def hasDomainNoun(chunkList, domainNouns):
    """
    Identify the domain nouns in a chunklist such as a clause or sentence.
    returns the indices of the chunks in chunklist containing the domaining nouns
    """
    #domainNouns = hr.resources[RESKEY_DOMAIN_NOUNS]
    hasDN = [] #[0]*len(chunkList)
    hasDN_append = hasDN.append
    for h, chunk in enumerate(chunkList):
        for t, tok in enumerate(chunk.tokens):
            if tok in domainNouns:
                hasDN_append(h)
    return hasDN

def hasNoun(chunkList):
    """
    Identify the domain nouns in a chunklist such as a clause or sentence.
    returns the indices of the chunks in chunklist containing the domaining nouns
    """
    #domainNouns = hr.resources[RESKEY_DOMAIN_NOUNS]
    hasN = [] #[0]*len(chunkList)
    hasN_append = hasN.append
    for h, chunk in enumerate(chunkList):
        for t, tag in enumerate(chunk.tags):
            if tag in ['N', '@', '#', 'Z', '^']:
                hasN_append(h)
    return hasN

def ppd_degenerateClause(clause, clpols, vpidx, hr): #(chunkList, hr):
    """ 
    """
    domainNouns = hr.resources[RESKEY_DOMAIN_NOUNS]
    ndn = defaultdict(list)
    dnChunksIdx = hasDomainNoun(clause, domainNouns)
    nChunksIdx = hasNoun(clause)
    
    nChunksIdx = list(set((nChunksIdx + dnChunksIdx)))
    
    if not nChunksIdx:
        return ndn
    
    allNeutral = True
    for pol in clpols:
        if pol[0]:
            allNeutral = False
            break
    
    noNegation = True
    for ng in clpols:
        if ng[1]:
            noNegation = False
            break   
    
    if allNeutral and noNegation:
        return ndn

    dn = [ k in nChunksIdx for k, ch in enumerate(clause)]
    tndn = []
    for h, chunk in enumerate(clause):
        pols = clpols[h]
        if pols[0] < 0: # and not negtd[h]:
            tndn.append((chunk, clpols[h], dn[h]))#(h)
        elif pols[0] > 0:  #and negtd[h]:
            tndn.append((chunk, clpols[h], dn[h]))#(h)
        elif pols[1]:
            tndn.append((chunk, clpols[h], dn[h]))#(h)
        elif dn[h]:
            tndn.append((chunk, clpols[h], dn[h]))#(h)
    ndn['LHS'] = tndn                 
    return ndn
    
from collections import Counter


_PPD_AUX = set(['need', 'would', 'would_NG_like', 'want', 'hope', 'hoping', 'needed', 'wanted', 'tryna', 'trying', 'tryin', 'showed_NG_up'])
_PPD_AUX_PART = set(['to'])
_PPD_ACTVRB = set(['reset', 'log', 'pay', 'enter', 'set', 'delete', 'alter', 'change', 'cancel', 'request', 'register', 'apply', 'get', 'access'])

def ppd_SVClause(clause, clpols, vpidx, hr):
    """ 
    clpols = (pols[k], negn[k], negtd[k])
    """
    domainNouns = hr.resources[RESKEY_DOMAIN_NOUNS]
    ndn = defaultdict(list)
    dnChunksIdx = hasDomainNoun(clause, domainNouns)
    nChunksIdx = hasNoun(clause)
    
    nChunksIdx = list(set((nChunksIdx + dnChunksIdx)))
    
    if not nChunksIdx:
        return ndn
    
    allNeutral = True
    for pol in clpols:
        if pol[0]:
            allNeutral = False
            break
    
    noNegation = True
    for ng in clpols:
        if ng[1]:
            noNegation = False
            break   

    PPD_ATTEMPT =False
    for h, chunk in enumerate(clause):
        if chunk.chunkType == 'VP':
            hasPPDAUX = None
            for t, tok in enumerate(chunk.tokens):
                if tok in _PPD_AUX:
                    hasPPDAUX = t
                    break
               
            if hasPPDAUX != None: 
                    PPD_ATTEMPT = True
                        
    if (not PPD_ATTEMPT) and (allNeutral and noNegation):
        return ndn
    
    clLabels = ['LHS', 'VP', 'RHS']
    clauseBranches = [clause[:vpidx], [clause[vpidx]], clause[vpidx+1:]]
    clauseBranchPols = [clpols[:vpidx], [clpols[vpidx]], clpols[vpidx+1:]]
    isdn = [ k in nChunksIdx for k, ch in enumerate(clause)]
    isdn = [isdn[:vpidx], [isdn[vpidx]], isdn[vpidx+1:]]
    
    for c, clauseBranch in enumerate(clauseBranches):
        pols = clauseBranchPols[c]
        dn = isdn[c]
        tndn = []
        for h, chunk in enumerate(clauseBranch):
            if pols[h][0] < 0: # and not negtd[h]:
                tndn.append((chunk, pols[h], dn[h]))
            elif pols[h][0] > 0:  #and negtd[h]:
                if c == 0:
                    pols[h][0] = 0
                tndn.append((chunk, pols[h], dn[h]))
            elif pols[h][1]:
                tndn.append((chunk, pols[h], dn[h]))
            elif dn[h]:
                tndn.append((chunk, pols[h], dn[h]))
            elif chunk.chunkType == 'VP':
                hasPPDAUX = None
                for t, tok in enumerate(chunk.tokens):
                    if tok in _PPD_AUX:
                        ntoks = len(chunk.tokens)
                        if t < ntoks-1:
                           hasPPDAUX = t
                           break
#                hasPPDACTVRB = None
#                for t, tok in enumerate(chunk.tokens):
#                    if tok in _PPD_ACTVRB:
#                        hasPPDACTVRB = t
#                        break                        
                if hasPPDAUX != None: # and hasPPDACTVRB != None:
#                    print clause
#                    if hasPPDACTVRB > hasPPDAUX:
                    tndn.append((chunk, pols[h], dn[h]))
#                        print hasPPDAUX #, hasPPDACTVRB
#                        print chunk
#                        print tndn
                
        ndn[clLabels[c]] = tndn  
       
    return ndn

def ppd_MVClause(clause, clpols, vpfIdxs, hr):
#    print vpIdx
    
    vpidxs = [vp[1] for vp in vpfIdxs]
    triples = [[vpf, clpols[k], int(k in vpidxs)] for k, vpf in enumerate(clause)]
    
    splittriples = [triples[i:j] for i, j in zip([0]+ [f+1 for f in vpidxs[:-1]], vpidxs[1:]+[None])]
    
    svClauses = [[t[0] for t in tri] for tri in splittriples]
    svPols = [[t[1] for t in tri] for tri in splittriples]
    isvp = [[t[2] for t in tri] for tri in splittriples]

    clause_problem = []
    for k, svc in enumerate(svClauses):
        svp = svPols[k]
        vpidx = isvp[k].index(1)
        frac_problem = ppd_SVClause(svc, svp, vpidx, hr)
        clause_problem.append(frac_problem)
    
    return clause_problem
    
import itertools
PD_LOC = ['LHS', 'VP', 'RHS']
PD_CTYP = ['NP','ADJP','ADVP','VP', 'INTJ', 'NONE', 'PP']
PD_POLS = [-1, 0, 1]
PD_NEGN = [0, 1]
PD_NEGD = [0, 1]
PD_DN = [0,1]
_ATT_VALID_TAGS = set(('@', '^', 'Z', 'N'))

def problemPhraseAnalysis(procTxt, hr):
    """ """
    
    procTxt = updateTokenAndChunkPropertiesPD(procTxt, hr)    
    problems = []
    for s, sentence in enumerate(procTxt[PTKEY_CHUNKEDCLAUSES]):
        sentence_problem = []               
        for c, clause in enumerate(sentence):
            clause_problem = defaultdict(list) 
            n_vp, n_vpfinite, vpidx, lhs, vp, rhs = clauseVPAnalysis(clause)
            chPat, pols, negn, negtd = clausePolarity(clause, hr)
            pols = [cmp(pol,0) for pol in pols]
            clpol = [[p, int(n), int(t)] for p,n,t in zip(pols, negn, negtd)]
            if n_vp == 0:
                clause_problem = ppd_degenerateClause(clause, clpol, vpidx, hr)
                clause_problems = [clause_problem]
            elif n_vpfinite < 2: 
                clause_problem = ppd_SVClause(clause, clpol, vpidx, hr)
                clause_problems = [clause_problem]
            else:
                clause_problems = ppd_MVClause(clause, clpol, vpidx, hr)
            sentence_problem.append(clause_problems)
        problems.append(sentence_problem)
        
    return problems
           
           
def probleMTontextDetector(procTxt, hr):
    problem_context_dm=[]
    problem_context=[]
    problems=problemPhraseAnalysis(procTxt,hr)
    for problem in problems:
        for current_problems in problem:
            for current_problem in current_problems:
                for key in current_problem:
                    for phrase in current_problem[key]:
                        for ind,token in enumerate(phrase[0].tokens):
                            if (phrase[1][0] == -1 and (phrase[1][2] - phrase[1][1]) <= 0) or ((phrase[1][2] - phrase[1][1]) > 0) or (phrase[1][0] == 0 and phrase[1][1] == 1):
                                if token in hr.resources["domain_nouns"]:
                                    problem_context_dm.append(" ".join(phrase[0].tokens))
                                    break
                                elif phrase[0].tags[ind] in ["N","Z"]:
                                    problem_context.append(" ".join(phrase[0].tokens))
                                    break
    return(list(set(problem_context_dm)),list(set(problem_context)))


def inducedChunkPolarity(procTxt, hr):
    indSentiment=[]
    allPhrase=[]
    problems=problemPhraseAnalysis(procTxt,hr)
    for problem in problems:
        for current_problems in problem:
            for current_problem in current_problems:
                for key in current_problem:
                    for phrase in current_problem[key]:
                        od=OrderedDict()
                        entity=""
                        for ind,toks in enumerate(phrase[0].tokens):
                            if phrase[0].tags[ind] in ['N', '@', '#', 'Z', '^']:
                                if ind > 0:
                                    entity=" ".join((entity,"/".join((toks,phrase[0].tags[ind]))))
                                else:
                                    entity="/".join((toks,phrase[0].tags[ind]))
                        od["entity"]=entity
                        od["phrase"]=str([phrase[0]])[4:-2]
                        if entity and od["phrase"] not in allPhrase:
                            allPhrase.append(phrase[0])
                            if (phrase[1][0] == -1 and (phrase[1][2] - phrase[1][1]) <= 0) or ((phrase[1][2] - phrase[1][1]) > 0) or (phrase[1][0] == 0 and phrase[1][1] == 1):
                                od["sentiment"]="Negative"
                            else: 
                                od["sentiment"]="Positive"
                            indSentiment.append(od)
    return(indSentiment)
                                
            
                         
def problemPhraseBases(procTxt, hr, featureVals = {}, FKEY = 'problemPhraseBases'):
#    keys = ['_'.join(map(str,key)) for key in list(itertools.product(*[
#        PD_LOC, PD_CTYP, PD_POLS, PD_NEGN, PD_NEGD, PD_DN]))]
#    cpdict = {key:0 for key in keys}    
    
    cpdict = {'HAS_PROB_CLAUSE':False}
    problems = problemPhraseAnalysis(procTxt, hr)
    for s, sentence_problems in enumerate(problems):               
        for c, clause_problems in enumerate(sentence_problems):
            for clause_problem in clause_problems:
                if clause_problem:
                    plist = []
                    for branch, phrase in clause_problem.iteritems():
                        plist.extend(phrase)
                    pols = [p[1] for p in plist]
                    postPols = [p[0] for p in pols]
                    
                    for k, pol in enumerate(pols):
                        if pol[1] == 0 and pol[2] == 1:
                            postPols[k] = -1*postPols[k]
                    
                    if sum(postPols) < 1:
                        cpdict['HAS_PROB_CLAUSE'] = True
    
    featureVals[FKEY] = cpdict 
    
    return featureVals           

def probPhrasePretty(procTxt, hr):
    problems = problemPhraseAnalysis(procTxt, hr)
    txtProblems = []
    for sentence_problems in problems:
        for clause_problems in sentence_problems:
            for clause_problem in clause_problems:
                lhs = [t[0] for t in clause_problem['LHS']]
                vp = [t[0] for t in clause_problem['VP']]
                rhs = [t[0] for t in clause_problem['RHS']]
                lhs = [' '.join([' '.join(tok.split('_NG_')) for tok in ch.tokens]) for ch in lhs] 
                vp = [' '.join([' '.join(tok.split('_NG_')) for tok in ch.tokens]) for ch in vp] 
                rhs = [' '.join([' '.join(tok.split('_NG_')) for tok in ch.tokens]) for ch in rhs] 
                
                problem = lhs+vp+rhs
                if problem:
                    txtProblems.append(' '.join(problem))
    return list(set(txtProblems))

