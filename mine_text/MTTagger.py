#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 16:22:10 2017

@author: Tredence
"""

'''
modifying this code to use nltk tagger as jnius is not working after
ubuntu update and CMUTweetTagger is proving time expensive to call
'''



import os
import json
import sys
# PYJNIUS INTERFACE TO CMU TAGGER
import warnings
import jnius_config
from collections import defaultdict
from nltk import word_tokenize
from nltk import pos_tag

nltk_pos_to_cmu=[('NN','N'),
('NNS','N'),
('PRP','O'),
('WP','O'),
('NNS','S'),
('NNP','^'),
('NNPS','^'),
('VB','V'),
('VBD','V'),
('VBG','V'),
('VBN','V'),
('VBP','V'),
('VBZ','V'),
('MD','V'),
('JJ','A'),
('JJR','A'),
('JJS','A'),
('RB','R'),
('RBR','R'),
('RBS','R'),
('WRB','R'),
('UH','!'),
('WDT','D'),
('DT','D'),
('WP$','D'),
('PRP$','D'),
('IN','P'),
('TO','P'),
('CC','&'),
('RP','T'),
('EX','X'),
('PDT','X'),
('CD','$'),
('FW','G'),
('POS','G'),
('SYM','G'),
('LS','G')]




if not jnius_config.vm_running:
    if not 'MINE_TEXT_HOME' in os.environ:
        os.environ['MINE_TEXT_HOME'] = '/'.join(os.path.abspath(__file__).split('/')[:-1])
    os.environ['CLASSPATH'] = os.path.join(os.environ['MINE_TEXT_HOME'], 'java/Tweebo-master/ark-tweet-nlp-0.3.2/ark-tweet-nlp-0.3.2.jar')
    jnius_config.add_options('-Xrs', '-Xmx512m')
    print os.environ['MINE_TEXT_HOME']
    print os.environ['CLASSPATH']
else:
    warnings.warn('Tagger JVM Already Running')
    

#importing CMUTweetTagger

sys.path.append("".join((os.getenv('MINE_TEXT_HOME'),'/java/Tweebo-master/ark-tweet-nlp-0.3.2')))  
  
#from CMUTweetTagger import runtagger_parse

class Tagger(object):
    def __init__(self):
        """
        """
        
        #self.tag = runtagger_parse
        self.tag = pos_tag
    def getTags(self, txt):
        """ """
        #return json.loads(self.tag(txt,run_tagger_cmd="".join(("java -XX:ParallelGCThreads=2 -Xmx500m -jar",os.getenv("CLASSPATH")))))        
        #tagged_text = self.tag([txt],run_tagger_cmd="".join(("java -XX:ParallelGCThreads=2 -Xmx500m -jar ",os.getenv("CLASSPATH")))) 
        tagged_text = self.tag(word_tokenize(txt))
        result = defaultdict()
        result["tokens"] = []
        result["tags"] = []
        for item in tagged_text:
            result["tokens"].append(item[0])
            result["tags"].append(item[1])
        
        #converting the nltk tags into cmu tags
        for ind,tag in enumerate(result["tags"]):
            try:
                index = [n[0] for n in nltk_pos_to_cmu].index(tag)
                result["tags"][ind] = nltk_pos_to_cmu[index][1]
            except: 
                result["tags"][ind] = ","
        return result    
            
        
        
        
        
