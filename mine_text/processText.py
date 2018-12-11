# -*- coding: utf-8 -*-
"""
Created on Sat Jun 14 21:12:00 2014

@author: Tredence
"""
from config import MT_USE_PY_NORMALIZATION
if MT_USE_PY_NORMALIZATION:
    print 'using py normalization'
    from ptPreProc import ptNormalize, getCMUTag, normalizeAndTag
    from config import MT_TAGGER_HOME

import re
#import nltk as nltk
from nltk.chunk import RegexpParser
import warnings
from ngdict import parseAsNgrams
from Resources import RESKEY_POLAR_NGRAMS
from config import PTKEY_TOKENS, PTKEY_TAGS, PTKEY_SENTENCES, PTKEY_PRECHUNK, PTKEY_CLAUSES, PTKEY_CHUNKEDCLAUSES
from config import PTKEY_CHUNKEDSENTENCES, PTKEY_CHUNKTYPE_NONE
from ptdatatypes import ptSentence, ptChunk
from Resources import RESKEY_SMILEYS, RESKEY_POLAR_ADJS, RESKEY_POLAR_ADVS
from Resources import RESKEY_NEGATORS, RESKEY_POLAR_NOUNS, RESKEY_POLAR_VERBS, RESKEY_POLAR_ANYPOS
from collections import defaultdict
from appDefs import *
import chunk_cleanup

#USING_NLTK3 = nltk.__version__.split('.')[0] >= 3
##############################################################################
__SEN_PUNC_TAG__ = ","
__SEN_PUNC_TOKS__ = re.compile(r"[?|-|--|:|;|!|.+]")
__SEN_REL_POSTAGS__ = set([POSKEY_EMOT, POSKEY_DM, POSKEY_HASH]) #['E', 'U', '~', '#']
__PT_URL_TXT__ = '__URL__'
__SEN_Ques__=re.compile(r"\?+")
__SEN_dash__=re.compile(r"-+")
__SEN_ddash__=re.compile(r"--+")
__SEN_colon__=re.compile(r":+")
__SEN_semicolon__=re.compile(r";+")
__SEN_exclamation__=re.compile(r"!+")
__SEN_dot__=re.compile(r"\.+")

_COMPANY_VALID_TAGS = set(('@', '^', 'Z', 'N'))
_COMPANY_NAME = 'lenovo'
def ptSentencify(procTxt): #it comes here
    """
    POS-tag based sentence boundary detection
    """
    sentences = []
    thisSentence = ptSentence()
    nlen = procTxt[PTKEY_TOKENS].__len__()
    for k, tok in enumerate(procTxt[PTKEY_TOKENS]):
        print "SSSS",tok
        tag = procTxt[PTKEY_TAGS][k]
        if tag == POSKEY_URL:
            procTxt[PTKEY_TOKENS][k] = __PT_URL_TXT__

        if _COMPANY_NAME in tok and not tag in _COMPANY_VALID_TAGS: #not in ('^', 'Z') : 'V', 'E'
            procTxt[PTKEY_TAGS][k] = POSKEY_PRPNOUN
        
        if tok in ('dropped', 'missed', 'calls'):
            procTxt[PTKEY_TAGS][k] = 'N'
        elif tok == 'slow' and tag == 'N':
            procTxt[PTKEY_TAGS][k] = 'A'
        elif k < nlen -1 and tok == 'offer' and procTxt[PTKEY_TAGS][k+1] == 'A':
            procTxt[PTKEY_TAGS][k] = 'V'
            #print procTxt[PTKEY_TOKENS][k], procTxt[PTKEY_TAGS][k] 
            
        tag = procTxt[PTKEY_TAGS][k]
        
        thisSentence.tokens.append(tok)
        thisSentence.tags.append(tag)
        
        #if ((tag == __SEN_PUNC_TAG__) and (__SEN_PUNC_TOKS__.search(tok))) or (tag in __SEN_REL_POSTAGS__):           
        if ((tag == __SEN_PUNC_TAG__) and (any([__SEN_Ques__.search(tok),__SEN_dash__.search(tok),__SEN_ddash__.search(tok),__SEN_colon__.search(tok),__SEN_semicolon__.search(tok),__SEN_dot__.search(tok),__SEN_exclamation__.search(tok)]))) or (tag in __SEN_REL_POSTAGS__):                      
            if (thisSentence.tags.__len__() >= 2 and any(a in _COMPANY_VALID_TAGS for a in thisSentence.tags)):
                sentences.append(thisSentence)
                thisSentence = ptSentence()
            if k > nlen:
                break
    if not thisSentence.isEmpty():
        sentences.append(thisSentence)
    print "SENT",sentences
    return sentences

