# -*- coding: utf-8 -*-
"""
Created on Mon May 30 22:22:52 2022

@author: anaga
"""


import multiprocessing
import time
 
def task():
    print('Sleeping for 0.5 seconds')
    time.sleep(0.5)
    print('Finished sleeping')
 
if __name__ == "__main__":
    start_time = time.perf_counter()
 
    # Creates two processes
    p1 = multiprocessing.Process(target=task)
    p2 = multiprocessing.Process(target=task)
 
    # Starts both processes
    p1.start()
    p2.start()
 
    finish_time = time.perf_counter()
 
    print(f"Program finished in {finish_time-start_time} seconds")
    print(f'Process p is alive: {p1.is_alive()}')
    
    #p1.terminate()
    p1 = multiprocessing.Process(target=task)
    p1.start()
    print(f'Process p is alive: {p1.is_alive()}')
    