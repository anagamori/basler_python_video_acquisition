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

def save_images(queue,queue2,queue3,mouse_ID,session_ID,count_video):
    now = datetime.now()               
    date_time = now.strftime("%H-%M-%S")       
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

if __name__ == "__main__":
    # Enter file info
    current_directory = "C:/Users/MNL-E/Documents/AKIRA/Python Code for Video"
    
    mouse_ID = "AN08" 
    session_ID = "050622"
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
    
    exposureTime = 100
    gain = 15
    
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
    camera1.Height = 512
    camera1.Width = 512
    camera1.OffsetX = 108
    camera1.OffsetY = 16
    
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
    camera2.Height = 512
    camera2.Width = 512
    camera2.OffsetX = 108
    camera2.OffsetY = 16
    
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
    camera3.Height = 512
    camera3.Width = 512
    camera3.OffsetX = 108
    camera3.OffsetY = 16
    
    # Set up acquisition parameters
    fps = 200 # frame per second
    video_length = 0.5*fps # the length of video in frames after event trigger 
    buffer_size = 0.5*fps # the size of buffer in frames that can be 
    
    
    # counter variablesq
    i = 0
    count_video = 0
    
    # Initialize empty queues 
    queue = deque([]) 
    queue2 = deque([])
    queue3 = deque([])
    trigger = deque([]) 
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
            trigger.append(enable)
            grab.Release()  
            grab2.Release() 
            grab3.Release() 
           
        # When the number of images overflows the size of buffer, remove the oldest images 
        if len(queue) > buffer_size: 
            queue.popleft()
            queue2.popleft()
            queue3.popleft()
            trigger.popleft()
          
        # Event detection and trigger video recording
        if enable == False and enable_prev == True:
            flag_record = True
            j = 0 # counter for the nuber of images acquired 
            queue_new = queue
            queue2_new = queue2
            queue3_new = queue3            
        
        if flag_record == True and j < int(video_length):
            j += 1   
            queue_new.append(grab.GetArray())
            queue2_new.append(grab2.GetArray())
            queue3_new.append(grab3.GetArray()) 
        elif j == int(video_length):
            count_video += 1
            flag_record = False
            p = multiprocessing.Process(target=save_images(queue_new,queue_new,queue_new,mouse_ID,session_ID,count_video))
            p.start()
            
        grab.Release()  
        grab2.Release() 
        grab3.Release() 
        
        if 'p' in locals() and p.is_alive():
            p.terminate()
            p.close()
            
            # k = 0 # counter for triggers
            # idx_trigger = deque([]) 
            # flag = False
            # buffer_frame = len(queue)
            
            # while j <= int(video_length): 
            #     j += 1 # frame number counter 
            #     # Grab images from cameras
            #     grab = camera1.RetrieveResult(500, pylon.TimeoutHandling_ThrowException)
            #     grab2 = camera2.RetrieveResult(500, pylon.TimeoutHandling_ThrowException)
            #     grab3 = camera3.RetrieveResult(500, pylon.TimeoutHandling_ThrowException)
            
            #     enable = camera2.LineStatus.GetValue()  
                
            #     # Add images to queues
            #     queue.append(grab.GetArray())
            #     queue2.append(grab2.GetArray())
            #     queue3.append(grab3.GetArray())
            #     trigger.append(enable)
                
            #     # Release grabber
            #     grab.Release() 
            #     grab2.Release()
            #     grab3.Release()
                
            #     # if the next trial triggered before the previous ends
            #     if enable == False and enable_prev == True:
            #         flag = True
            #         idx_trigger.append(j)
            #         k += 1           
                  
            #     # When the number of frames reaches the specified value, save them as video files 
            #     if j == int(video_length):    
            #         # If another trigger didn't happen while acquiring the pre-specified number of images after the initial trigger
            #         # save the images 
            #         if flag == False and k == 0: # another tirgger never happened 
            #             nFrame = len(queue) # check the number of frames used in video
                                   
            #             # Generate the name of video files based on time
            #             now = datetime.now()               
            #             date_time = now.strftime("%H-%M-%S")       
                      
                        
            #             # Save image files into python files 
            #             filename = mouse_ID + "_" + session_ID + "_" + str(count_video) + "_" + date_time + "_cam1"
            #             infile = open(filename, "wb" )
            #             cPickle.dump(queue,infile)
            #             infile.close()
                        
            #             filename = mouse_ID + "_" + session_ID + "_" + str(count_video) + "_"  + date_time + "_cam2"
            #             infile = open(filename, "wb" )
            #             cPickle.dump(queue2,infile)
            #             infile.close()
                        
            #             filename = mouse_ID + "_" + session_ID + "_" + str(count_video) + "_"  + date_time + "_cam3"
            #             infile = open(filename, "wb" )
            #             cPickle.dump(queue3,infile)
            #             infile.close()
                    
                       
            #             print('Video acquired')                            
            #             # Empty variables 
            #             queue = deque([])
            #             queue2 = deque([])
            #             queue3 = deque([])
                    
            #             count_video += 1
            #             break
            #         elif flag == False and k > 0: # another trigger(s) have happened 
            #             nFrame = len(queue) # check the number of frames used in video
    
            #             for x in range(k+1):
            #                 queue_new = deque([]) 
            #                 queue2_new = deque([])
            #                 queue3_new = deque([])
            #                 if x == 0:
            #                     for y in range(int(video_length+buffer_frame)):
            #                         queue_new.append(queue[y])
            #                         queue2_new.append(queue2[y])
            #                         queue3_new.append(queue3[y])
                                    
            #                     idx = int(video_length+int(idx_trigger[x-1]))                      
            #                 else:
            #                     idx_start = int(buffer_frame)+int(idx_trigger[k-1])
            #                     for y in range(idx_start,idx_start+int(video_length)+1):
            #                         queue_new.append(queue[y])
            #                         queue2_new.append(queue2[y])
            #                         queue3_new.append(queue3[y])
                                    
            #                     idx = idx+int(video_length)-(int(video_length)-int(idx_trigger[x-1]))
            #                 # Generate the name of video files based on time
            #                 now = datetime.now()               
            #                 date_time = now.strftime("%H-%M-%S")       
                          
                            
            #                 # Save image files into python files 
            #                 filename = mouse_ID + "_" + session_ID + "_" + str(count_video) + "_" + date_time + "_cam1"
            #                 infile = open(filename, "wb" )
            #                 cPickle.dump(queue_new,infile)
            #                 infile.close()
                            
            #                 filename = mouse_ID + "_" + session_ID + "_" + str(count_video) + "_"  + date_time + "_cam2"
            #                 infile = open(filename, "wb" )
            #                 cPickle.dump(queue2_new,infile)
            #                 infile.close()
                            
            #                 filename = mouse_ID + "_" + session_ID + "_" + str(count_video) + "_"  + date_time + "_cam3"
            #                 infile = open(filename, "wb" )
            #                 cPickle.dump(queue3_new,infile)
            #                 infile.close()
                            
            #                 count_video += 1               
                       
            #             print('Video acquired')                            
            #             # Empty variables 
            #             queue = deque([])
            #             queue2 = deque([])
            #             queue3 = deque([])
                        
            #             break
            #         elif flag == True: # Another trigger has happened while acquiring images  
            #             j = video_length-idx_trigger[k-1]-1 # reset counter to the number of missing images to be recorded for the next video  
            #             flag = False                             
                        
                        
            #     enable_prev = enable
            # print('Video #' + str(count_video))   
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