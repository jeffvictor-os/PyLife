'''
Created on Feb 1, 2018

@author: jeff victor
'''

import wx
import wx.grid
import csv
import time
import timeit
import threading
from wx.lib.pubsub import Publisher

NUMROWS=40
NUMCOLS=40

AC='*'   # Alive Cell
EC=''    # "Empty Cell"
DC='-'   # Dead Cell


numSteps=0
numAlive=0
speedMeasured=0

stopWorker=threading.Event()     # True:=User pressed Stop button.
workerRunning=threading.Event()  # True:=Worker thread is running.
UIdone=threading.Event()         # After a step, Worker waits until this is set.

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
        loadMenuItem = fileMenu.Append(wx.NewId(), "Load...", "Load a file")
        self.Bind(wx.EVT_MENU, self.onMenuLoad, loadMenuItem)
        saveMenuItem = fileMenu.Append(wx.NewId(), "Save...", "Save a file")
        self.Bind(wx.EVT_MENU, self.onMenuSave, saveMenuItem)

 
        exitMenuItem = fileMenu.Append(wx.NewId(), "Exit", "Exit Life")
        self.Bind(wx.EVT_MENU, self.onExit, exitMenuItem)

        helpMenu = wx.Menu()
        aboutMenuItem = helpMenu.Append(wx.NewId(), "About...", "About Life")
        menuBar.Append(helpMenu, "&Help")
        self.Bind(wx.EVT_MENU, self.onAbout, aboutMenuItem)

        self.SetMenuBar(menuBar)

        # Status Bar
        self.statusBar=self.CreateStatusBar(5)
        self.statusBar.SetStatusWidths([200,100,75,75,150])
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
        self.ltitle = wx.StaticText(self.lifePanel, wx.ID_ANY, 'Life Grid - Click to Create Life')
        self.ltitleSizer       = wx.BoxSizer(wx.HORIZONTAL)
        self.ltitleSizer.Add(self.ltitle, 0, wx.ALL, 5)
        self.lifeSizer.Add(self.ltitleSizer, 0, wx.CENTER)

        self.lGrid=lifeGrid(self.lifePanel)
        self.lifeSizer.Add(self.lGrid, 0, wx.LEFT, 5)

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
        self.runStillBox = wx.CheckBox(self.ctrlPanel, wx.ID_ANY, label='Stop when still lifes')
        self.runStillBox.SetValue(True)

        # Stop a run when the map is static plus blinkers.
        self.runOscillatorsBox = wx.CheckBox(self.ctrlPanel, wx.ID_ANY, label='Stop when just oscillators')
        self.runOscillatorsBox.SetValue(True)
        
        # Show the most recently deceased cells?         
        self.showCorpsesBox = wx.CheckBox(self.ctrlPanel, wx.ID_ANY, 'Show corpses')
        
        # Show map after each step in a run.
        self.showStepsBox = wx.CheckBox(self.ctrlPanel, wx.ID_ANY, 'Show each step')
        self.showStepsBox.SetValue(True)

        # Buttons to run and stop.
        self.runManyBtn    = wx.Button(self.ctrlPanel, wx.ID_ANY, 'Run', style=wx.EXPAND)
        self.Bind(wx.EVT_BUTTON, self.onRun, self.runManyBtn)
        self.stopBtn = wx.Button(self.ctrlPanel, wx.ID_ANY, 'Stop')
        self.Bind(wx.EVT_BUTTON, self.onStop, self.stopBtn)
        self.stopBtn.Disable()
        self.runStopSizer       = wx.BoxSizer(wx.HORIZONTAL)
        self.runStopSizer.Add(self.runManyBtn, 0, wx.RIGHT|wx.CENTER, 5)
        self.runStopSizer.Add(self.stopBtn, 0, wx.RIGHT|wx.CENTER, 5)

        # Buttons to reset the counters and to clear all cells.
        self.resetStepBtn = wx.Button(self.ctrlPanel, wx.ID_ANY, 'Reset Steps')
        self.Bind(wx.EVT_BUTTON, self.onResetSteps, self.resetStepBtn)
        self.clearGridBtn = wx.Button(self.ctrlPanel, wx.ID_ANY, 'Clear Grid')
        self.Bind(wx.EVT_BUTTON, self.onClearGrid, self.clearGridBtn)
        self.resetClearSizer       = wx.BoxSizer(wx.HORIZONTAL)
        self.resetClearSizer.Add(self.resetStepBtn, 0, wx.ALL, 5)
        self.resetClearSizer.Add(self.clearGridBtn, 0, wx.ALL, 5)
        
        # Now layout all of the controls and sizers.
        self.ctrlSizer.Add(self.oneStepSizer,   0,       wx.ALL|wx.CENTER, 5)
        self.ctrlSizer.Add(wx.StaticLine(self.ctrlPanel), 0, wx.ALL|wx.EXPAND, 5)
        self.ctrlSizer.Add(self.manyStepSizer,  0,     wx.ALL|wx.LEFT, 0)
        self.ctrlSizer.Add(self.stepRateSizer, 0,      wx.LEFT|wx.ALL, 0)
        self.ctrlSizer.Add(self.runStillBox, 0,     wx.LEFT|wx.ALL, 0)
        self.ctrlSizer.Add(self.runOscillatorsBox, 0,  wx.LEFT|wx.ALL, 0)
        self.ctrlSizer.Add(self.showCorpsesBox, 0,     wx.LEFT|wx.ALL, 0)
        self.ctrlSizer.Add(self.showStepsBox, 0,     wx.LEFT|wx.ALL, 0)
        self.ctrlSizer.Add(self.runStopSizer,   0,     wx.ALL|wx.CENTER, 5)
        self.ctrlSizer.Add(wx.StaticLine(self.ctrlPanel), 0, wx.ALL|wx.EXPAND, 5)
        self.ctrlSizer.Add(self.resetClearSizer,  0, wx.ALL|wx.CENTER, 5)

        # Top level sizer.
        self.SetSizer(self.mainSizer)
        self.mainSizer.Fit(self)

        Publisher().subscribe(self.recvRunDone,  "rundone") # Worker sends this at end of a run.
        Publisher().subscribe(self.recvStepDone, "stepdone") # Worker sends this after each step.


