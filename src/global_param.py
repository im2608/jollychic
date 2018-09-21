#coding=utf-8
'''
Created on May 17, 2018

@author: Heng.Zhang
'''

import sys
import time
import pandas as pd
import numpy as np


runningPath = sys.path[0]
# sys.path.append("%s\\features\\" % runningPath)
inputPath = '%s/../input/in_submiting' % runningPath
outputPath = '%s/../output' % runningPath
def getCurrentTime():
    return "[%s]" % (time.strftime("%Y-%m-%d %X", time.localtime()))
