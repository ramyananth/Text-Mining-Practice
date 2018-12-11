#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 16:22:10 2017

@author: Tredence
"""

def readlines(fname):
    lines = open(fname,'r').readlines()
    lines = [line.strip() for line in lines]
    return lines

def writelines(lines, fname):   
    with open(fname, 'w') as out_file: 
        for k, line in enumerate(lines):
            out_file.write("%s\n" % line)
