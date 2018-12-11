#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 30 17:00:32 2017

@author: Tredence
"""
import re

def escalation(procTxt,hr):
    #current escalations regex
    lvl1_search=re.compile("(?=.*(escalation|escalate))(?=.*(supervisor|manager))(?=.*(call|connect|talk|speak))",re.I)
    lvl2_search=re.compile("((?=.*(escalation|escalate))|(?=.*(supervisor|manager)))",re.I)
    lvl3_search=re.compile("((?=.*(escalation|escalate))|(?=.*(supervisor|manager)))(?=.*(call|connect|talk|speak))",re.I)
    lvl4_search=re.compile("((?=.*(escalation|escalate))|(?=.*(supervisor|manager)))",re.I)
    
    #previously escalated calls regex
    lvl1_searchpre=re.compile("(?=.*(supervisor|manager))(?=.*(called|told|spoke|was speaking))",re.I)
    
    
    result={"current_escalation":{"result":"0","scores":{"1":0.0,"0":1.0}},
            "previously_escalated":{"result":"0","scores":{"1":0.0,"0":1.0}}}
    for sentence in procTxt["sentences"]:
       if lvl1_searchpre.search(sentence.tokString()):
           result["previously_escalated"]["result"] = "1"
           result["previously_escalated"]["scores"]["1"] = 0.67
           result["previously_escalated"]["scores"]["0"] = 0.33
       if lvl1_search.search(sentence.tokString()):
           result["current_escalation"]["result"] = "1"
           result["current_escalation"]["scores"]["1"] = 0.8
           result["current_escalation"]["scores"]["0"] = 0.2
           break
       elif lvl2_search.search(sentence.tokString()):
           result["current_escalation"]["result"] = "1"
           result["current_escalation"]["scores"]["1"] = 0.7
           result["current_escalation"]["scores"]["0"] = 0.3
       elif lvl3_search.search(sentence.tokString()) and result["result"] == "0":
           result["current_escalation"]["result"] = "1"
           result["current_escalation"]["scores"]["1"] = 0.6
           result["current_escalation"]["scores"]["0"] = 0.4
       elif lvl4_search.search(sentence.tokString()) and result["result"] == "0":
           result["current_escalation"]["result"] = "1"
           result["current_escalation"]["scores"]["1"] = 0.6
           result["current_escalation"]["scores"]["0"] = 0.4

    return result 

            

