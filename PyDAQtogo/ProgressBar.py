
# -*- coding: utf-8 -*-
"""
Created on Tue Sep  7 17:24:38 2021

@author: Zhang101
"""

import time, sys
#https://en.wikipedia.org/wiki/ANSI_escape_code#8-bit
RED   = "\033[1;31m"  
BC ='\033[1;19;36;47m'
BLUE  = "\033[1;34m"
CYAN  = "\033[1;36m"
GREEN = "\033[0;32m"
RESET = "\033[0;0m"
BOLD    = "\033[1m"
REVERSE = "\033[;7m"
UNDERLINE = '\033[4m'
END = '\033[0m'
BLINKING= '\033[5m'
# update_progress() : Displays or updates a console progress bar
## Accepts a float between 0 and 1. Any int will be converted to a float.
## A value under 0 represents a 'halt'.
## A value at 1 or bigger represents 100%
def update_progress(progress, Barname = "Progress", runtime=None):
    barLength = 50 # Modify this to change the length of the progress bar
    status = ""
    
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    
    if progress >= 1:
        progress = 1
        timeleft = "[Time Togo:{0:1d}:{1:02d}:{2:.1f}]".format( 0, 0, 0)
        # status = "Done!\n"    
        
    block = int(round(barLength*progress))
    title = "\r" + Barname + ':'
    timer = "[Elapsed Time:{0:1d}:{1:02d}:{2:.1f}]".format( int(progress*runtime/3600), 
             int(((progress*runtime)%3600)/60), ((progress*runtime)%3600)%60%60)
    text = "[{0}] {1:.1f}% {2}".format( '█'*block + "-"*(barLength-block), progress*100, status)
    
      
    timeleft = "[Time Togo:{0:1d}:{1:02d}:{2:.1f}]".format( int((1-progress)*runtime/3600), 
             int((((1-progress)*runtime)%3600)/60), (((1-progress)*runtime)%3600)%60%60)
    if progress >= 1:
        progress = 1
        timeleft = "[Time Togo:{0:1d}:{1:02d}:{2:.1f}]".format( 0, 0, 0)
          
    # sys.stdout.flush()
    sys.stdout.write(BC+title+END)
    sys.stdout.write(UNDERLINE+timer+END)
    # sys.stdout.flush()
    sys.stdout.write(BOLD+text+END)
    sys.stdout.write(UNDERLINE+timeleft+END)
    sys.stdout.flush()
    


# update_progress test script

print( "progress : 0->1")
def ShowBar(Barname, runtime):
    runtime = runtime
    start_time = time.time()
    while (time.time()-start_time)< runtime:
        time.sleep(0.5)
        # print("\r1")
        update_progress((time.time()-start_time)/runtime,Barname, runtime)
    print("\nDone!  Running %f s \n" %(time.time()-start_time))
# update_progress test script
if __name__  == '__main__':
    
    ShowBar(Barname = "MoveProgress", runtime = 17)
    ShowBar(Barname = "ScanProgress", runtime = 12)    


#%%

# import tqdm
# from time import sleep

# for i in tqdm.tqdm(range(4), desc = "first loop"):
#     for j in tqdm.tqdm(range(5), desc = "second loop"):
#         for k in tqdm.tqdm(range(4), desc = "Third loop"):
#             ShowBar(Barname = "ScanProgress", runtime = 5) 
