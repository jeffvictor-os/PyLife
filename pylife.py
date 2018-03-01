'''
Created on Feb 1, 2018

@author: Jeff Victor
'''

# This is the main module. It manages the window and the user control panel.
# This module does not contain code for the presentation of the map to 
# the user. Also, it does not contain any knowledge about the data
# structure that stores map state.


import wx
import wx.adv 
import wx.grid
from wx.lib.pubsub import pub
import threading
import constants as const
import globals as glob
import datamap as data
import usermap as user

class lifeFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, title='Game of Life')
        self.InitUI()

    def InitUI(self):
        # Menu Bar, then Status Bar, then Panels
        
        # Menu Bar
        menuBar = wx.MenuBar()

        fileMenu = wx.Menu()
        menuBar.Append(fileMenu, "&File")
        loadMenuItem = fileMenu.Append(wx.NewId(), "&Load...", "Load a file")
        self.Bind(wx.EVT_MENU, self.onMenuLoad, loadMenuItem)
        saveMenuItem = fileMenu.Append(wx.NewId(), "&Save...", "Save a file")
        self.Bind(wx.EVT_MENU, self.onMenuSave, saveMenuItem)
        exitMenuItem = fileMenu.Append(wx.NewId(), "E&xit", "Exit Life")
        self.Bind(wx.EVT_MENU, self.onExit, exitMenuItem)

        helpMenu = wx.Menu()
        aboutMenuItem = helpMenu.Append(wx.NewId(), "&About...", "About Life")
        usageMenuItem = helpMenu.Append(wx.NewId(), "&Usage...", "Instructions")
        menuBar.Append(helpMenu, "&Help")
        self.Bind(wx.EVT_MENU, self.onAbout, aboutMenuItem)
        self.Bind(wx.EVT_MENU, self.onHelp, usageMenuItem)

        self.SetMenuBar(menuBar)

        # Status Bar
        self.statusBar=self.CreateStatusBar(6)
        self.statusBar.SetStatusWidths([225,100,75,75,150,75])
        self.statusBar.SetStatusText('Hello Life Form!')

        # Two panels: one for the controls, one for the grid.
        self.mainSizer      = wx.BoxSizer(wx.HORIZONTAL)
        self.ctrlPanel=wx.Panel(self, size=(200, -1))
        self.lifePanel=wx.Panel(self)
        self.mainSizer.Add(self.ctrlPanel, 0, wx.ALL, 5)
        self.mainSizer.Add(self.lifePanel, 3, wx.ALL, 5)

        # Left panel: Control panel
        self.ctrlSizer        = wx.BoxSizer(wx.VERTICAL)
        self.ctrlPanel.SetSizer(self.ctrlSizer)
        self.ctitle = wx.StaticText(self.ctrlPanel, wx.ID_ANY, 'Control Panel')
        self.ctitleSizer        = wx.BoxSizer(wx.HORIZONTAL)
        self.ctitleSizer.Add(self.ctitle, 0, wx.ALL, 5)
        self.ctrlSizer.Add(self.ctitleSizer, 0, wx.CENTER)

        # The actual controls are created after the Life (right) Panel.
        
        # Life Panel: wx.grid
        self.lifeSizer        = wx.BoxSizer(wx.VERTICAL)
        self.lifePanel.SetSizer(self.lifeSizer)
        self.ltitle = wx.StaticText(self.lifePanel, wx.ID_ANY, 'Life Map - Click to Create Life')
        self.ltitleSizer       = wx.BoxSizer(wx.HORIZONTAL)
        self.ltitleSizer.Add(self.ltitle, 0, wx.ALL, 5)
        self.lifeSizer.Add(self.ltitleSizer, 0, wx.CENTER)

        # Instantiate the Map Presentation
        self.uMap=user.userMap(self.lifePanel)
        self.lifeSizer.Add(self.uMap, 0, wx.LEFT, 5)

        # Controls for the Control Panel
        
        # Button to run one step (generation)
        self.oneStepBtn = wx.Button(self.ctrlPanel, wx.ID_ANY, '1-Step')
        self.Bind(wx.EVT_BUTTON, self.on1Step, self.oneStepBtn)
        self.oneStepSizer       = wx.BoxSizer(wx.HORIZONTAL)
        self.oneStepSizer.Add(self.oneStepBtn, 0, wx.ALL, 0)

        # Controls to specify termination conditions for a run.        
        self.runStopStepsBox = wx.CheckBox(self.ctrlPanel, wx.ID_ANY, style=wx.CHK_2STATE, label="Stop at...")
        self.inputStopSteps = wx.TextCtrl(self.ctrlPanel, wx.ID_ANY,'10', size=(50,-1), style=wx.TE_RIGHT|wx.TE_PROCESS_ENTER)
        self.labelStopSteps = wx.StaticText(self.ctrlPanel, wx.ID_ANY, 'Steps')
        self.manyStepSizer  = wx.BoxSizer(wx.HORIZONTAL) 
        self.manyStepSizer.Add(self.runStopStepsBox, 0, wx.RIGHT|wx.CENTER, 5)
        self.manyStepSizer.Add(self.inputStopSteps, 1, wx.ALL|wx.EXPAND|wx.CENTER, 1)
        self.manyStepSizer.Add(self.labelStopSteps, 0, wx.ALL|wx.CENTER, 5)

        # Controls to throttle the step rate.
        self.stepRateBox = wx.CheckBox(self.ctrlPanel, wx.ID_ANY, style=wx.CHK_2STATE, label="Limit to")
        self.inputStepRate  = wx.TextCtrl(self.ctrlPanel, wx.ID_ANY,'0', size=(30,-1), style=wx.TE_RIGHT|wx.TE_PROCESS_ENTER)
        self.labelStepRate  = wx.StaticText(self.ctrlPanel, wx.ID_ANY, 'Steps/sec')
        self.stepRateSizer  = wx.BoxSizer(wx.HORIZONTAL)
        self.stepRateSizer.Add(self.stepRateBox, 0, wx.RIGHT|wx.CENTER, 1)
        self.stepRateSizer.Add(self.inputStepRate, 1, wx.ALL|wx.EXPAND|wx.CENTER, 5)
        self.stepRateSizer.Add(self.labelStepRate, 0, wx.ALL|wx.CENTER, 1)    

        # Stop a run when the map stops changing.
        self.runStillBox = wx.CheckBox(self.ctrlPanel, wx.ID_ANY, label='Stop when just still lifes')
        self.runStillBox.SetValue(True)

        # Stop a run when the map is static plus blinkers.
        self.runOscillatorsBox = wx.CheckBox(self.ctrlPanel, wx.ID_ANY, label='Stop when just oscillators')
        self.runOscillatorsBox.SetValue(True)
        
        # Show the most recently deceased cells?         
        self.showCorpsesBox = wx.CheckBox(self.ctrlPanel, wx.ID_ANY, 'Show corpses')
        
        # Show map after each step in a run.
        self.showStepsBox = wx.CheckBox(self.ctrlPanel, wx.ID_ANY, 'Show each step')
        self.showStepsBox.SetValue(True)

        # Buttons to run and pause.
        self.runManyBtn    = wx.Button(self.ctrlPanel, wx.ID_ANY, 'Run', style=wx.EXPAND)
        self.Bind(wx.EVT_BUTTON, self.onRun, self.runManyBtn)
        self.pauseBtn = wx.Button(self.ctrlPanel, wx.ID_ANY, 'Pause')
        self.Bind(wx.EVT_BUTTON, self.onPause, self.pauseBtn)
        self.pauseBtn.Disable()
        self.runPauseSizer       = wx.BoxSizer(wx.HORIZONTAL)
        self.runPauseSizer.Add(self.runManyBtn, 0, wx.RIGHT|wx.CENTER, 7)
        self.runPauseSizer.Add(self.pauseBtn, 0, wx.RIGHT|wx.CENTER, 7)

        # Buttons to reset the counters and to clear all cells.
        self.resetStepBtn = wx.Button(self.ctrlPanel, wx.ID_ANY, 'Reset Steps')
        self.Bind(wx.EVT_BUTTON, self.onResetSteps, self.resetStepBtn)
        self.clearMapBtn = wx.Button(self.ctrlPanel, wx.ID_ANY, 'Clear Map')
        self.Bind(wx.EVT_BUTTON, self.onClearMap, self.clearMapBtn)
        self.resetClearSizer       = wx.BoxSizer(wx.HORIZONTAL)
        self.resetClearSizer.Add(self.resetStepBtn, 1, wx.RIGHT|wx.CENTER, 7)
        self.resetClearSizer.Add(self.clearMapBtn, 1, wx.RIGHT|wx.CENTER, 7)
        
        # Buttons to slide the window.
        self.slideUpBtn = wx.Button(self.ctrlPanel, wx.ID_ANY, 'Up')
        self.Bind(wx.EVT_BUTTON, self.onSlideUp, self.slideUpBtn)

        self.slideLeftBtn = wx.Button(self.ctrlPanel, wx.ID_ANY, 'Left')
        self.Bind(wx.EVT_BUTTON, self.onSlideLeft, self.slideLeftBtn)

        self.slideRightBtn = wx.Button(self.ctrlPanel, wx.ID_ANY, 'Right')
        self.Bind(wx.EVT_BUTTON, self.onSlideRight, self.slideRightBtn)

        self.slideDownBtn = wx.Button(self.ctrlPanel, wx.ID_ANY, 'Down')
        self.Bind(wx.EVT_BUTTON, self.onSlideDown, self.slideDownBtn)
        self.slideLRSizer       = wx.BoxSizer(wx.HORIZONTAL)
        self.slideLRSizer.Add(self.slideLeftBtn,   0, wx.ALIGN_LEFT|wx.LEFT|wx.RIGHT|wx.EXPAND, 3)
        self.slideLRSizer.Add(self.slideRightBtn,  0, wx.ALIGN_RIGHT|wx.LEFT|wx.RIGHT|wx.EXPAND, 3)

        # Now layout all of the controls and sizers.
        self.ctrlSizer.Add(self.oneStepSizer,   0,       wx.ALL|wx.CENTER, 5)
        self.ctrlSizer.Add(wx.StaticLine(self.ctrlPanel), 0, wx.ALL|wx.EXPAND, 5)
        self.ctrlSizer.Add(self.manyStepSizer,  0,     wx.ALL|wx.LEFT, 0)
        self.ctrlSizer.Add(self.stepRateSizer, 0,      wx.LEFT|wx.ALL, 0)
        self.ctrlSizer.Add(self.runStillBox, 0,     wx.LEFT|wx.ALL, 0)
        self.ctrlSizer.Add(self.runOscillatorsBox, 0,  wx.LEFT|wx.ALL, 0)
        self.ctrlSizer.Add(self.showCorpsesBox, 0,     wx.LEFT|wx.ALL, 0)
        self.ctrlSizer.Add(self.showStepsBox, 0,     wx.LEFT|wx.ALL, 0)
        self.ctrlSizer.Add(self.runPauseSizer,   0,     wx.ALL|wx.CENTER, 5)
        self.ctrlSizer.Add(wx.StaticLine(self.ctrlPanel), 0, wx.ALL|wx.EXPAND, 5)
        self.ctrlSizer.Add(self.resetClearSizer,  0, wx.ALL|wx.CENTER, 5)
        self.ctrlSizer.Add(wx.StaticLine(self.ctrlPanel), 0, wx.ALL|wx.EXPAND, 5)
        self.ctrlSizer.Add(self.slideUpBtn,  0, wx.ALL|wx.CENTER, 5)
        self.ctrlSizer.Add(self.slideLRSizer,  0, wx.ALL|wx.CENTER, 1)
        self.ctrlSizer.Add(self.slideDownBtn,  0, wx.ALL|wx.CENTER, 5)

        # Top level sizer.
        self.SetSizer(self.mainSizer)
        self.mainSizer.Fit(self)

        pub.subscribe(self.recvRunDone,  "rundone") # Worker sends this at end of a run.
        pub.subscribe(self.recvStepDone, "stepdone") # Worker sends this after each step.


