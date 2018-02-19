'''
Created on Feb 1, 2018

@author: Jeff Victor
'''

# This module contains all of the code that manipulates the data structures
# that store map state.

# pylife-sepfuncs.py: separate into 4 modules:
# 1. Frame and Control panel
# 2. Map presentation
# 3. Data representation
# 4. Globals

import wx
import csv
import time
import timeit
import threading
from wx.lib.pubsub import Publisher
import constants as const
import globals as glob

class datamap():
    def __init__(self):
        self._numAlive=0
        self.curMatrix=[['' for x in range(const.NUMROWS)] for y in range(const.NUMCOLS)]

    def getNumAlive(self):
        return self._numAlive

    def incrNumAlive(self):
        self._numAlive += 1
        return self._numAlive

    def decrNumAlive(self):
        self._numAlive -= 1
        return self._numAlive

    def clearNumAlive(self):
        self._numAlive = 0
        return self._numAlive

    # These funcs are used by the UI to get/set the status of a cell location.
    def getContents(self, row, col):
        return self.curMatrix[row][col]

    def setContents(self, row, col, value):
        self.curMatrix[row][col]=value

    # Load data from a file into the in-memory map.
    def loadDataFromFile(self, loadFile):
        self._numAlive=0
        rownum=-1
        lreader = csv.reader(loadFile)
        for row in lreader:
            rownum +=1
            if rownum>=const.NUMROWS:   # Safely handle oversized files.
                break;
            for col in range(const.NUMCOLS):
                self.curMatrix[rownum][col]='' # Default value...
                if col<len(row):                     # ..handles undersized lines.
                    if row[col] != '0':
                        if row[col]==const.AC:
                            self._numAlive+=1
                            self.curMatrix[rownum][col]=row[col]

    # Save data from the in-memory map to a file in CSV format.
    def saveDataToFile(self, saveFile):
        swriter = csv.writer(saveFile)
        # First create a list that represents the row.
        for rownum in range(const.NUMROWS):
            row=[]
            for colnum in range(const.NUMCOLS):
                row.append(self.curMatrix[rownum][colnum])
                if row[-1]=='':
                    row[-1]='0'
            # Then write the list as CSV.
            swriter.writerow(row)


    # Run many iterations/generations.
    def dRunMany(self, stopAfterSteps, stopWhenStill, stopWhenOscillators, showCorpses, showSteps, speedGoal):
        # Data Initializations
        keepGoing=True  # Set to False when certain conditions are met.
        newHash=0       # Used to detect static map, possible with blinkers.
        oldHash1=0      # Used to detect blinkers.
        oldHash2=0      # Used to detect blinkers.
        oldHash3=0      # Used to detect blinkers.
        oldHash4=0      # Used to detect blinkers.
        step=1          # To limit steps, and to time perf samples.
        speedMeasured=0 # Stores rate of generations
    
        stepSpeedMeasured=0
        result="completed"
        glob.stopWorker.clear()
        glob.workerRunning.set()
    
        # We need to start with a "good guess" about the necessary delay to achieve 
        # the user's desired step rate.
        if speedGoal > 0:
            delay = 1.0/speedGoal      # This is a first guess.
            print "Goal= %d, Delay=%0.4f" % (speedGoal, delay)
    
        # Starting time used to report the step rate for the entire run.
        startTime=1.0*timeit.default_timer()
    
        # Report the rate every 10 steps, and optionally adjust step rate every 10 steps.
        # This is the starting time that will be used for each 10-step interval.
        stepStartTime=1.0*timeit.default_timer()
    
        # Main loop
        while keepGoing:
            newHash=self.lifeStep(showCorpses)  # Actually "live" for a step. :-)
    
            if step % 10 == 0:    # If using a rate cap, tune the delay.
                stepEndTime=1.0*timeit.default_timer()
                stepElapsed=stepEndTime-stepStartTime
                stepSpeedMeasured=10/stepElapsed
                stepStartTime=1.0*timeit.default_timer()  # Ready to time next loop.
                if speedGoal > 1.1*stepSpeedMeasured:
                    delay = 0.9*delay
                    if speedGoal: print "Tuning delay down to %0.4f." % delay
                if speedGoal>0 and speedGoal < 0.9*stepSpeedMeasured:
                    delay = 1.1*delay
                    if speedGoal: print "Tuning delay up   to %0.4f." % delay
    
            if showSteps==True:
                # Clear the semaphore, send a msg to the UI, wait for it to finish its update.
                glob.UIdone.clear()
                msg=format("%d,%d,%d" % (glob.numSteps, self._numAlive, stepSpeedMeasured))
                wx.CallAfter(Publisher().sendMessage, "stepdone", msg) # Tell GUI to refresh.
                glob.UIdone.wait()  # Wait for recvStepDone to signal completion of refresh.
    
            # Detect requested termination conditions, express same.
            if glob.stopWorker.isSet():
                result="was interrupted"
                keepGoing=False
    
            step += 1
            if stopWhenStill and newHash==oldHash1:
                keepGoing=False
                result='stopped with no changes'
            elif stopWhenOscillators and (newHash==oldHash2 or newHash==oldHash3 or newHash==oldHash4):
                keepGoing=False
                result='stopped with oscillators'
            else:
                oldHash4=oldHash3
                oldHash3=oldHash2
                oldHash2=oldHash1
                oldHash1=newHash
            if (stopAfterSteps>0 and step>stopAfterSteps):
                keepGoing=False
                result='completed all steps'
            if self._numAlive<1:
                result='ended with no cells'
                keepGoing=False  
            if speedGoal>0 and keepGoing==True:
                time.sleep(delay)

        endTime=1.0*timeit.default_timer()
        elapsed=endTime-startTime
        speedMeasured=step/elapsed

        msg=format("%d,%d,%d,%s" % (glob.numSteps, self._numAlive, speedMeasured, result))
        wx.CallAfter(Publisher().sendMessage, "rundone", msg) # Tell GUI all steps are done.
        glob.stopWorker.clear()
        

    # "Live" for one generation.
    def lifeStep(self, showCorpses):
        glob.numSteps += 1
        lifeHash=0    # Used to detect map that's static, possible with blinkers.
    
        nextMat=[['' for x in range(const.NUMROWS)] for y in range(const.NUMCOLS)]
    
        if showCorpses: corpse=const.DC  # Leave a mark for a cell that died recently.
        else:           corpse=const.EC
    
        # Build a new map of cells first...
        for row in range(0,const.NUMROWS):
            for col in range(0,const.NUMCOLS):
                naybors=self.sumNaybors(row, col)
                currentCell= self.curMatrix[row][col]
                if currentCell == const.AC:                # Was alive
                    if naybors<2 or naybors>3:
                        nextMat[row][col]=corpse     # Died.
                        self._numAlive -= 1
                    else:
                        nextMat[row][col]=const.AC         # Still alive
                else:                                # Was dead
                    if naybors==3:
                        nextMat[row][col]=const.AC         # New cell
                        self._numAlive   += 1
                    else:
                        nextMat[row][col]=const.EC         # Still dead
    
        # ...then copy the new map into the UI map so someone else can refresh the UI.
        for row in range(const.NUMROWS):
            for col in range(const.NUMCOLS):
                self.curMatrix[row][col]=nextMat[row][col]
                if self.curMatrix[row][col]==const.AC:
                    lifeHash += row**2+col
                    
        return lifeHash

    # Count the number of living neighbors (out of 8 potential cells).
    def sumNaybors(self, row, col):   # Count the number of neighbors of this cell.
        last=const.NUMROWS-1
        naybors=0
    
        # Except for cells at the edges, check the previous and next rows and columns.
        rowstart=row-1
        colstart=col-1
        rowend=row+1
        colend=col+1
    
        # Detect edges and adjust if necessary.
        if row==0:    rowstart=0
        if col==0:    colstart=0
        if row==last: rowend=last
        if col==last: colend=last
    
        for checkrow in range(rowstart, rowend+1):
            for checkcol in range(colstart, colend+1):
                if not (checkrow==row and checkcol==col):
                    if const.AC==self.curMatrix[checkrow][checkcol]:
                        naybors += 1
    
        return (naybors)

if __name__ == '__main__':
    print "This module should only be used with pylifeui.py"
