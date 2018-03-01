'''
Created on Feb 1, 2018

@author: Jeff Victor
'''

# This file contains the userMap class. This represents the functionality and data
# of the on-screen map presented to the user.
# The code also serves as an intermediate layer between the high level logic and 
# the data structure that stores map state.

import wx.grid
import constants as const
import globals as glob
import datamap as data

class userMap(wx.grid.Grid):
    def __init__(self, *args, **kw):
        wx.grid.Grid.__init__(self, *args, **kw)
        self.CreateGrid(const.VIEWROWS, const.VIEWCOLS)

        self.EnableGridLines(False) # Hide grid lines.
        self.SetColLabelSize(0)     # Hide column labels.
        self.SetDefaultCellAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
        self.SetRowLabelSize(0)     # Hide row labels.
        self.SetDefaultColSize(3, resizeExistingCols=False)
        self.SetDefaultRowSize(3, resizeExistingRows=False)
        for r in range(const.VIEWROWS):    # Prevent user from entering data.
            for c in range(const.VIEWCOLS):
                self.SetReadOnly(r, c, True)
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.onCellLeftClick)

        # Create the data structure that is the "real" map.
        self.dMap=data.datamap()
        self._offsetR=(const.NUMROWS-const.VIEWROWS)/2   # Offset is distance from 
        self._offsetC=(const.NUMCOLS-const.VIEWCOLS)/2   # edge to top-right corner
 
    # Update the userMap from the underlying data structure.
    def updateMap(self):
        for row in range(const.VIEWROWS):
            for col in range(const.VIEWCOLS):
                self.SetCellValue(row, col, self.dMap.getContents(row+self._offsetR, col+self._offsetC)) 
 
    def getOffset(self):
        return (self._offsetR, self._offsetC)

    def slideUp(self, amount):
        if self._offsetR > 0:
            self._offsetR -= amount
            if self._offsetR <0: self._offsetR=0
            self.updateMap()

    def slideLeft(self, amount):
        if self._offsetC > 0:
            self._offsetC -= amount
            if self._offsetC <0: self._offsetC=0
            self.updateMap()

    def slideCenter(self):
        self._offsetR=(const.NUMROWS-const.VIEWROWS)/2   # Offset is distance from 
        self._offsetC=(const.NUMCOLS-const.VIEWCOLS)/2   # edge to top-right corner
        self.updateMap()

    def slideRight(self, amount):
        if self._offsetC < (const.NUMCOLS-const.VIEWCOLS):
            self._offsetC += amount
            self.updateMap()

    def slideDown(self, amount):
        if self._offsetR < (const.NUMROWS-const.VIEWROWS):
            self._offsetR += amount
            self.updateMap()

    def moveWindow(self, row, col):
        self._offsetR=row
        self._offsetC=col
        self.updateMap()

    def setCell(self, row, col, value):
        self.SetCellValue(row, col, value)
        self.dMap.setContents(row+self._offsetR, col+self._offsetC, value)

    def clearMap(self):
        for row in range(const.VIEWROWS):
            for col in range(const.VIEWCOLS):
                # Minimize calls to SetCellValue.
                if self.dMap.getContents(row+self._offsetR, col+self._offsetC) !=const.EC:  
                    self.setCell(row, col, const.EC)

    # The UI supports single-step operation via this method.
    def umapStep(self, showCorpses):
        self.dMap.lifeStep(showCorpses)

    # This method is called when the user clicks on the map to create or destroy
    def onCellLeftClick(self, evt):
        dataR=evt.GetRow()+self._offsetR
        dataC=evt.GetCol()+self._offsetC

        if self.dMap.getContents(dataR, dataC) == const.EC:
            self.dMap.setContents(dataR, dataC, const.AC)
        elif self.dMap.getContents(dataR, dataC) == const.AC:
            self.dMap.setContents(dataR, dataC, const.EC)
        else: #self.dMap.getContents(dataR, dataC) == const.DC:
            self.dMap.setContents(dataR, dataC, const.EC)

        self.SetCellValue(evt.GetRow(), evt.GetCol(), self.dMap.getContents(dataR, dataC))

        wx.GetTopLevelParent(self).reportStats(glob.numSteps, self.dMap.getNumAlive(), 0)
        evt.Skip()

    # This method loads a file into the datamap so that it appears in the usermap.
    # applies the sliding window to the request to load a mapfile.
    def uLoadDataFromFile(self, loadFile, row, col):
        self.dMap.dLoadDataFromFile (loadFile, row+self._offsetR, col+self._offsetC)

    # This method merely provides separation between the UI and the datamap module.
    def uRunMany(self, stopSteps, stopStill, stopOscillators, showCorpsesBox, speedGoal, batch):
        self.dMap.dRunMany(stopSteps, stopStill, stopOscillators, showCorpsesBox, speedGoal, batch)
        

if __name__ == '__main__':
    print "This module should only be used with pylife.py"
