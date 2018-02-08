# Unit tests for pylife.py
#
# @author: Jeff Victor

import unittest
import wx
import pylife

class TestPyLife(unittest.TestCase):
    def setUp(self):
        self.app = wx.PySimpleApp()
        self.lFrame = pylife.lifeFrame()
        self.lFrame.Show()

    def tearDown(self):
        wx.CallAfter(self.app.Exit)
        self.app.MainLoop()

    def test_reportMessage(self):
        self.lFrame.reportMessage("Message")
        self.assertEqual("Message", self.lFrame.statusBar.GetStatusText())
        
    def test_reportStats(self):
        AC=pylife.AC
        self.lFrame.reportStats(5, 4, 3)
        self.assertEqual(format("%d %s"%(4, AC)), self.lFrame.statusBar.GetStatusText(2))
        
    def test_onAbout(self):
        evt = wx.CommandEvent(wx.EVT_MENU_OPEN.typeId)
        self.lFrame.onAbout(evt)
        self.assertEqual("PyLife", self.lFrame.aboutInfo.GetName())
        
    def test_lifeStep(self):
        # Set a known pattern, and test the result of lifeStep.
        # This indirectly tests sumNaybors().
        mat=self.lFrame.lGrid.curMatrix
        evt = wx.CommandEvent(wx.EVT_BUTTON.typeId)
        self.lFrame.onClearGrid(evt)
        AC=pylife.AC
        EC=pylife.EC
        mat[2][1]=AC
        mat[2][2]=AC
        mat[2][3]=AC
        pylife.lifeStep(mat, self.lFrame.showCorpsesBox.GetValue())
        self.assertEqual(mat[1][1],EC)
        self.assertEqual(mat[1][2],AC)
        self.assertEqual(mat[1][3],EC)
        self.assertEqual(mat[2][1],EC)
        self.assertEqual(mat[2][2],AC)
        self.assertEqual(mat[2][3],EC)
        self.assertEqual(mat[3][1],EC)
        self.assertEqual(mat[3][2],AC)
        self.assertEqual(mat[3][3],EC)
        
        
    def test_loadDataFromFile(self):
        # This test loads a known map-file, and verifies that the resulting map is "correct."
        AC=pylife.AC
        EC=pylife.EC
        pathname='loadtest.csv'
        mat=self.lFrame.lGrid.curMatrix
        mat[1][1]=AC
        mat[20][20]=EC
        try:
            with open(pathname, 'r') as loadFile:
                self.lFrame.loadDataFromFile(loadFile)
            self.lFrame.reportMessage("The file has been loaded.")
            self.lFrame.reportStats(0, pylife.numAlive, 0)
        except IOError:
            self.lFrame.reportMessage(format("Cannot open file '%s'." % pathname))
            self.fail ('Could not open the file.')

        self.assertEqual(mat[1][1],EC)
        self.assertEqual(mat[20][20],AC)
        
    def test_saveDataToFile(self):
        # This test loads a known map-file, saves it somewhere else, and then verifies the result.
        AC=pylife.AC
        EC=pylife.EC
        loadpath='loadtest.csv'
        savepath='/tmp/pylifesavetest.csv'
        mat=self.lFrame.lGrid.curMatrix
        mat[1][1]=AC
        mat[20][20]=EC
        try:                                       # First load a known map.
            with open(loadpath, 'r') as loadFile:
                self.lFrame.loadDataFromFile(loadFile)
            self.lFrame.reportMessage("The file has been loaded.")
            self.lFrame.reportStats(0, pylife.numAlive, 0)
        except IOError:
            self.fail (format ('Could not open the source file: %s.'%loadpath))
        try:                                       # Then save the map.
            with open(savepath, 'w') as saveFile:
                self.lFrame.saveDataToFile(saveFile)
            self.lFrame.reportMessage("The file has been saved.")
            self.lFrame.reportStats(0, pylife.numAlive, 0)
        except IOError:
            self.fail (format ('Could not open the file to save: %s.'%savepath))
        try:                                       # Now *re*load the known map.
            with open(savepath, 'r') as loadFile:
                self.lFrame.loadDataFromFile(loadFile)
            self.lFrame.reportMessage("The file has been loaded.")
            self.lFrame.reportStats(0, pylife.numAlive, 0)
        except IOError:
            self.fail (format ('Could not open the file that was saved: %s.'%savepath))

        self.assertEqual(mat[1][1],EC)
        self.assertEqual(mat[20][20],AC)
        
    def test_onClearGrid(self):
        mat=self.lFrame.lGrid.curMatrix
        evt = wx.CommandEvent(wx.EVT_BUTTON.typeId)
        self.lFrame.onClearGrid(evt)
        self.assertEqual(mat[1][1],pylife.EC)
        self.assertEqual(mat[2][3],pylife.EC)
        self.assertEqual(mat[6][8],pylife.EC) 

    def test_showCorpses(self):
        # Create a known pattern, step once, verify results, and repeat.
        AC=pylife.AC
        DC=pylife.DC
        EC=pylife.EC
        mat=self.lFrame.lGrid.curMatrix
        evt = wx.CommandEvent(wx.EVT_BUTTON.typeId)
        self.lFrame.onClearGrid(evt)
        mat[2][1]=AC   # Draw a '-'
        mat[2][2]=AC
        mat[2][3]=AC
        pylife.lifeStep(mat, True)
        self.assertEqual(mat[1][1],EC)    # Verify '|'
        self.assertEqual(mat[2][1],DC)
        self.assertEqual(mat[2][2],AC)
        pylife.lifeStep(mat, False)
        self.assertEqual(mat[1][2],EC)    # Verify '-'
        self.assertEqual(mat[2][1],AC)
        self.assertEqual(mat[3][2],EC)
        
    def test_runMany(self):
        # Set desired initial state, call method, verify.
        mat=self.lFrame.lGrid.curMatrix
        self.lFrame.inputStopSteps.ChangeValue(str(10))
        pylife.numSteps=0
        evt = wx.CommandEvent(wx.EVT_BUTTON.typeId)
        self.lFrame.onClearGrid(evt)
        mat[1][2]=pylife.AC   # Draw a glider.
        mat[2][3]=pylife.AC
        mat[3][1]=pylife.AC
        mat[3][2]=pylife.AC
        mat[3][3]=pylife.AC
        pylife.numAlive=5

        self.lFrame.runMany(mat, 10, 0)
        self.assertEqual(pylife.numSteps, 10) # Also tests reportStats()
        self.assertEqual(mat[5][3],pylife.AC)
        self.assertEqual(mat[4][5],pylife.AC)
        self.assertEqual(mat[1][2],pylife.EC)
          
            
if __name__ == '__main__':
    unittest.main()
