'''
Created on Feb 1, 2018

@author: Jeff Victor
'''

import threading

numSteps=0

stopWorker=threading.Event()     # True:=User pressed Pause button.
workerRunning=threading.Event()  # True:=Worker thread is running.
UIdone=threading.Event()         # After a step, Worker waits until this is set.

