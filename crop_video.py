# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 09:12:17 2023

@author: anaga
"""

import os
from os import listdir
from os.path import isfile, join
from imageio import get_writer
import _pickle as cPickle

ext = '.mp4'
fps = 200
fps_new = 200

start_frame = int(1) #int(2.2*fps)
end_frame = int(8.0*fps)
frame_str = '_' + str(start_frame) + '_' + str(end_frame)
idx = range(start_frame,end_frame)

filename = "C:\\Users\\anaga\\OneDrive\\Desktop\\Research\\Presentation\\U19\\All-hands\\Videos\\CFL24_08232023_saline_21_15-55-51_cam2"
infile = open(filename, "rb" )
data = cPickle.load(infile)
# cannot use quality = 10 if you want to play it on powerpoint 
writer = get_writer(filename + frame_str +ext,fps = fps_new,quality = 10)
for j in range(len(idx)):
    idx_frame = idx[j]
    img_temp = data[idx_frame] 
    writer.append_data(img_temp) 
    

infile.close()        
writer.close()