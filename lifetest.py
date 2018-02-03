# Unit tests for pylife

import unittest
import wx
import pylife

AC='*'   # Alive Cell

class TestInitUI(unittest.TestCase):
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

if __name__ == '__main__':
    unittest.main()
