# Unit tests for pylife.py
#
'''
@author: Jeff Victor
'''

import unittest
import wx
import threading
from wx.lib.pubsub import pub
import pylife
import datamap 
import usermap
import constants as const
import globals as glob

class TestPyLife(unittest.TestCase):
    def setUp(self):
        self.app = wx.App()
        self.lFrame = pylife.lifeFrame()
        self.lFrame.Show()

    def tearDown(self):
        for tlw in wx.GetTopLevelWindows():
            if tlw:
                tlw.Close(force=True)
        wx.WakeUpIdle()
        self.app.MainLoop()
        del self.app

    def test_numAlive(self):
        self.lFrame.uMap.clearMap()
        dMap=self.lFrame.uMap.dMap
        dMap.setNumAlive(5)
        dMap.incrNumAlive()
        self.assertEqual(6, dMap.getNumAlive())
        dMap.decrNumAlive()
        self.assertEqual(5, dMap.getNumAlive())
        dMap.clearNumAlive()
        self.assertEqual(0, dMap.getNumAlive())
        dMap.decrNumAlive()                     # Test non-negative result.
        self.assertEqual(0, dMap.getNumAlive())

#   def test_getCenter(self):
#       self.lFrame.onClearMap(evt)
#       mat=self.lFrame.uMap.dMap.curMatrix
#       mat[10][10]=const.AC
#       (centerR, centerL)=self.lFrame.uMap.dMap.getCenter()
#       self.assertEqual(10, centerR)

    def test_reportMessage(self):
        self.lFrame.reportMessage("Message")
        self.assertEqual("Message", self.lFrame.statusBar.GetStatusText())
        
    def test_reportStats(self):
        self.lFrame.reportStats(5, 4, 3)
        self.assertEqual(format("%d cells"%4), self.lFrame.statusBar.GetStatusText(2))
        
    def test_onAbout(self):
        evt = wx.CommandEvent(wx.EVT_MENU_OPEN.typeId)
        self.lFrame.onAbout(evt)
        self.assertEqual("PyLife", self.lFrame.aboutInfo.GetName())
 
    def test_slideWindow(self):
        uMap=self.lFrame.uMap
        evt = wx.CommandEvent(wx.EVT_BUTTON.typeId)

        self.lFrame.onSlideCenter(evt)
        uMap.setCell(10, 10, const.AC)

        self.lFrame.onSlideUp(evt) 
        self.assertEqual(uMap.GetCellValue(11, 10), const.AC)
        self.lFrame.onSlideDown(evt) 
        self.assertEqual(uMap.GetCellValue(10, 10), const.AC)
        self.assertEqual(uMap.GetCellValue(11, 10), const.EC)
        self.lFrame.onSlideLeft(evt) 
        self.assertEqual(uMap.GetCellValue(10, 11), const.AC)
        self.lFrame.onSlideRight(evt) 
        self.assertEqual(uMap.GetCellValue(10, 10), const.AC)
    
        uMap.slideUp(1000)      # Should be handled correctly.
        R,C=uMap.getOffset()
        self.assertEqual(R, 0)
        uMap.slideLeft(1000)      # Should be handled correctly.
        R,C=uMap.getOffset()
        self.assertEqual(C, 0)
       
    def test_on1Step(self):
        uMap=self.lFrame.uMap
        uMap.setCell(10, 10, const.AC)
        evt = wx.CommandEvent(wx.EVT_BUTTON.typeId)
        self.lFrame.on1Step(evt)
        self.assertEqual(uMap.GetCellValue(10, 10),const.EC)

    def test_onResetSteps(self):
        self.lFrame.statusBar.SetStatusText("1 steps", 1)
        evt = wx.CommandEvent(wx.EVT_BUTTON.typeId)
        self.lFrame.onResetSteps(evt)
        self.assertEqual("0 steps", self.lFrame.statusBar.GetStatusText(1))

    def test_lifeStep(self):
        # Set a known pattern, and test the result of lifeStep.
        # This indirectly tests sumNaybors().
        uMap=self.lFrame.uMap
        dMap=self.lFrame.uMap.dMap
        AC=const.AC
        EC=const.EC
        uMap.setCell(10, 10, AC)
        uMap.setCell(20, 20, AC)
        uMap.setCell(30, 30, AC)
        evt = wx.CommandEvent(wx.EVT_BUTTON.typeId)
        self.lFrame.onClearMap(evt)
        uMap.setCell(2, 1, AC)
        uMap.setCell(2, 2, AC)
        uMap.setCell(2, 3, AC)
        dMap.lifeStep(self.lFrame.showCorpsesBox.GetValue())
        uMap.updateMap()
        self.assertEqual(uMap.GetCellValue(1, 1), EC)
        self.assertEqual(uMap.GetCellValue(1, 2), AC)
        self.assertEqual(uMap.GetCellValue(1, 3), EC)
        self.assertEqual(uMap.GetCellValue(2, 1), EC)
        self.assertEqual(uMap.GetCellValue(2, 2), AC)
        self.assertEqual(uMap.GetCellValue(2, 3), EC)
        self.assertEqual(uMap.GetCellValue(3, 1), EC)
        self.assertEqual(uMap.GetCellValue(3, 2), AC)
        self.assertEqual(uMap.GetCellValue(3, 3), EC)
        
        
    def test_loadDataFromFile(self):  # This should test file format problems.
        # This test loads a known mapfile, and verifies that the resulting map is "correct."
        dMap=self.lFrame.uMap.dMap
        AC=const.AC
        EC=const.EC
        pathname='loadtest.csv'
        dMap.setContents(1, 1, AC)
        dMap.setContents(20, 20, EC)
        try:
            with open(pathname, 'r') as loadFile:
                dMap.dLoadDataFromFile(loadFile, 0, 0)
            self.lFrame.reportMessage("The file has been loaded.")
            self.lFrame.reportStats(0, self.lFrame.uMap.dMap.getNumAlive(), 0)
        except IOError:
            self.lFrame.reportMessage(format("Cannot open file '%s'." % pathname))
            self.fail ('Could not open the file.')

        self.assertEqual(dMap.getContents(1, 1), EC)
        self.assertEqual(dMap.getContents(20, 20), AC)
        
    def test_saveDataToFile(self):
        # This test loads a known mapfile, saves it somewhere else, and then verifies the result.
        uMap=self.lFrame.uMap
        dMap=self.lFrame.uMap.dMap
        AC=const.AC
        EC=const.EC
        loadpath='loadtest.csv'
        savepath='/tmp/pylifesavetest.csv'
        uMap.moveWindow(0, 0)
        uMap.setCell(1, 1, AC)
        uMap.setCell(20, 20, EC)
        try:                                       # First load a known map.
            with open(loadpath, 'r') as loadFile:
                uMap.uLoadDataFromFile(loadFile, 0, 0)
            self.lFrame.reportMessage("The file has been loaded.")
            self.lFrame.reportStats(0, self.lFrame.uMap.dMap.getNumAlive(), 0)
        except IOError:
            self.fail (format ('Could not open the source file: %s.'%loadpath))
        try:                                       # Then save the map.
            with open(savepath, 'w') as saveFile:
                dMap.saveDataToFile(saveFile)
            self.lFrame.reportMessage("The file has been saved.")
            self.lFrame.reportStats(0, dMap.getNumAlive(), 0)
        except IOError:
            self.fail (format ('Could not open the file to save: %s.'%savepath))
        try:                                       # Now *re*load the known map.
            with open(savepath, 'r') as loadFile:
                uMap.uLoadDataFromFile(loadFile, 0, 0)
            self.lFrame.reportMessage("The file has been loaded.")
            self.lFrame.reportStats(0, dMap.getNumAlive(), 0)
        except IOError:
            self.fail (format ('Could not open the file that was saved: %s.'%savepath))

        self.assertEqual(dMap.getContents(1, 1), EC)
        self.assertEqual(dMap.getContents(20, 20), AC)

    def test_recvRunDone(self):
        steps=10
        alive=11
        rate=12
        result=13
        self.lFrame.recvRunDone(steps, alive, rate, result)
        self.assertEqual(self.lFrame.statusBar.GetStatusText(1), "10 steps") 

    def test_recvStepDone(self):
        steps=10
        alive=11
        rate=12
        self.lFrame.recvStepDone(steps, alive, rate)
        self.assertEqual(self.lFrame.statusBar.GetStatusText(1), "10 steps") 
        
    def test_onClearMap(self):
        uMap=self.lFrame.uMap
        evt = wx.CommandEvent(wx.EVT_BUTTON.typeId)
        uMap.setCell(2, 2, const.AC)
        uMap.setCell(4, 4, const.AC)
        uMap.setCell(8, 8, const.AC)
        uMap.setCell(16, 16, const.AC)
        uMap.setCell(16, 17, const.AC)
        uMap.setCell(16, 18, const.AC)
        uMap.setCell(16, 19, const.AC)

        self.lFrame.onClearMap(evt)
        self.assertEqual(uMap.GetCellValue(2, 2), const.EC)
        self.assertEqual(uMap.GetCellValue(2, 3), const.EC)
        self.assertEqual(uMap.GetCellValue(16, 18), const.EC)

    def test_showCorpses(self):
        # Create a known pattern, step once, verify results, and repeat.
        dMap=self.lFrame.uMap.dMap
        AC=const.AC
        DC=const.DC
        EC=const.EC
        evt = wx.CommandEvent(wx.EVT_BUTTON.typeId)
        self.lFrame.onClearMap(evt)
        dMap.setContents(2, 1, AC)  # Draw a '-'
        dMap.setContents(2, 2, AC) 
        dMap.setContents(2, 3, AC)  
        self.lFrame.uMap.dMap.lifeStep(True)
        self.assertEqual(dMap.getContents(1, 1), EC)  # Verify '|'
        self.assertEqual(dMap.getContents(2, 1), DC)
        self.assertEqual(dMap.getContents(2, 2), AC)
        self.lFrame.uMap.dMap.lifeStep(False)
        self.assertEqual(dMap.getContents(1, 2), EC)  # Verify '-'
        self.assertEqual(dMap.getContents(2, 1), AC)
        self.assertEqual(dMap.getContents(3, 2), EC)

    def test_runMany(self):
        dMap=self.lFrame.uMap.dMap
        uMap=self.lFrame.uMap
        uMap.moveWindow(0, 0)
        # Set desired initial state, call method, verify.
        AC=const.AC
        EC=const.EC

        glob.numSteps=0
        evt = wx.CommandEvent(wx.EVT_BUTTON.typeId)
        self.lFrame.onClearMap(evt)
        uMap.setCell(11, 12, AC)  # Draw a glider.
        uMap.setCell(12, 13, AC)
        uMap.setCell(13, 11, AC)
        uMap.setCell(13, 12, AC)
        uMap.setCell(13, 13, AC)

        thrRunMany = threading.Thread(target=self.lFrame.uMap.uRunMany,args=(10, 0, 0, 0, 15, True))
        thrRunMany.start()
        thrRunMany.join()
        uMap.updateMap()   # uRunMany does not update the UI in batch mode.
        
        self.assertEqual(glob.numSteps, 10) # Also tests reportStats()
        self.assertEqual(uMap.GetCellValue(15, 13), AC)
        self.assertEqual(uMap.GetCellValue(14, 15), AC)
        self.assertEqual(uMap.GetCellValue(11, 12), EC)

#   def test_onRun(self):
#       uMap=self.lFrame.uMap
#       AC=const.AC
#       EC=const.EC
#
#       glob.numSteps=0
#       evt = wx.CommandEvent(wx.EVT_BUTTON.typeId)
#       self.lFrame.onClearMap(evt)
#       uMap.setCell(11, 12, AC)  # Draw a glider.
#       uMap.setCell(12, 13, AC)
#       uMap.setCell(13, 11, AC)
#       uMap.setCell(13, 12, AC)
#       uMap.setCell(13, 13, AC)

        
if __name__ == '__main__':
    unittest.main()
