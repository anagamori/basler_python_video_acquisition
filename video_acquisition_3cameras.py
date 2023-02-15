# -*- coding: utf-8 -*-
"""
Created on Wed Mar 16 15:36:48 2022

@author: MNL-E
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

# Run this function when event trigger is detected by the digital input channel 
def video_recording(queue,queue2,queue3,video_length,buffer_size,fps,count_video,mouse_ID,session_ID):
    j = 0
    
    while j <= video_length: 
        j += 1 # frame number counter 
        # Grab images from cameras
        grab = camera1.RetrieveResult(500, pylon.TimeoutHandling_ThrowException)
        grab2 = camera2.RetrieveResult(500, pylon.TimeoutHandling_ThrowException)
        grab3 = camera3.RetrieveResult(500, pylon.TimeoutHandling_ThrowException)
    
        enable = camera2.LineStatus.GetValue()  
        
        # Add images to queues
        queue.append(grab.GetArray())
        queue2.append(grab2.GetArray())
        queue3.append(grab3.GetArray())
        
        # Release grabber
        grab.Release() 
        grab2.Release()
        grab3.Release()

          
        # When the number of frames reaches the specified value, save them as video files 
        if j == video_length:  
  
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
            
            filename = mouse_ID + "_" + session_ID + "_" + str(count_video) + "_"  + date_time + "_cam3"
            infile = open(filename, "wb" )
            cPickle.dump(queue3,infile)
            infile.close()
        
           
            print('Video acquired')                            
            # Empty variables 
            queue = deque([])
            queue2 = deque([])
            queue3 = deque([])
        

            break
        enable_prev = enable
        
    return nFrame,queue,queue2,queue3

# Enter file info
current_directory = "C:/Users/MNL-E/Documents/AKIRA/Python Code for Video"

mouse_ID = "test" 
session_ID = "090122"
save_directory = "F:/JoystickExpts/data/"
isdir = os.path.isdir(save_directory + mouse_ID + "/" + session_ID) 
if not isdir:
    os.mkdir(save_directory + mouse_ID + "/" + session_ID)
os.chdir(save_directory + mouse_ID + "/" + session_ID)
# Set up cameras
tlFactory = pylon.TlFactory.GetInstance()
devices = tlFactory.EnumerateDevices()

n = 0
for device in devices:
    temp = device.GetFriendlyName()
    if temp[-9:-1] == '40110281':
        cam1_idx = n
    elif temp[-9:-1] == '40110282':
        cam2_idx = n
    elif temp[-9:-1] == '40092103':
        cam3_idx = n
    n += 1

exposureTime = 500
gain = 0

## Set up camera 1 (camera 1 will be whaterver computer detects first )
camera1 = pylon.InstantCamera()
camera1.Attach(tlFactory.CreateDevice(devices[cam1_idx]))
camera1.Open()
# Set up a GPIO line for digital trigger for video recording 
# Note that this line has to be set up before frame trigger lines
# Set to trigger at rising edge 

# Set up a trigger line for image acquisition 
camera1.TriggerSelector.SetValue("FrameStart");
camera1.TriggerSource.SetValue("Line3")
camera1.TriggerActivation.SetValue('FallingEdge')
camera1.TriggerMode.SetValue('On');
# Additional parameteres 
camera1.ExposureTime.SetValue(exposureTime)
camera1.Gain = gain
#camera1.Height = 544

## Set yo camera 2
camera2 = pylon.InstantCamera()
camera2.Attach(tlFactory.CreateDevice(devices[cam2_idx]))
camera2.Open()
# Set up a trigger line for image acquisition 
camera2.LineSelector.SetValue("Line4")
camera2.LineMode.SetValue("Input")  
enable_prev = False # boolean variable for event detection 
camera2.TriggerSelector.SetValue("FrameStart");
camera2.TriggerSource.SetValue("Line3")
camera2.TriggerActivation.SetValue('FallingEdge')
camera2.TriggerMode.SetValue('On');
# Additional parameteres 
camera2.ExposureTime.SetValue(exposureTime)
camera2.Gain = gain
#camera1.Height = 544

## Set up camera 3 
camera3 = pylon.InstantCamera()
camera3.Attach(tlFactory.CreateDevice(devices[cam3_idx]))
camera3.Open()
# Set up a GPIO line for digital trigger for video recording 
# Note that this line has to be set up before frame trigger lines
# Set to trigger at rising edge 

# Set up a trigger line for image acquisition 
camera3.TriggerSelector.SetValue("FrameStart");
camera3.TriggerSource.SetValue("Line3")
camera3.TriggerActivation.SetValue('FallingEdge')
camera3.TriggerMode.SetValue('On');
# Additional parameteres 
camera3.ExposureTime.SetValue(exposureTime)
camera3.Gain = gain
#camera3.Height = 544
#camera1.Width = 528

# Set up acquisition parameters
fps = 200 # frame per second
video_length = 5*fps # the length of video in frames after event trigger 
buffer_size = 3*fps # the size of buffer in frames that can be 


# counter variablesq
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
camera3.StartGrabbing(pylon.GrabStrategy_OneByOne)

while camera1.IsGrabbing():
    # Continuously grab acquired images 
    grab = camera1.RetrieveResult(500, pylon.TimeoutHandling_ThrowException)
    grab2 = camera2.RetrieveResult(500, pylon.TimeoutHandling_ThrowException)
    grab3 = camera3.RetrieveResult(500, pylon.TimeoutHandling_ThrowException)
   
    # Get status of the first GPIO line 
    enable = camera2.LineStatus.GetValue()      
    # Store current time 
    time_vec.append(current_milli_time())
    # Store acquired images in a queueq
    if grab.GrabSucceeded() and grab2.GrabSucceeded() and grab3.GrabSucceeded():
        i += 1     
        queue.append(grab.GetArray())
        queue2.append(grab2.GetArray())
        queue3.append(grab3.GetArray())
       
        grab.Release()  
        grab2.Release() 
        grab3.Release() 
       
    # When the number of images overflows the size of buffer, remove the oldest images 
    if len(queue) > buffer_size: 
        queue.popleft()
        queue2.popleft()
        queue3.popleft()
      
    # Event detection and trigger video recording
    if enable == False and enable_prev == True:
        count_video += 1
        start_time = time.perf_counter()
        (nFrame,queue,queue2,queue3) = video_recording(queue,queue2,queue3,video_length,buffer_size,fps,count_video,mouse_ID,session_ID)
        print('Video #' + str(count_video))   
        finish_time = time.perf_counter()
        print(f"Program finished in {finish_time-start_time} seconds")
    enable_prev = enable
    
    # When a user presses "q" on keyboard, abort recording and close cameras 
    if keyboard.is_pressed("q"):
        camera1.StopGrabbing()
        camera1.Close()  
        camera2.StopGrabbing()
        camera2.Close()
        camera3.StopGrabbing()
        camera3.Close()
        break

executionTime = (time.time() - t0)
print('Execution time in seconds: ' + str(executionTime))
#print('Number of frames in video:' + str(nFrame))
print('Number of video files acquired:' + str(count_video))

os.chdir(current_directory)