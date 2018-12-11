#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 16:20:34 2017

@author: Tredence
"""
from collections import defaultdict
from config import PTKEY_TOKENS, PTKEY_TAGS, PTKEY_TAGCONF
import re
import unicodedata
from bs4 import BeautifulSoup as bs

pattern_1=re.compile(r"@[a-z0-9]+|#[a-z0-9]+",re.I)
pattern_2=re.compile(r"^&[a-z0-9]+",re.I)

def replace_all(text, repl):
    for i in repl:
        text = re.sub(i[0],i[1],text, flags=re.I)
    return text
   
def clean_tags(text_json):
    len_text=text_json['tokens'].__len__()
    for i,k in enumerate(text_json['tokens']):
        if(i<len_text):
            if(pattern_2.match(text_json['tokens'][i]) and pattern_1.match(text_json['tokens'][i-1]) ):
	        text_json["tokens"][i-1]=''.join([text_json["tokens"][i-1],text_json["tokens"][i]])
		text_json["tokens"].pop(i)
		text_json["tags"].pop(i)
        


repls = [
    (u"\\xc2", ' '),
    (r"☺|☻|✌|♡|♥|❤|😁|😂|😃|😄|😅|😆|😇|😊|😋|😌|😍|😎|😏|😘|😚|😜|😝",r":)"),
    (r"☹|😒|😞|😒|😠|😡|😢|😣|😩|😭",r" :( "),
    (r"(\b((att&t)|(att)|(a tt)|a[t]+[\s]+t+|a[t]*&[t]+|(at[7|n]t)|(a[\W|_]*t[\W|_]*[&]*t)|(at t(\s+)))\b)", "AT&T "),
    (r"\b^(\s)*t\s*([[:punct:]])*mobil[e]*|(\s)+t\s*mobil[e]*|\s+t[[:punct:]]mobil[e]*|\s+t(\s*)\\(\s*)mobil[e]*\b"," t-mobile"),
    (r"\b(ver[i|z|s]*o[n]+)|(\bvz[w]*\b)\b", "verizon"),
    (r"(\b((AT&T .com)|(AT&T.com)|(AT&T [\s]+.com))\b)", "AT&Tcom "),
    (r"(\b((AT&T .net)|(AT&T.net)|(AT&T [\s]+.net))\b)", "AT&Tnet "),
    (r"(?i)(\b(i(\s?)phone(\s?))\b)",r"iPhone "),
    ("(\s+)"," "),
    (r"\b(wifi)\b", "wi-fi"),
    (r"\b(u verse)\b|(u[^a-zA-Z.]verse)", "UVerse"),
    (r"mb/s|megs\b", "mbps"),
    (r"mbs speed\b", "mbps speed"),
    (r"mega b[i|y]tes\b|megs\b", 'mb'),
    (r"mega b[i|y]tes\b", 'mb'),
    (r"\baint|ai'nt\b", "ain't"),
    (r"\b[0-9]g[-|/]*[lte|tle]+", "4glte"),
    (r"\bdirecttv\b|\bdirect tv\b", "DIRECTV"),
    (r"television|t\.v\.", "tv"),
    (r"\bre-", "re")
]
 
_mods = ["are", "ca", "can", "could", "cud", "did", "do", "does", "had", "has", "have", "is", "sha", "shall", "should", "was", "were", "wo", "would", "wud"] 
_rmods = {k:k for k in _mods}
_rmods["ca"] = "can"
_rmods["cud"] = "could" 
_rmods["sha"] = "shall"
_rmods["wo"] = "would"
_rmods["wud"] = "would"
for mod in _mods:
    s = r"\b%s[']*n[']*t\b" % mod
    r = "%s not" % (_rmods[mod])
    repls.append((s, r))     


    
def ptNormalize(txts): #it comes here
    """
    pre-processing
    """
    for k, txt in enumerate(txts):
        txts[k] = bs(txts[k], "lxml").get_text(strip=True)
        for repl in repls:
            txts[k] = re.sub(repl[0],repl[1],txts[k], flags=re.I)

        if isinstance(txts[k], unicode):
            txts[k] = unicodedata.normalize('NFKD',txts[k]).encode('ascii','ignore') 
        else:
            txts[k] = unicodedata.normalize('NFKD',unicode(txts[k],'UTF-8')).encode('ascii','ignore')               
          
    return txts
    

