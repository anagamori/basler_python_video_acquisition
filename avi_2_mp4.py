# -*- coding: utf-8 -*-
"""
Created on Tue Sep 19 16:22:44 2023

@author: anaga
"""

import os

def convert_avi_to_mp4(avi_file_path, output_name):
    os.popen("ffmpeg -i '{input}' -ac 2 -b:v 2000k -c:a aac -c:v libx264 -b:a 160k -vprofile high -bf 0 -strict experimental -f mp4 '{output}.mp4'".format(input = avi_file_path, output = output_name))
    return True

convert_avi_to_mp4('C:/Users/anaga/OneDrive/Desktop/Research/Presentation/Project update/Figures/061923/trial_1.avi','trial_1')