word2num = {'zero':0, 'one':1, 'two':2, 'three':3, 'four':4, 'five':5, 
            'six':6, 'seven':7, 'eight':8, 'nine':9, 'ten':10,
            'eleven':11, 'twelve':12, 'thirteen':13, 'fourteen':14, 'fifteen':15, 'sixteen':16, 'seventeen':17, 'eighteen':18, 'nineteen':19,
            'twenty':20, 'thirty':30, 'forty':40, 'fifty':50, 'sixty':60, 'seventy':70, 'eight':80, 'ninety':90, 'hundred':100
}

def repWord2Num2(tok):
    if tok in word2num:
        num = word2num[tok]
    else:
        try:
            num = int(tok)
        except:
            return tok
                
        
    if num == 0:
        return str(num)
    elif num == 1:
        return 'one'
    elif num <= 10:
        return '2-10'
    elif num <= 100:
        return '11-100'
    elif num <= 1000:
        return '101-1000'
    else:
        return '>1000'
        
    
##############################################################################
ngpolmap = {'negative':-1, 'positive':1, 'neutral':0}
__POL_MERGEPATTERNS__ = ['V', 'A', 'R', 'N', 'O', 'P', 'T']
def checkNgramMembership(tokens, tags, ngDictRes): #it comes here
    """
    """
    pcToks = []
    pcTags = []
    pcPols = []
    ngd = ngDictRes

    tt = [t for t in zip(tokens, tags)]
    ngsentence = parseAsNgrams(ngd, tt)
    for ngtok in ngsentence:

        if type(ngtok) == tuple:
            pcToks.append(ngtok[0])
            pcTags.append(ngtok[1])
            pcPols.append(0)
        else:
            val = [tok for tok, tag in ngtok.val]
            tag = [tag for tok, tag in ngtok.val]
            tagpattern = '+'.join(tag)
            val = '_NG_'.join(val)

            newTag = tagpattern #if tagpattern in ['V+P+N', 'V+P+O', 'V+N', 'V+O', 'V+D+N', 'V+T', 'V+O+T']:
            newTag = tag[0]
            
            if tag[0] in ('P') and tag[1] in ('N'):
                newTag = tag[1]
            elif not (tag[0] in __POL_MERGEPATTERNS__):
                if len(tag) > 1:
                    newTag = tag[1]
                else:
                    newTag = tag[0]
            elif tag[0] in ('R', 'A'): 
                if 'N' in tag:
                    newTag = 'N'
                elif 'V' in tag:
                    newTag = 'V'
                elif 'A' in tag[1:]:
                    newTag = 'A'                    

            pcToks.append(val)
            pcTags.append(newTag)
            pcPols.append(ngpolmap[ngtok.polarity])

    return (pcToks, pcTags, pcPols)

#__PRECHUNK_MERGEPATTERNS__ = ['V', 'A', 'R', 'N', 'O', 'P', 'T']
polMapDict = defaultdict(int, {'positive':1,'negative':-1})

def unigramPol(tok,  hr):
    """
    Just tokens no tags
    """
    resLst = [RESKEY_POLAR_ANYPOS, RESKEY_POLAR_NOUNS, RESKEY_POLAR_VERBS, RESKEY_POLAR_ADVS, RESKEY_POLAR_ADJS]
    for res in resLst:
        pol = polMapDict[hr.resources[res].get(tok, 0)]
        if pol:
            return pol
    return 0


_UPP_VARN = set(['A', 'R', 'V', 'N'])
def __unigramPriorPol(pcToks, pcTags, pcPols, hr): #it comes here

    pdict = {}
    pdict['V'] = hr.resources[RESKEY_POLAR_VERBS]
    pdict['A'] = hr.resources[RESKEY_POLAR_ADJS]
    pdict['R'] = hr.resources[RESKEY_POLAR_ADVS]
    pdict['N'] = hr.resources[RESKEY_POLAR_NOUNS]
    pdict['*'] = hr.resources[RESKEY_POLAR_ANYPOS]

    for k, tok in enumerate(pcToks):
        tag = pcTags[k]
        key = '*'

        if (not tag == '#') and '#' in tok:
            tok = tok.replace('#','')

        if tag in _UPP_VARN  and len(tok.split('_NG_')) < 2: #'_NG(' not in tok:
            pol = pdict[tag].get(tok, None)
            if not pol:
                pol = pdict['*'].get(tok, 0)

            pcPols[k] = polMapDict[pol]

    return pcPols

