# Unit tests for pylife

import unittest
import wx
import pylife

#AC='*'
#EC=''

class TestPyLife(unittest.TestCase):
    def setUp(self):
        self.app = wx.PySimpleApp()
        self.lFrame = pylife.lifeFrame()
        self.lFrame.Show()

    def tearDown(self):
        wx.CallAfter(self.app.Exit)
        self.app.MainLoop()

    def test_reportMessage(self):
        pylife.lifeFrame.reportMessage(self.lFrame, "Message")
        self.assertEqual("Message", self.lFrame.statusBar.GetStatusText())
        
    def test_reportStats(self):
        AC=pylife.AC
        pylife.lifeFrame.reportStats(self.lFrame, 5, 4, 3)
        self.assertEqual(format("%d %s"%(4, AC)), self.lFrame.statusBar.GetStatusText(2))
        
    def test_onAbout(self):
        evt = wx.CommandEvent(wx.EVT_MENU_OPEN.typeId)
        pylife.lifeFrame.onAbout(self.lFrame, evt)
        self.assertEqual("PyLife", self.lFrame.aboutInfo.GetName())
        
    def test_lifeStep(self):
        # Set a known pattern, and test the result of lifeStep.
        # This indirectly tests sumNaybors().
        mat=self.lFrame.lGrid.curMatrix
        for x in range(pylife.NUMROWS): 
            for y in range(pylife.NUMCOLS):
                mat[x][y]=''
        AC=pylife.AC
        EC=pylife.EC
        mat[2][1]=AC
        mat[2][2]=AC
        mat[2][3]=AC
        pylife.lifeStep(mat)
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
                pylife.lifeFrame.loadDataFromFile(self.lFrame, loadFile)
            pylife.lifeFrame.reportMessage(self.lFrame, "The file has been loaded.")
            pylife.lifeFrame.reportStats(self.lFrame, 0, pylife.numAlive, 0)
        except IOError:
            pylife.lifeFrame.reportMessage(self.lFrame, format("Cannot open file '%s'." % pathname))
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
                pylife.lifeFrame.loadDataFromFile(self.lFrame, loadFile)
            pylife.lifeFrame.reportMessage(self.lFrame, "The file has been loaded.")
            pylife.lifeFrame.reportStats(self.lFrame, 0, pylife.numAlive, 0)
        except IOError:
            self.fail (format ('Could not open the source file: %s.'%loadpath))
        try:
            with open(savepath, 'w') as saveFile:
                pylife.lifeFrame.saveDataToFile(self.lFrame, saveFile)
            pylife.lifeFrame.reportMessage(self.lFrame, "The file has been saved.")
            pylife.lifeFrame.reportStats(self.lFrame, 0, pylife.numAlive, 0)
        except IOError:
            self.fail (format ('Could not open the file to save: %s.'%savepath))
        try:                                       # First *re*load the known map.
            with open(savepath, 'r') as loadFile:
                pylife.lifeFrame.loadDataFromFile(self.lFrame, loadFile)
            pylife.lifeFrame.reportMessage(self.lFrame, "The file has been loaded.")
            pylife.lifeFrame.reportStats(self.lFrame, 0, pylife.numAlive, 0)
        except IOError:
            self.fail (format ('Could not open the file that was saved: %s.'%savepath))

        self.assertEqual(mat[1][1],EC)
        self.assertEqual(mat[20][20],AC)
        
        
if __name__ == '__main__':
    unittest.main()
