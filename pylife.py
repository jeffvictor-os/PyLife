'''
Created on Feb 1, 2018

@author: jeff victor
'''

import wx
import wx.grid
import csv


NUMROWS=40
NUMCOLS=40

AC='*'   # Alive Cell
EC=''    # "Empty Cell"


numSteps=0
numAlive=0

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

        # The controls are created after the Life (right) Panel.
        
        # Life Panel: wx.grid
        self.lifeSizer        = wx.BoxSizer(wx.VERTICAL)
        self.lifePanel.SetSizer(self.lifeSizer)
        self.ltitle = wx.StaticText(self.lifePanel, wx.ID_ANY, 'Life Grid')
        self.ltitleSizer       = wx.BoxSizer(wx.HORIZONTAL)
        self.ltitleSizer.Add(self.ltitle, 0, wx.ALL, 5)
        self.lifeSizer.Add(self.ltitleSizer, 0, wx.CENTER)

        self.lGrid=lifeGrid(self.lifePanel)
        self.lifeSizer.Add(self.lGrid, 0, wx.LEFT, 5)

        # Controls for the Control Panel
        self.oneStepBtn = wx.Button(self.ctrlPanel, wx.ID_ANY, '1-Step')
        self.Bind(wx.EVT_BUTTON, self.on1Step, self.oneStepBtn)
        self.oneStepSizer       = wx.BoxSizer(wx.HORIZONTAL)
        self.oneStepSizer.Add(self.oneStepBtn, 0, wx.ALL, 0)
        self.ctrlSizer.Add(self.oneStepSizer, 0,       wx.ALL|wx.CENTER, 5)
 
 
        # Top level sizer.
        self.SetSizer(self.mainSizer)
        self.mainSizer.Fit(self)


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

    def on1Step(self, event):
        global numSteps
        global numAlive
        lifeStep(lFrame.lGrid.curMatrix)  # Defined outside of this class.
        for row in range(NUMROWS):
            for col in range(NUMCOLS):
                self.lGrid.SetCellValue(row, col, lFrame.lGrid.curMatrix[row][col])
        self.reportStats(numSteps, numAlive, 0)


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

def lifeStep(curMatrix):
    global numAlive
    global numSteps
    numSteps +=1

    nextMat=[['' for x in range(NUMROWS)] for y in range(NUMCOLS)]

    # Build a new map of cells first...
    for row in range(0,NUMROWS):
        for col in range(0,NUMCOLS):
            naybors=sumNaybors(curMatrix, row, col)
            currentCell= curMatrix[row][col]
            if currentCell == AC:              # Was alive
                if naybors<2 or naybors>3:
                    nextMat[row][col]=EC         # Died.
                    numAlive -= 1
                else:
                    nextMat[row][col]=AC         # Still alive
            else:                              # Was dead
                if naybors==3:
                    nextMat[row][col]=AC           # New cell
                    numAlive   += 1
                else:
                    nextMat[row][col]=EC           # Still dead

    # ...then copy the new map into the wx grid so someone else can refresh the UI.
    for row in range(NUMROWS):
        for col in range(NUMCOLS):
            curMatrix[row][col]=nextMat[row][col]

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