# Event Handlers
    def onExit(self, event):
        self.exitPyLife()

    def exitPyLife(self):
        self.Close()

    def onSlideUp(self, event):
        self.uMap.slideUp(1)
        self.reportOffset()

    def onSlideLeft(self, event):
        self.uMap.slideLeft(1)
        self.reportOffset()

    def onSlideCenter(self, event):
        self.uMap.slideCenter()
        self.reportOffset()

    def onSlideRight(self, event):
        self.uMap.slideRight(1)
        self.reportOffset()

    def onSlideDown(self, event):
        self.uMap.slideDown(1)
        self.reportOffset()

    def onAbout(self, event):
        description="Conway's Game of Life simulates growth and death of cells."
        self.aboutInfo = wx.adv.AboutDialogInfo()
        self.aboutInfo.SetName('PyLife')
        self.aboutInfo.SetDescription(description)
        self.aboutInfo.AddDeveloper('Jeff Victor')
        wx.adv.AboutBox(self.aboutInfo)

    def onHelp(self, event):
        wx.MessageBox('PyLife is an implementation of Conway\'s Game of Life.\n\
        To get started, click anywhere in the large empty rectangle to create a "cell"\
 - or, if one is already there, to destroy it. After creating a few cells,\
 click the "1-Step" button to more forward one generation.\n\
        To  move forward several generations, use the "Run" button. Cells will appear\
 and disappear until you click "Pause."\n\
        The other controls allow you to:\n\
        - Specify a number of generations to run\n\
        - Stop a run if all cells have died, or if changes aren\'t happening,\
 or if the same pattern keeps repeating\n\
        - Limit the number of steps per second, if they are happening too quickly,\n\
        - Show the most-recently-deceased cells\n\
        - Improve performance considerably by not showing the result of each step.\n\
        "Reset Steps" clears the "steps" counter, and "Clear Map" removes all of the\
 "living" cells.')
 

    # Step forward one generation.
    def on1Step(self, event):
        self.reportMessage('')
        self.uMap.umapStep(self.showCorpsesBox.GetValue())  
        self.uMap.updateMap()  # Update visible map from data.
        self.reportStats(glob.numSteps, self.uMap.dMap.getNumAlive(), 0)

    # Handler of the Run button. It gathers inputs and spawns a worker thread
    # so that the UI, including the Pause button, can work during the run.
    def onRun(self, event):  

        self.runManyBtn.Disable()    # This will be enabled in recvRunDone
    
        stopSteps=0    # Number of generations to run in succession.
        if (self.runStopStepsBox.GetValue()):
            rawValue = self.inputStopSteps.GetValue()
            if len(rawValue)>0 and all(x in '0123456789' for x in rawValue):
                # convert to float and limit to 2 decimals
                stopSteps = int(float(rawValue))
                self.inputStopSteps.ChangeValue(str(stopSteps))
            else:
                # Tell UI that there was an error.
                self.reportMessage("Steps: Input Error")
                self.runManyBtn.Enable()
                return

        speedGoal=0    # User's preferred rate of generations.
        if self.stepRateBox.GetValue():      # Get the user-specified goal.
            rawValue = self.inputStepRate.GetValue()
            if len(rawValue)>0 and all(x in '0123456789' for x in rawValue):
                # convert to float and limit to 2 decimals
                speedGoal = int(float(rawValue))
                self.inputStepRate.ChangeValue(str(speedGoal))
            else:
                # Tell UI that there was an error.
                self.reportMessage("Steps/sec: Input Error")
                self.runManyBtn.Enable()
                return
        
        self.reportMessage("Running...") # Tell the world that we're running.

        # What features did the user request?
        stopStill       =self.runStillBox.GetValue()
        stopOscillators =self.runOscillatorsBox.GetValue()

        self.pauseBtn.Enable()
        thrRunMany = threading.Thread(target=self.uMap.uRunMany,\
                     args=(stopSteps, stopStill, stopOscillators,\
                           self.showCorpsesBox.GetValue(), speedGoal, False)) 
        thrRunMany.start()

    # After the run completes, the thread pub's a msg that causes recvRunDone to run.
    def recvRunDone(self, steps, alive, rate, result):        
        self.pauseBtn.Disable()
        self.reportMessage(format("The run %s."%result))
        self.reportStats(int(steps), int(alive), int(rate))
        self.uMap.updateMap()
        self.runManyBtn.Enable()
        
    # The run-worker thread sends one message per generation, running this.
    def recvStepDone(self, steps, alive, rate):
        # Update the visible map from the map data.
        if self.showStepsBox.GetValue():
            self.uMap.updateMap()

        # Receive data from worker thread and update the display
        if self.showStepsBox.GetValue() or int(steps)%10==0:
            self.reportStats(int(steps), int(alive), int(rate))
  
        # Now tell the thread that the UI has been updated, so that it can continue.
        glob.UIdone.set()

    def onResetSteps(self, event):
        glob.numSteps=0
        self.reportStats(glob.numSteps, self.uMap.dMap.getNumAlive(), 0)

    # Clear the visible map and the map data.
    def onClearMap(self, event):
        glob.numSteps=0
        self.uMap.clearMap()
        self.reportMessage('')
        self.reportStats(0, 0, 0)

    # Raise a flag indicating that the user wants the run to stop.
    def onPause(self, event):
        self.pauseBtn.Disable()        # Will be re-enabled by recvRunDone
        glob.stopWorker.set()          # Tell worker to stop.
        
    # Handle the menu choice to load a file into the maps.
    def onMenuLoad(self, event):
        with wx.FileDialog(self, "Open CSV file", wildcard="CSV files (*.csv)|*.csv",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     

            # Proceed loading the file chosen by the user
            pathname = fileDialog.GetPath()
            try:
                with open(pathname, 'r') as loadFile:
                    # Load data into the usermap in the upper-left corner of the "window"...
                    self.uMap.uLoadDataFromFile(loadFile, 0, 0)
                    # ...and then update the user's map.
                    self.uMap.updateMap()
                self.reportMessage("The file has been loaded.")
                self.reportStats(0, self.uMap.dMap.getNumAlive(), 0)
            except IOError:
                self.reportmessage(format("Cannot open file '%s'." % pathname))

    # Handle the menu choice that saves the current map into a file.
    def onMenuSave(self, event):
        with wx.FileDialog(self, "Save CSV file", wildcard="CSV files (*.csv)|*.csv",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL: return

            # save the current contents in the file
            pathname = fileDialog.GetPath()
            try:
                with open(pathname, 'w') as saveFile:
                    self.uMap.dMap.saveDataToFile(saveFile)
                self.reportMessage("The file has been saved.")
            except IOError:
                self.reportMessage(format("Cannot save current data in file '%s'." % pathname))

# Small UI functions
    def reportStats(self, steps, alive, rate):
        self.statusBar.SetStatusText(format("%d steps"%steps), 1)
        self.statusBar.SetStatusText(format("%d cells"%alive), 2)
        self.statusBar.SetStatusText(format("%d steps/second"%rate), 4)

    def reportOffset(self):
        self.statusBar.SetStatusText(format("%d,%d"%self.uMap.getOffset()), 5)

    def reportMessage(self, text):
        self.statusBar.SetStatusText(text, 0)

        

if __name__ == '__main__':
    app = wx.App()
    lFrame = lifeFrame()
    lFrame.Show()
    app.MainLoop()
