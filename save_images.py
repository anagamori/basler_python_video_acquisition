# -*- coding: utf-8 -*-
"""
Created on Wed Apr  6 14:20:02 2022

@author: MNL-E
"""

import os
from os import listdir
from os.path import isfile, join
import imageio
import _pickle as cPickle

ext = '.avi'
fps = 200

# Enter session information
mouse_ID = "F_081920_CT" 
session_ID = "092921"
save_directory = "D:\\JoystickExpts\\data\\"
os.chdir(save_directory + mouse_ID + "\\" + session_ID)

filename = '09-29-2021-09-52-07'
infile = open(filename, "rb" )
data = cPickle.load(infile)
for j in range(len(data)):
    img_temp = data[j] 
    imageio.imwrite(filename + '_' + str(j) + '.tif',img_temp)

infile.close()        