def priorPolAndPreChunker(sentence, hr): #it comes here
    """
    Two functions:
    1. Get pre-chunks based on ngram dictionaries
    2. Get prior polarities of tokens.
        e.g., strike a deal, save money, pay you that much, cost that much, too much
    """
    pcToks, pcTags, pcPols = checkNgramMembership(sentence.tokens, sentence.tags, hr.resources[RESKEY_POLAR_NGRAMS])
    pcPols = __unigramPriorPol(pcToks, pcTags, pcPols, hr)
    pts = ptSentence(pcToks, pcTags, pcPols)

#    for tok in pts.tokens:
#        if 'NG' in tok:
#            print tok
    return pts

def priorPolaritiesAndPreChunker(sentences, hr):
    """
    Wrapper for pre-Chunking
    """

    preChunkedSentences = [priorPolAndPreChunker(sentence, hr) for sentence in sentences]
    return preChunkedSentences

#<D|\$|\&|\#>*
#    <D|\$|\#>* <R|A>* <A\&>*
        #{<D>* <N|O|S|\^|Z>}+ <\&> <D>* <N|O|S|\^|Z>}+} O||A|A
        #{<D|N|O|S|\^|Z|A|\$|\#>+ <P> <N|S|\^|Z>+}
# {<V|P|R|L|Y>* <V|L|Y>+ <R|A|T|P>*}
# {<V|P|R|L|Y>* <V|L|Y>+ <T|P>*}
##############################################################################
__CMUTAGCHUNKER_GRAMMAR__ = r"""
    INTJ:
    {<!>+ <\,|G>* <!|~>*}
    NP:
    {<D>*<@>+}
    {<O> <N|S|\^|Z>*}
    {<DPO>}
    {<D>*<X|N|O|S|\^|Z|A|\$|\#>* <N|S|\^|Z|$>+}
    {<D>+<N|O|S|\^|Z|A|\$|\#>+ <P> <N|S|\^|Z|$>+}
    {<D|X>+}
    VP:
    {<V|P|R|L|Y>* <V|L|Y>+ <T>*}
    PP:
    {<P>+}
    ADJP:
    {<R|A|D>* <A\,>* <A\&>* <A>+}
    ADVP:
    {<R>+}
    """

__CMUTAGCHUNKER_CHUNKTYPES__ = set(['NP', 'VP', 'PP', 'ADJP', 'ADVP', 'INTJ'])
__CMUTAGCHUNKER_REGEX__ = RegexpParser(__CMUTAGCHUNKER_GRAMMAR__,loop=1)

def __getChunksCMU__(sentence):
    """
    Chunk a sentence.
    A way to isolate the chunker.
    Chunker for CMU POS Tags
    """
    tokTags = []
    newChunkLst =[]
    for k, (tok, tag, pols) in enumerate(zip(sentence.tokens, sentence.tags, sentence.pols)):
        ptc = ptChunk(tok, tag, [pols], PTKEY_CHUNKTYPE_NONE)
        tokTags.append(([ptc, k], tag))
        newChunkLst.append(ptc)

    parsedSentence = __CMUTAGCHUNKER_REGEX__.parse(tokTags)

    for k, subtree in enumerate(parsedSentence.subtrees()):
        if k == 0:
            continue
        ttLst, tags = zip(*subtree.leaves())

        chunks, idx  = zip(*ttLst)
        headChunk = chunks[0]
        for chunk in chunks[1:]:
            headChunk.merge(chunk)

        chunkType = PTKEY_CHUNKTYPE_NONE
        if subtree.label() in __CMUTAGCHUNKER_CHUNKTYPES__: #['NP', 'VP', 'PP']:
                chunkType = subtree.label()

        headChunk.chunkType = chunkType
        #replace all tokens in chunk with the headChunk
        for i in idx:
            newChunkLst[i] = headChunk

    #remove the duplicate chunks
    lastChunk = []
    chunkedSentence = []
    for chunk in newChunkLst:
        if (chunk.chunkType in __CMUTAGCHUNKER_CHUNKTYPES__) and (chunk == lastChunk): continue
        if chunk.chunkType == 'NP':
            schunks = chunk_cleanup.npCleanup(chunk)    
            chunkedSentence.extend(schunks)
        else:
            chunkedSentence.append(chunk)
        lastChunk = chunk
    return chunkedSentence

