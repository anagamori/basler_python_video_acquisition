# -*- coding: utf-8 -*-
"""
Created on Mon May 30 22:54:25 2022

@author: anaga
"""

from pypylon import pylon
import time 
from datetime import datetime
from collections import deque
import _pickle as cPickle
import keyboard 
import os 
import multiprocessing

def current_milli_time():
    return time.time() * 1000

# Function to save images 
def save_images(camera_ID,queue,mouse_ID,session_ID,count_video):
    #start_time = time.perf_counter()
    now = datetime.now()               
    date_time = now.strftime("%H-%M-%S")       
    filename = mouse_ID + "_" + session_ID + "_" + str(count_video) + "_" + date_time + "_cam" + camera_ID
    infile = open(filename, "wb" )
    cPickle.dump(queue,infile)
    infile.close()
    
    #finish_time = time.perf_counter()
    #print(f"Program finished in {finish_time-start_time} seconds")
    print('Video #' + str(count_video))  
    print('Video acquired')    

if __name__ == "__main__":
    # Enter file info
    current_directory = "C:/Users/MNL-E/Documents/AKIRA/Python Code for Video"
    
    mouse_ID = "AN663" 
    session_ID = "012623"
    save_directory = "F:\\JoystickExpts\\data\\"
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
    gain = 5
    
    ## Set up camera 1 (camera 1 will be whaterver computer detects first )
    camera1 = pylon.InstantCamera()
    camera1.Attach(tlFactory.CreateDevice(devices[cam1_idx]))
    camera1.Open()
    # Set up a GPIO line for digital trigger for video recording 
    # Note that this line has tcao be set up before frame trigger lines
    # Set to trigger at rising edge 
    
    # Set up a trigger line for image acquisition 
    camera1.TriggerSelector.SetValue("FrameStart");
    camera1.TriggerSource.SetValue("Line3")
    camera1.TriggerActivation.SetValue('FallingEdge')
    camera1.TriggerMode.SetValue('On');
    # Additional parameteres 
    camera1.ExposureTime.SetValue(exposureTime)
    camera1.Gain = gain
    # camera1.Height = 512
    # camera1.Width = 512
    # camera1.CenterX()
    # camera1.CenterY()
    
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
    # camera2.Height = 512
    # camera2.Width = 512
    # camera2.CenterX()
    # camera2.CenterY()
    # camera2.OffsetX = 108
    # camera2.OffsetY = 16
    
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
    # camera3.Height = 512
    # camera3.Width = 512
    # camera3.CenterX()
    # camera3.CenterY()
    # camera3.OffsetX = 108
    # camera3.OffsetY = 16
    
    # Set up acquisition parameters
    fps = 200 # frame per second
    video_length = 0.2*fps # the length of video in frames after event trigger 
    buffer_size = 0.2*fps # the size of buffer in frames that can be 
    
    
    # counter variables
    i = 0
    count_video = 0
    flag_record = False
    j = 0 # # of images taken after a trigger
    k = 0 # # of triggers (i.e. # of trials )
    
    # Initialize empty queues 
    queue = deque([]) 
    queue2 = deque([])
    queue3 = deque([])
    queue_new = deque([]) 
    queue2_new = deque([])
    queue3_new = deque([])
    trigger = deque([]) 
    idx_trigger = deque([])
    time_vec = []
    
    # Start image acquisition
    print('Starting to acquire')
    t0 = time.time()
    
    camera1.StartGrabbing(pylon.GrabStrategy_OneByOne)
    camera2.StartGrabbing(pylon.GrabStrategy_OneByOne)
    camera3.StartGrabbing(pylon.GrabStrategy_OneByOne)
    
    while camera1.IsGrabbing():
        # Continuously grab acquired images 
        grab = camera1.RetrieveResult(1000, pylon.TimeoutHandling_ThrowException)
        grab2 = camera2.RetrieveResult(1000, pylon.TimeoutHandling_ThrowException)
        grab3 = camera3.RetrieveResult(1000, pylon.TimeoutHandling_ThrowException)
       
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
            trigger.append(enable)
          
        # When the number of images overflows the size of buffer, remove the oldest images 
        if len(queue) > buffer_size: 
            queue.popleft()
            queue2.popleft()
            queue3.popleft()
            trigger.popleft()
          
        # Event detection (falling edge) and trigger video recording
        # When evenet detection trigger is recieved and not in the middle of acquiring images for a preivous trial
        if enable == False and enable_prev == True and j == 0:            
            k = 1 # first trigger (i.e. first trial)
            idx_trigger = deque([])
            idx_trigger.append(0)
            flag_record = True
            # Create new buffers and fill them with images prior to the event 
            queue_new = deque([]) 
            queue2_new = deque([])
            queue3_new = deque([])
            queue_new += queue
            queue2_new += queue2
            queue3_new += queue3       
        
        # When an evenet is detected while still acquiring images for a previous trial 
        elif enable == False and enable_prev == True and j > 0 and j < int(video_length):
            # Store timing of this new trigger (# of images acquired since the last trigger)
            idx_trigger.append(j+idx_trigger[-1])
            # Reset the counter for image counts
            j = 0
            # Increment trial counter 
            k += 1
        
        # Keep appedning images when flag_record is true and the number of acquired images is less the target
        if flag_record == True and j < int(video_length):
            j += 1   
            queue_new.append(grab.GetArray())
            queue2_new.append(grab2.GetArray())
            queue3_new.append(grab3.GetArray()) 
            
        # When # of images post trigger meets the user defined #, save the images 
        elif j == int(video_length):       
            
            # Undo recording flag
            flag_record = False
            # Reset image counter 
            j = 0 
            
            # # Clear queues 
            # queue = deque([]) 
            # queue2 = deque([])
            # queue3 = deque([])
            
            # Break images in buffer into individual trials 
            start_time2 = time.perf_counter()
            for n in range(k):
                queue_proc = deque([]) 
                queue2_proc = deque([]) 
                queue3_proc = deque([]) 
                count_video += 1
                
                for m in range(int(video_length+buffer_size)):
                    queue_proc.append(queue_new[m+idx_trigger[n]])
                    queue2_proc.append(queue2_new[m+idx_trigger[n]])
                    queue3_proc.append(queue3_new[m+idx_trigger[n]])
              
                camera_ID_1 = "1"
                camera_ID_2 = "2"
                camera_ID_3 = "3"
                start_time = time.perf_counter()
                p1 = multiprocessing.Process(target=save_images(camera_ID_1,queue_proc,mouse_ID,session_ID,count_video))
                p1.start()                
                p2 = multiprocessing.Process(target=save_images(camera_ID_2,queue2_proc,mouse_ID,session_ID,count_video))
                p2.start()
                p3 = multiprocessing.Process(target=save_images(camera_ID_3,queue3_proc,mouse_ID,session_ID,count_video))
                p3.start()
                # joint all processes seem required to simultaneously run them
                # p1.join()
                # p2.join()
                # p3.join()
                finish_time = time.perf_counter()
                print(f"Program finished in {finish_time-start_time} seconds")
                #p = multiprocessing.Process(target=save_images(queue_proc,queue2_proc,queue3_proc,mouse_ID,session_ID,count_video))
                #p.start()
            finish_time2 = time.perf_counter()
            print(f"Program finished in {finish_time2-start_time2} seconds")
        grab.Release()  
        grab2.Release() 
        grab3.Release() 
        
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