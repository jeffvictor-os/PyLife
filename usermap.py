'''
Created on Feb 1, 2018

@author: Jeff Victor
'''

# This file contains the userMap class. This represents the functionality and data
# of the on-screen map presented to the user.
# The code also serves as an intermediate layer between the high level logic and 
# the data structure that stores map state.

# pylife-sepfuncs.py: separate into 4 modules:
# 1. Frame and Control panel
# 2. Map presentation
# 3. Data representation
# 4. Globals

import wx.grid
import threading
from wx.lib.pubsub import Publisher
import constants as const
import globals as glob
import datamap as data
import pylifeui

#stopWorker=threading.Event()     # True:=User pressed Pause button.
#workerRunning=threading.Event()  # True:=Worker thread is running.
#UIdone=threading.Event()         # After a step, Worker waits until this is set.


class userMap(wx.grid.Grid):
    def __init__(self, *args, **kw):
        wx.grid.Grid.__init__(self, *args, **kw)
        self.CreateGrid(const.NUMROWS, const.NUMCOLS)

        self.EnableGridLines(False) # Hide grid lines.
        self.SetColLabelSize(0)     # Hide column labels.
        self.SetDefaultCellAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
        self.SetRowLabelSize(0)     # Hide row labels.
        self.SetDefaultColSize(3, resizeExistingCols=True)
        self.SetDefaultRowSize(5, resizeExistingRows=False)
        for r in range(const.NUMROWS):    # Prevent user from entering data.
            for c in range(const.NUMCOLS):
                self.SetReadOnly(r, c, True)
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.onCellLeftClick)

        # Create the matrix that contains "truth" for the cells.
#       self.curMatrix=[['' for x in range(const.NUMROWS)] for y in range(const.NUMCOLS)]
        self.map=data.datamap()
 
    # When we need to update the userMap from the underlying data structure.
    def updateMap(self):
        for row in range(const.NUMROWS):
            for col in range(const.NUMCOLS):
                self.SetCellValue(row, col, self.map.getContents(row, col))        
           
    def clearMap(self):
        for row in range(const.NUMROWS):
            for col in range(const.NUMCOLS):
                if self.map.getContents(row, col) !=const.EC:  # Avoid unnecessary SetCellValue's.
                    self.map.setContents(row, col, const.EC)
                    self.SetCellValue(row, col, const.EC)

    def umapStep(self, showCorpses):
        self.map.lifeStep(showCorpses)


    def onCellLeftClick(self, evt):
        if self.map.getContents(evt.GetRow(), evt.GetCol()) == const.EC:
            self.map.setContents(evt.GetRow(), evt.GetCol(), const.AC)
            self.map.incrNumAlive()
        elif self.map.getContents(evt.GetRow(), evt.GetCol()) == const.AC:
            self.map.setContents(evt.GetRow(), evt.GetCol(), const.EC)
            self.map.decrNumAlive()
        else: #self.map.getContents(evt.GetRow(), evt.GetCol()) == const.DC:
            self.map.setContents(evt.GetRow(), evt.GetCol(), const.EC)
        self.SetCellValue(evt.GetRow(), evt.GetCol(), self.map.getContents(evt.GetRow(), evt.GetCol()))

        wx.GetTopLevelParent(self).reportStats(glob.numSteps, self.map.getNumAlive(), 0)
        evt.Skip()

    # This method merely provides separation between the UI and the datamap module.
    def uRunMany(self, stopSteps, stopStill, stopOscillators, showCorpsesBox, showSteps, speedGoal):
        self.map.dRunMany(stopSteps, stopStill, stopOscillators, showCorpsesBox, showSteps, speedGoal)
        

if __name__ == '__main__':
    print "Use this module with pylife"
