# -*- coding: utf-8 -*-
"""
mt API

Created on Tue Apr 22 14:01:02 2017

@author: Tredence
"""

import json, nltk
from mtServicesAPI import mtPrintConfig, mtRunServices, mtGetServiceNames, mtNormTxt, mtSentences
a = mtServicesAPI.mtInit()
__all__ = [mtPrintConfig, mtRunServices, mtGetServiceNames, mtSentences, mtNormTxt]

