# Unit tests for pylife

import unittest
import wx
import pylife

AC='*'
EC=''

class TestInitUI(unittest.TestCase):
    global AC
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
        pylife.lifeFrame.reportStats(self.lFrame, 5, 4, 3)
        self.assertEqual(format("%d %s"%(4, AC)), self.lFrame.statusBar.GetStatusText(2))
        
    def test_onAbout(self):
        evt = wx.CommandEvent(wx.EVT_MENU_OPEN.typeId)
        pylife.lifeFrame.onAbout(self.lFrame, evt)
        self.assertEqual("PyLife", self.lFrame.aboutInfo.GetName())
        
    def test_lifeStep(self):
        mat=self.lFrame.lGrid.curMatrix
        mat[2][1]=AC
        mat[2][2]=AC
        mat[2][3]=AC
        print mat[2][1]+mat[2][2]+mat[2][3]
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
        print mat[2][1]+mat[2][2]+mat[2][3]

        
if __name__ == '__main__':
    unittest.main()