def chunkifyCMUTags(clausedSentences): #it comes here
    """
    wrapper around chunker
    """
    #assert(all([type(clause) == ptSentence for sentence in sentences]))

    chunkedSentences = []
    for sentence in clausedSentences:
        chunkedSentences.append([__getChunksCMU__(clause) for clause in sentence])
    return chunkedSentences

##############################################################################
## TEXT PROCESSING PIPELINE
##############################################################################
from clausifier import clausify

#_PT_DEFAULT ={PTKEY_TOKENS:[], PTKEY_TAGS}
def sentencifyAndChunkOld(procTxtLst, hr):
    """
    Wrapper.
    """
    if MT_USE_PY_NORMALIZATION:
        procTxtLst = normalizeAndTag(procTxtLst, MT_TAGGER_HOME)
    
    for idx, procTxt in enumerate(procTxtLst):
        if not procTxt:
            procTxtLst[idx] = [] 
            continue

        for k, tok in enumerate(procTxt[PTKEY_TOKENS]):
            procTxtLst[idx][PTKEY_TOKENS][k] = tok.lower()

        sentences = ptSentencify(procTxt)

        #preChunkedS = priorPolaritiesAndPreChunker(sentences, hr)
        preChunkedS = [priorPolAndPreChunker(sentence, hr) for sentence in sentences]
        clausedSentences = [clausify(sentence) for sentence in preChunkedS]
        chunkedClausedSentence = chunkifyCMUTags(clausedSentences)

        #chunked sentences
        ccs = [[chunk for clause in sentence for chunk in clause] for sentence in chunkedClausedSentence]

        procTxtLst[idx][PTKEY_SENTENCES] = sentences
        procTxtLst[idx][PTKEY_PRECHUNK] = preChunkedS
        procTxtLst[idx][PTKEY_CLAUSES] = clausedSentences
        procTxtLst[idx][PTKEY_CHUNKEDSENTENCES] = ccs
        procTxtLst[idx][PTKEY_CHUNKEDCLAUSES] = chunkedClausedSentence

    return procTxtLst

def sentencifyAndChunk(procTxtLst, hr):
    #it comes here
    """
    Wrapper.
    
    """
    print "HR",hr.resources['polar_ngrams']
    if MT_USE_PY_NORMALIZATION:
        procTxtLst = normalizeAndTag(procTxtLst, MT_TAGGER_HOME)
    
    rprocTxtLst = []
    rprocTxtLst_append = rprocTxtLst.append
    for idx, procTxt in enumerate(procTxtLst):
        if not procTxt:
            rprocTxtLst_append([]) 
            continue

        for k, (tok, tag) in enumerate(zip(procTxt[PTKEY_TOKENS], procTxt[PTKEY_TAGS])):
            procTxtLst[idx][PTKEY_TOKENS][k] = tok.lower()
            if tag == '$':
                nn = repWord2Num2(tok)
                #print 'gets here', tok, nn
                procTxtLst[idx][PTKEY_TOKENS][k] = nn
        
        sentences = ptSentencify(procTxt)

        #preChunkedS = priorPolaritiesAndPreChunker(sentences, hr)
        preChunkedS = [priorPolAndPreChunker(sentence, hr) for sentence in sentences]
        clausedSentences = [clausify(sentence) for sentence in preChunkedS]
        chunkedClausedSentence = chunkifyCMUTags(clausedSentences)

        #chunked sentences
        ccs = [[chunk for clause in sentence for chunk in clause] for sentence in chunkedClausedSentence]

        rdict = {}
        for k,v in procTxt.iteritems():
            rdict[k] = procTxt[k]
        rdict[PTKEY_SENTENCES] = sentences
        rdict[PTKEY_PRECHUNK] = preChunkedS
        rdict[PTKEY_CLAUSES] = clausedSentences
        rdict[PTKEY_CHUNKEDSENTENCES] = ccs
        rdict[PTKEY_CHUNKEDCLAUSES] = chunkedClausedSentence
        rprocTxtLst_append(rdict) 

    return rprocTxtLst
    