# Event Handlers
    def onExit(self, event):
        self.closeProgram()

    def closeProgram(self):
        self.Close()

    def onAbout(self, event):
        description="Conway's Game of Life simulates growth and death of cells."
        self.aboutInfo = wx.AboutDialogInfo()
        self.aboutInfo.SetName('PyLife')
        self.aboutInfo.SetDescription(description)
        self.aboutInfo.AddDeveloper('Jeff Victor')
        wx.AboutBox(self.aboutInfo)

    # Step forward one generation.
    def on1Step(self, event):
        global numSteps
        global numAlive
        lifeStep(lFrame.lGrid.curMatrix, self.showCorpsesBox.GetValue())  # Defined outside of this class.
        for row in range(NUMROWS):
            for col in range(NUMCOLS):
                self.lGrid.SetCellValue(row, col, lFrame.lGrid.curMatrix[row][col])
        self.reportStats(numSteps, numAlive, 0)

    # Handler of the Run button. It gathers inputs and spawns a worker thread
    # so that the UI, including the Stop button can work during the run.
    def onRun(self, event):  
        global numSteps
        self.runManyBtn.Disable()    # This will be enabled in recvRunDone
        self.reportMessage("Running...") # Tell the world that we're running.
        speedGoal=0    # Zero means no rate cap.

        stopSteps=0
        if (lFrame.runStopStepsBox.GetValue()):
            raw_value = lFrame.inputStopSteps.GetValue()
            if all(x in '0123456789.+-' for x in raw_value):
                # convert to float and limit to 2 decimals
                stopSteps = int(float(raw_value))
                lFrame.inputStopSteps.ChangeValue(str(stopSteps))
            else:
                # Tell UI that there was an error.
                self.reportMessage("Steps: Input Error")
                return

        if lFrame.stepRateBox.GetValue():      # Get the user-specified goal.
            raw_value = lFrame.inputStepRate.GetValue()
            if all(x in '0123456789.+-' for x in raw_value):
                # convert to float and limit to 2 decimals
                speedGoal = int(float(raw_value))
                lFrame.inputStepRate.ChangeValue(str(speedGoal))
            else:
                # Tell UI that there was an error.
                wx.CallAfter(Publisher().sendMessage, "errdone", "Input Error")
                return
        
        stopStill  =lFrame.runStillBox.GetValue()
        stopOscillators=lFrame.runOscillatorsBox.GetValue()
        showSteps=lFrame.showStepsBox.GetValue()

        self.stopBtn.Enable()
        thrRunMany = threading.Thread(target=self.runMany,args=(lFrame.lGrid.curMatrix, stopSteps, stopStill, stopOscillators, lFrame.showCorpsesBox.GetValue(), showSteps, speedGoal)) 
        thrRunMany.start()

    def recvRunDone(self, msg):        
        t = msg.data
        (steps, alive, rate, result) = t.split(',')
        
        self.stopBtn.Disable()
        self.reportMessage(format("The run %s."%result))
        self.reportStats(int(steps), int(alive), int(rate))
        for row in range(NUMROWS):
            for col in range(NUMCOLS):
                self.lGrid.SetCellValue(row, col, self.lGrid.curMatrix[row][col])        
        self.runManyBtn.Enable()
        
    # The run-worker thread sends one message per generation.
    def recvStepDone(self, msg):
        global UIdone

        # Uses the incoming message and the updated map to update the display.
        for row in range(NUMROWS):
            for col in range(NUMCOLS):
                self.lGrid.SetCellValue(row, col, lFrame.lGrid.curMatrix[row][col])
        # Receives data from thread and updates the display
        t = msg.data
        (steps, alive, rate) = t.split(',')
        self.reportStats(int(steps), int(alive), int(rate))
        UIdone.set()

        
    def onResetSteps(self, event):
        global numAlive, numSteps
        numSteps=0
        self.reportStats(numSteps, numAlive, 0)

    def onClearGrid(self, event):
        global numSteps, numAlive
        numSteps=numAlive=0
        for row in range(NUMROWS):
            for col in range(NUMCOLS):
                if self.lGrid.curMatrix[row][col] !=EC:  # Avoid unnecessary SetCellValue's.
                    self.lGrid.curMatrix[row][col]=EC
                    self.lGrid.SetCellValue(row, col, EC)
        self.reportMessage('')
        self.reportStats(0, 0, 0)

    def onStop(self, event):
        global workerRunning, stopWorker
        if workerRunning.isSet():         # Is worker even running?
            self.stopBtn.Disable()        # Will be re-enabled by recvRunDone
            stopWorker.set()              # Tell worker to stop.
        
    def onMenuLoad(self, event):
        with wx.FileDialog(self, "Open CSV file", wildcard="CSV files (*.csv)|*.csv",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # Proceed loading the file chosen by the user
            pathname = fileDialog.GetPath()
            try:
                with open(pathname, 'r') as loadFile:
                    self.loadDataFromFile(loadFile)
                self.reportMessage("The file has been loaded.")
                self.reportStats(0, numAlive, 0)
            except IOError:
                self.reportmessage(format("Cannot open file '%s'." % pathname))

    def loadDataFromFile(self, loadFile):
        global numAlive
        numAlive=0
        rownum=-1
        lreader = csv.reader(loadFile)
        for row in lreader:
            rownum +=1
            if rownum>=NUMROWS:   # Safely handle oversized files.
                break;
            for col in range(NUMCOLS):
                self.lGrid.curMatrix[rownum][col]='' # Default value...
                if col<len(row):                     # ..handles undersized lines.
                    if row[col] != '0':
                        if row[col]==AC:
                            numAlive+=1
                            self.lGrid.curMatrix[rownum][col]=row[col]
                self.lGrid.SetCellValue(rownum, col, self.lGrid.curMatrix[rownum][col])

    def onMenuSave(self, event):
        with wx.FileDialog(self, "Save CSV file", wildcard="CSV files (*.csv)|*.csv",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL: return

            # save the current contents in the file
            pathname = fileDialog.GetPath()
            try:
                with open(pathname, 'w') as saveFile:
                    self.saveDataToFile(saveFile)
                self.reportMessage("The file has been saved.")
            except IOError:
                self.reportMessage(format("Cannot save current data in file '%s'." % pathname))

    def saveDataToFile(self, saveFile):
        swriter = csv.writer(saveFile)
        # First create a list that represents the row.
        for rownum in range(NUMROWS):
            row=[]
            for colnum in range(NUMCOLS):
                row.append(self.lGrid.curMatrix[rownum][colnum])
                if row[-1]=='':
                    row[-1]='0'
            # Then write the list as CSV.
            swriter.writerow(row)

        
# Small utility functions
    def reportStats(self, steps, Alive, rate):
        self.statusBar.SetStatusText(format("%d steps"%steps), 1)
        self.statusBar.SetStatusText(format("%d %s"%(Alive, AC)), 2)
        self.statusBar.SetStatusText(format("%d steps/second"%rate), 4)

    def reportMessage(self, text):
        self.statusBar.SetStatusText(text, 0)

    def runMany(self, matrix, stopAfterSteps, stopWhenStill, stopWhenOscillators, showCorpses, showSteps, speedGoal):
        global numSteps, numAlive, speedMeasured
        global stopWorker, workerRunning, UIdone
        # Data Initializations
        keepGoing=True  # Set to False when certain conditions are met.
        newHash=0       # Used to detect static map, possible with blinkers.
        oldHash1=0      # Used to detect blinkers.
        oldHash2=0      # Used to detect blinkers.
        oldHash3=0      # Used to detect blinkers.
        oldHash4=0      # Used to detect blinkers.
        step=1          # To limit steps, and to time perf samples.
        stepSpeedMeasured=0
        result="completed"
        stopWorker.clear()
        workerRunning.set()

        # Start timer to report step rate.
        startTime=1.0*timeit.default_timer()

        if speedGoal > 0:
            delay = 1.0/speedGoal      # This is a first guess.
            print "Goal= %d, Delay=%0.4f" % (speedGoal, delay)

        # Report rate every 10 steps, and optionally adjust step rate every 10 steps.
        stepStartTime=1.0*timeit.default_timer()

        # Main loop
        while keepGoing:
            newHash=lifeStep(matrix, showCorpses)  # Actually "live" for a step. :-)

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
                UIdone.clear()
                msg=format("%d,%d,%d" % (numSteps, numAlive, stepSpeedMeasured))
                wx.CallAfter(Publisher().sendMessage, "stepdone", msg) # Tell GUI to refresh.
                UIdone.wait()  # Wait for recvStepDone to signal completion of refresh.

            # Detect requested termination conditions, express same.
            if stopWorker.isSet():
                result="was interrupted"
                keepGoing=False

            step += 1
            if stopWhenStill and newHash==oldHash1:
                keepGoing=False
            elif stopWhenOscillators and (newHash==oldHash2 or newHash==oldHash3 or newHash==oldHash4):
                keepGoing=False
            else:
                oldHash4=oldHash3
                oldHash3=oldHash2
                oldHash2=oldHash1
                oldHash1=newHash
            if (stopAfterSteps>0 and step>stopAfterSteps):
                keepGoing=False  
            if numAlive<1:
                result="ended with no cells"
                keepGoing=False  
            if speedGoal>0 and keepGoing==True:
                time.sleep(delay)

        endTime=1.0*timeit.default_timer()
        elapsed=endTime-startTime
        speedMeasured=step/elapsed

        msg=format("%d,%d,%d,%s" % (numSteps, numAlive, speedMeasured, result))
        wx.CallAfter(Publisher().sendMessage, "rundone", msg) # Tell GUI all steps are done.
        stopWorker.clear()
        

class lifeGrid(wx.grid.Grid):
    def __init__(self, *args, **kw):
        wx.grid.Grid.__init__(self, *args, **kw)
        self.CreateGrid(NUMROWS, NUMCOLS)

        self.EnableGridLines(False) # Hide grid lines.
        self.SetColLabelSize(0)     # Hide column labels.
        self.SetDefaultCellAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
        self.SetRowLabelSize(0)     # Hide row labels.
        self.SetDefaultColSize(3, resizeExistingCols=True)
        self.SetDefaultRowSize(5, resizeExistingRows=False)
        for r in range(NUMROWS):    # Prevent user from entering data.
            for c in range(NUMCOLS):
                self.SetReadOnly(r, c, True)
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.onCellLeftClick)

        # Create the matrix that contains "truth" for the cells.
        self.curMatrix=[['' for x in range(NUMROWS)] for y in range(NUMCOLS)]
    
    def onCellLeftClick(self, evt):
        global numAlive, numSteps
        if self.curMatrix[evt.GetRow()][evt.GetCol()] == EC:
            self.curMatrix[evt.GetRow()][evt.GetCol()] = AC
            numAlive   += 1
        elif self.curMatrix[evt.GetRow()][evt.GetCol()] == AC:
            self.curMatrix[evt.GetRow()][evt.GetCol()] = EC
            numAlive   -= 1
        else: #self.curMatrix[evt.GetRow()][evt.GetCol()] == DC:
            self.curMatrix[evt.GetRow()][evt.GetCol()] =  EC
        self.SetCellValue(evt.GetRow(), evt.GetCol(), self.curMatrix[evt.GetRow()][evt.GetCol()])

        lFrame.reportStats(numSteps, numAlive, 0)

        evt.Skip()

def lifeStep(curMatrix, showCorpses):
    global numAlive
    global numSteps
    numSteps +=1
    lifeHash=0    # Used to detect map that's static, possible with blinkers.

    nextMat=[['' for x in range(NUMROWS)] for y in range(NUMCOLS)]

    if showCorpses: corpse=DC  # Leave a mark for a cell that died recently.
    else:           corpse=EC

    # Build a new map of cells first...
    for row in range(0,NUMROWS):
        for col in range(0,NUMCOLS):
            naybors=sumNaybors(curMatrix, row, col)
            currentCell= curMatrix[row][col]
            if currentCell == AC:                # Was alive
                if naybors<2 or naybors>3:
                    nextMat[row][col]=corpse     # Died.
                    numAlive -= 1
                else:
                    nextMat[row][col]=AC         # Still alive
            else:                                # Was dead
                if naybors==3:
                    nextMat[row][col]=AC         # New cell
                    numAlive   += 1
                else:
                    nextMat[row][col]=EC         # Still dead

    # ...then copy the new map into the wx grid so someone else can refresh the UI.
    for row in range(NUMROWS):
        for col in range(NUMCOLS):
            curMatrix[row][col]=nextMat[row][col]
            if curMatrix[row][col]==AC:
                lifeHash += row**2+col
                
    return lifeHash

def sumNaybors(matrix, row, col):   # Count the number of neighbors of this cell.
    last=NUMROWS-1
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
                if AC==matrix[checkrow][checkcol]:
                    naybors += 1

    return (naybors)


if __name__ == '__main__':
    app = wx.PySimpleApp()
    lFrame = lifeFrame()
    lFrame.Show()
    app.MainLoop()
