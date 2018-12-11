#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 16:22:10 2017

@author: Tredence
"""

import os
import sys
from config import MT_DATA_HOME
from collections import defaultdict

def availableDataSets():
    pd = defaultdict(list) #possible datasets
    for fil in os.listdir(MT_DATA_HOME):
        fileName, fileExtension = os.path.splitext(fil)
        if fileExtension in ['.txts', '.lbls']:
            pd[fileName].append(1)

    ad = [ k for k,v in pd.iteritems() if sum(v) == 2]

    return ad        

  
    
    
