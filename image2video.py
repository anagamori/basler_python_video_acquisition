# -*- coding: utf-8 -*-
"""
Created on Wed Jul 28 13:09:52 2021

@author: anaga
"""

import os
from os import listdir
from os.path import isfile, join
from imageio import get_writer
import _pickle as cPickle

ext = '.avi'
fps = 200

# Enter session information
mouse_ID = "AN663" 
session_ID = "012623"
save_directory = "F:\\JoystickExpts\\data\\"
os.chdir(save_directory + mouse_ID + "\\" + session_ID)

onlyfiles = [f for f in listdir(save_directory + mouse_ID + "\\" + session_ID) if isfile(join(save_directory + mouse_ID + "\\" + session_ID,f))]

for i in range(len(onlyfiles)):
    print('Processing ' + str(i) +'/' + str(len(onlyfiles)))
    filename = onlyfiles[i]
    infile = open(filename, "rb" )
    data = cPickle.load(infile)
    writer = get_writer(filename+ext,fps = fps,quality=10)
    for j in range(len(data)):
        img_temp = data[j] 
        writer.append_data(img_temp)      
    
    infile.close()        
    writer.close()