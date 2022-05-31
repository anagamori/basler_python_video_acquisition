# -*- coding: utf-8 -*-
"""
Created on Wed Mar  9 09:57:54 2022

@author: MNL-E
"""

import cv2
import numpy 

img = numpy.zeros([200,200,3])

img[:,:,0] = numpy.ones([200,200])*64/255.0
img[:,:,1] = numpy.ones([200,200])*128/255.0
img[:,:,2] = numpy.ones([200,200])*192/255.0

cv2.imshow('frame', img)
cv2.waitKey(1)