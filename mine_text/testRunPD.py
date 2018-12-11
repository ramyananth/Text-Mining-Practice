#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 16:22:10 2017

@author: Tredence
"""

import os, sys
import pandas as pd
home = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.append(home)
os.chdir(home)
print home
print os.getcwd()


os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-8-openjdk-amd64"

import cPickle as pickle
import mine_text.mtServicesAPI as mt
import mine_text.mcsa_word_relationships as mcwa


text="My name is eric and i am not happy with the lenovo's customer serivce. network is not working. Modem is good. iphone is working. Moto xyz crashes."
#text = "Ok. The phone is good. It's like an everyday smartphone that suits the light and moderate users. But I've noticed two big problems so far. The touch ID works fine, but sometimes it just doesn't recognize the finger or some other times it doesn't unlock the phone and you need to unlock manually. The next problem is the signal on my metro pcs sim card. This phone is supposed to work good on every major carrier, but it just doesn't on t-mobile's bands. Don't know the reason yet. And this drains the battery a lot. Trust me. I barely get 4 hours of screen on time. So annoying."
text="My name is eric and i am not happy wi-fi the lenovo's customer serivce."

text = "This is the third time I ordered my items for the 2 day shipping and got them at different times ..it's more like 4 days ..why is that ??..and when I got them one package wasn't protected ( taco shells ) and they were all broken ..bringing them back for a refund but not happy considering I order from Walmart almost every week .."

text = "the product could have been bad"
text = "product is good but it is pathetic."

text = "the product was placed on february. It was wrong. It was pathetic"

text = "the customer service was placed on february and wrong and it was pathetic"


nlp=mt.mtRunServices(text,["entitySentiment","keywords"]) 


text = "the product was placed on february and was not working and it was never good"

res=mt._mtNLPipeline(text)
ver=mcwa.findNounrelatedKeyVerbs(res)
adj=mcwa.findNounIntensifyingAdj(res)


#import mine_text.problem_phrases as pp
#result=pp.inducedChunkPolarity(res,MTapi.__MT_PROD_HR__[0])

#lpp11["chunksInClauses"][0][0][3].pols
#procTxt["clausedSentences"][0][0].pols
#procTxt["chunkedSentences"][0][1].pols
#MTapi.__MT_PROD_HR__[0].getResource("polar_adjs_dict")

'''   
serviceNames=["sentiment","problemDetection"]
reqServices = mt._getServicesConfig(serviceNames)
allFeatures=set()
for service in reqServices:
    for serRes in service[mt.MTCFG_RESOURCES]:
        allFeatures = allFeatures.union(serRes[mt.MTKEY_FEATURES])   
  

 
print("i am here")
text = "no, its says the card has to be formated "
text = "unsupported sd card"
text ="lenovo's phone is great"
nlp=mt.mtRunServices(text,"sentiment") 
res=mt._mtNLPipeline(text)
'''