from token_properties import tokenLexicalProps
from chunk_pols import getChunkPolarity
def updateTokenAndChunkProperties(proctxt, hr):
    """ update token lexical and chunk polarity"""
    #print 'UPP', proctxt
    for s, sentence in enumerate(proctxt[PTKEY_CHUNKEDCLAUSES]):
        for c, clause in enumerate(sentence):
            for h, chunk in enumerate(clause):
                tokenLexicalProps(chunk, hr)
                getChunkPolarity(chunk, hr)
    return proctxt


from Resources import RESKEY_HAPPENINGVERBS, RESKEY_SOFTVERBS, RESKEY_OPENCLAUSALCOMPLIMENT
from Resources import RESKEY_PROBNOUNS, RESKEY_NO_PARTICLE, RESKEY_NOTHAPPENINGVERBS
def updateTokenAndChunkPropertiesPD(proctxt, hr):
    """ update token lexical and chunk polarity"""
    #dnngd = hr.resources[RESKEY_POLAR_NGRAMS]
    nhap_verbs = set(hr.resources[RESKEY_HAPPENINGVERBS])
    soft_verbs = set(hr.resources[RESKEY_SOFTVERBS])
    openClauseComp = set(hr.resources[RESKEY_OPENCLAUSALCOMPLIMENT])
    probNouns = set(hr.resources[RESKEY_PROBNOUNS])
    noParticle = set(hr.resources[RESKEY_NO_PARTICLE])
    hap_verbs = set(hr.resources[RESKEY_NOTHAPPENINGVERBS]) #work receive
    #negation = hr.resources[RESKEY_NEGATORS].getDicts(1, KEY_NEGATION)
    
    for s, sentence in enumerate(proctxt[PTKEY_CHUNKEDCLAUSES]):
        for c, clause in enumerate(sentence):
            for h, chunk in enumerate(clause):
                tokenLexicalProps(chunk, hr)
                for k, tok in enumerate(chunk.tokens):
                    if tok in nhap_verbs: 
                        chunk.pols[k] = -1
                    elif tok in soft_verbs:
                        chunk.pols[k] = -1
                    elif tok in hap_verbs:
                        chunk.pols[k] = 1
                    elif tok in openClauseComp:
                        chunk.pols[k] = -1
                    elif tok in probNouns:
                        chunk.pols[k] = -1
                    elif tok in noParticle:
                        chunk.pols[k] = -1
                getChunkPolarity(chunk, hr)
    return proctxt
    
def makeSProcTxts(procTxtLst):
    senProcTxts = []
    for idx, procTxt in enumerate(procTxtLst):
        senProcTxt = []
        for s, sentence in enumerate(procTxt[PTKEY_SENTENCES]):
            sproctxt = {}
            sproctxt[PTKEY_TAGS] = sentence.tags
            sproctxt[PTKEY_TOKENS] = sentence.tokens
            sproctxt[PTKEY_SENTENCES] = [sentence]
            sproctxt[PTKEY_CHUNKEDSENTENCES] = [procTxt[PTKEY_CHUNKEDSENTENCES][s]]
            sproctxt[PTKEY_CLAUSES] = [procTxt[PTKEY_CLAUSES][s]]
            sproctxt[PTKEY_CHUNKEDCLAUSES] = [procTxt[PTKEY_CHUNKEDCLAUSES][s]]
            sproctxt[PTKEY_PRECHUNK] = [procTxt[PTKEY_PRECHUNK][s]]
            senProcTxt.append(sproctxt)
        senProcTxts.append(senProcTxt)
    return senProcTxts

def sentenceSplitProcTxts(procTxt):
    senProcTxt = []
    if not procTxt:
        return []
    for s, sentence in enumerate(procTxt[PTKEY_SENTENCES]):
        sproctxt = {}
        sproctxt[PTKEY_TAGS] = sentence.tags
        sproctxt[PTKEY_TOKENS] = sentence.tokens
        sproctxt[PTKEY_SENTENCES] = [sentence]
        sproctxt[PTKEY_CHUNKEDSENTENCES] = [procTxt[PTKEY_CHUNKEDSENTENCES][s]]
        sproctxt[PTKEY_CLAUSES] = [procTxt[PTKEY_CLAUSES][s]]
        sproctxt[PTKEY_CHUNKEDCLAUSES] = [procTxt[PTKEY_CHUNKEDCLAUSES][s]]
        sproctxt[PTKEY_PRECHUNK] = [procTxt[PTKEY_PRECHUNK][s]]
        senProcTxt.append(sproctxt)
    return senProcTxt

