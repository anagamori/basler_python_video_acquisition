# -*- coding: utf-8 -*-
"""
Created on Sat Jun 19 23:37:12 2021
@author: anaga
Hardware:
    acA720-520um
        Pin 1: Line 3 GPIO
        Pin 2: Line 1 Opto-coupled I/O
        Pin 3: Line 4 GPIO
        Pin 4: Line 2 Opto-coupled I/O 
        Pin 5: Ground for opto-coupled I/O lines
        Pin 6: Ground for GPIO liunes 
    Basler Power-I/O Cable HRS 6p/open, S
        Pin 1: Brown
        Pin 2: Pink
        Pin 3: Green
        Pin 4: Yellow 
        Pin 5: Gray
        Pin 6: White
    Arduino uno for syncrhonizing image acquisition from multiple cameras
        digital output pin = 13
        verify and upload "arduino_digital_trigger"
        Connect DO to Pin 1, Line 3 GPIO of basler cameras 
    Digitial input for video recording
        Connect digital input to trigger video recording to Pin 3, Line 4 GPIO       
Software:
    Python 
        pypylon 
        imageio
        imageio-ffmpeg (pip install imageio-ffmpeg)
        keyboard
    Arduino IDE
"""

from pypylon import pylon
import time 
from imageio import get_writer
from datetime import datetime
from collections import deque
import keyboard 
import matplotlib.pyplot as plt
import numpy as np

def current_milli_time():
    return round(time.time() * 1000)

# Run this function when event trigger is detected by the digital input channel 
def video_recording(queue,queue2,video_length,buffer_size,fps):
    i = 0
    while i <= video_length: 
        i += 1 # frame number counter 
        # Grab images from cameras
        grab = camera1.RetrieveResult(500, pylon.TimeoutHandling_ThrowException)
        grab2 = camera2.RetrieveResult(500, pylon.TimeoutHandling_ThrowException)

        # Add images to queues
        queue.append(grab.GetArray())
        queue2.append(grab2.GetArray())
        # Release grabber
        grab.Release() 
        grab2.Release() 
        
        # When the number of frames reaches the specified value, save them as video files 
        if len(queue) == video_length + buffer_size:  
            nFrame = len(queue) # check the number of frames used in video
            
            t0_r = time.time() # time how long video saving takes 
            
            # Generate the name of video files based on time
            now = datetime.now()               
            date_time = now.strftime("%m-%d-%Y-%H-%M-%S")       
            ext = '.mp4'   
            
            # Write video files 
            writer = get_writer(date_time+ext,fps = fps)
            for j in range(len(queue)):
                img_temp = queue[j] 
                writer.append_data(img_temp)              
            writer.close()         
            writer2 = get_writer(date_time+"_2"+ext,fps = fps)
            for j in range(len(queue2)):
                img_temp = queue2[j] 
                writer2.append_data(img_temp)
            print('Video acquired')                
            writer2.close()
            
            # Empty variables 
            queue = deque([])
            queue2 = deque([])
            i = 0
            
            tf_r = time.time() # time how long video saving takes 
            break
    return t0_r,tf_r,nFrame,queue,queue2

# Set up cameras
tlFactory = pylon.TlFactory.GetInstance()
devices = tlFactory.EnumerateDevices()

## Set up camera 1 (camera 1 will be whaterver computer detects first )
camera1 = pylon.InstantCamera()
camera1.Attach(tlFactory.CreateDevice(devices[0]))

camera1.Open()
# Set up a GPIO line for digital trigger for video recording 
# Note that this line has to be set up before frame trigger lines
# Set to trigger at rising edge 
camera1.LineSelector.SetValue("Line4")
camera1.LineMode.SetValue("Input")  
enable_prev = False # boolean variable for event detection 
# Set up a trigger line for image acquisition 
camera1.TriggerSelector.SetValue("FrameStart");
camera1.TriggerSource.SetValue("Line3")
camera1.TriggerActivation.SetValue('RisingEdge')
camera1.TriggerMode.SetValue('On');
# Additional parameteres 
camera1.ExposureTime.SetValue(1000)


## Set yo camera 2
camera2 = pylon.InstantCamera()
camera2.Attach(tlFactory.CreateDevice(devices[1]))
camera2.Open()
# Set up a trigger line for image acquisition 
camera2.TriggerSelector.SetValue("FrameStart");
camera2.TriggerSource.SetValue("Line3")
camera2.TriggerActivation.SetValue('RisingEdge')
camera2.TriggerMode.SetValue('On');
# Additional parameteres 
camera2.ExposureTime.SetValue(1000)

# Set up acquisition parameters
fps = 500 # frame per second
video_length = 1*fps # the length of video in frames after event trigger 
buffer_size = 1*fps # the size of buffer in frames that can be 

# counter variables
i = 0
count_video = 0

# Initialize empty queues 
queue = deque([]) 
queue2 = deque([])
time_vec = []

# Start image acquisition
print('Starting to acquire')
t0 = time.time()

camera1.StartGrabbing(pylon.GrabStrategy_OneByOne)
camera2.StartGrabbing(pylon.GrabStrategy_OneByOne)

while camera1.IsGrabbing():
    # Continuously grab acquired images 
    grab = camera1.RetrieveResult(500, pylon.TimeoutHandling_ThrowException)
    grab2 = camera2.RetrieveResult(500, pylon.TimeoutHandling_ThrowException)
    # Get status of the first GPIO line 
    enable = camera1.LineStatus.GetValue()    
    # Store current time 
    time_vec.append(current_milli_time())
    # Store acquired images in a queue
    if grab.GrabSucceeded() and grab2.GrabSucceeded():
        i += 1     
        queue.append(grab.GetArray())
        queue2.append(grab2.GetArray())
        grab.Release()  
        grab2.Release()  
    # When the number of images overflows the size of buffer, remove the oldest images 
    if len(queue) > buffer_size: 
        queue.popleft()
        queue2.popleft()
    # Event detection and trigger video recording
    if enable == True and enable_prev == False:
        count_video += 1
        (t0_r,tf_r,nFrame,queue,queue2) = video_recording(queue,queue2,video_length,buffer_size,fps)
    enable_prev = enable
    
    # When a user presses "q" on keyboard, abort recording and close cameras 
    if keyboard.is_pressed("q"):
        camera1.StopGrabbing()
        camera1.Close()  
        camera2.StopGrabbing()
        camera2.Close()
        break
    
# Check time intervals between consecutive image acquisitions  
a = np.diff(time_vec)
b = np.mean(a)
mean_fps = 1/(b)*1000 # average frame rate 

executionTime = (time.time() - t0)
print('Execution time in seconds: ' + str(executionTime))
print('Number of frames in video' + str(nFrame))
print('Number of video files acquired' + str(count_video))
