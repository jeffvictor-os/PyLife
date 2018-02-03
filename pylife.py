'''
Created on Feb 1, 2018

@author: jeff victor
'''

import wx




class lifeFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, title='Game of Life')
        self.InitUI()

    def InitUI(self):
        # Menu Bar, then Status Bar, then panels
                # Menu Bar
        menuBar = wx.MenuBar()

        fileMenu = wx.Menu()
        exitMenuItem = fileMenu.Append(wx.NewId(), "Exit", "Exit Life")
        menuBar.Append(fileMenu, "&File")
        self.Bind(wx.EVT_MENU, self.onExit, exitMenuItem)

        helpMenu = wx.Menu()
        aboutMenuItem = helpMenu.Append(wx.NewId(), "About...", "About Life")
        menuBar.Append(helpMenu, "&Help")
        self.Bind(wx.EVT_MENU, self.onAbout, aboutMenuItem)

        self.SetMenuBar(menuBar)

    def onExit(self, event):
        self.closeProgram()

    def closeProgram(self):
        self.Close()

    def onAbout(self, event):
        description="Conway's Game of Life simulates growth and death of cells."
        aboutInfo = wx.AboutDialogInfo()
        aboutInfo.SetName('PyLife')
        aboutInfo.SetDescription(description)
        aboutInfo.AddDeveloper('Jeff Victor')
        wx.AboutBox(aboutInfo)




if __name__ == '__main__':
    app = wx.PySimpleApp()
    lFrame = lifeFrame()
    lFrame.Show()
    app.MainLoop()
