# -*- coding: utf-8 -*-
"""
Created on Tue Nov  9 15:14:12 2021

@author: anaga


"""
from pypylon import pylon
import time 
from datetime import datetime
from collections import deque
import _pickle as cPickle
import keyboard 
import os 

def current_milli_time():
    return time.time() * 1000

# Enter file info
current_directory = "C:\\Users\\anaga\\Documents\\GitHub\\python-arduino\\"

mouse_ID = "AN05" 
session_ID = "021522"
save_directory = "D:/JoystickExpts/data/"

isdir = os.path.isdir(save_directory + mouse_ID + "/" + session_ID) 
if not isdir:
    os.mkdir(save_directory + mouse_ID + "/" + session_ID)
    
os.chdir(save_directory + mouse_ID + "/" + session_ID)

# Set up cameras
tlFactory = pylon.TlFactory.GetInstance()
devices = tlFactory.EnumerateDevices()

exposureTime = 500
gain = 1
## Set up camera 1 (camera 1 will be whaterver computer detects first )
camera1 = pylon.InstantCamera()
camera1.Attach(tlFactory.CreateDevice(devices[3]))

camera1.Open()
# Set up a GPIO line for digital trigger for video recording 
# Note that this line has to be set up before frame trigger lines
# Set to trigger at rising edge 
camera1.LineSelector.SetValue("Line4")
camera1.LineMode.SetValue("Input")  
enable_prev = True # boolean variable for event detection 
# Set up a trigger line for image acquisition 
camera1.TriggerSelector.SetValue("FrameStart");
camera1.TriggerSource.SetValue("Line3")
camera1.TriggerActivation.SetValue('FallingEdge')
camera1.TriggerMode.SetValue('On');
# Additional parameteres 
camera1.ExposureTime.SetValue(exposureTime)
camera1.Gain = gain
camera1.Height = 528


## Set yo camera 2
camera2 = pylon.InstantCamera()
camera2.Attach(tlFactory.CreateDevice(devices[4]))
camera2.Open()
# Set up a trigger line for image acquisition 
camera2.TriggerSelector.SetValue("FrameStart");
camera2.TriggerSource.SetValue("Line3")
camera2.TriggerActivation.SetValue('FallingEdge')
camera2.TriggerMode.SetValue('On');
# Additional parameteres 
camera2.ExposureTime.SetValue(exposureTime)
camera2.Gain = gain
camera2.Height = 528

# Set up acquisition parameters
fps = 200 # frame per second
video_length = 0.5*fps # the length of video in frames after event trigger 
buffer_size = 1*fps # the size of buffer in frames that can be 

# counter variables
i = 0
count_video = 0

# Initialize empty queues 
queue = deque([]) 
queue2 = deque([])
queue3 = deque([])
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
       

    # When a user presses "q" on keyboard, abort recording and close cameras 
    if keyboard.is_pressed("q"):
        nFrame = len(queue) # check the number of frames used in video
                       
        # Generate the name of video files based on time
        now = datetime.now()               
        date_time = now.strftime("%H-%M-%S")       
             
        # Save image files into python files 
        filename = mouse_ID + "_" + session_ID + "_" + str(count_video) + "_" + date_time + "_cam1"
        infile = open(filename, "wb" )
        cPickle.dump(queue,infile)
        infile.close()
        
        filename = mouse_ID + "_" + session_ID + "_" + str(count_video) + "_"  + date_time + "_cam2"
        infile = open(filename, "wb" )
        cPickle.dump(queue2,infile)
        infile.close()
            
        camera1.StopGrabbing()
        camera1.Close()  
        camera2.StopGrabbing()
        camera2.Close()
        break

executionTime = (time.time() - t0)
print('Execution time in seconds: ' + str(executionTime))
#print('Number of frames in video:' + str(nFrame))
print('Number of video files acquired:' + str(count_video))

os.chdir(current_directory)

