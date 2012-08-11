'''
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Written by Jesse Merritt
August 5 , 2012
www.github.com/jes1510

Reads analog values over a serial port and calcculates a voltage.
The values should be terminated with a newline.
eg:  512\n

The values are stored in a buffer of variable size that can be
saved in a file.

The program depends on the following modules:
serial:             Controls data over the virtual serial port
wx:                 Manages the GUI
wx.lib.newevent:    Event manager
configSerial:       Configures serial port and manages config file
'''

import sys
sys.path.append("/home/jesse/code/python/configSerial")
import serial
import wx
from threading import Thread
import time
import configSerial
import os
import wx.lib.newevent
import threading

running = False
keepReading = True      # Keep parallel threads running
dataList = []           # Data buffer

# Custom events for window
NewDataEvent, EVT_NEW_DATA = wx.lib.newevent.NewEvent()     # New custom even to signal ther's data in the buffer
errorEvent, EVT_ERROR = wx.lib.newevent.NewEvent()          # New custom even to signal ther's data in the buffer

class MainWindow(wx.Frame, Thread):             # Main window
    def __init__(self, parent, config, title="wxDMM") :        
        self.parent = parent                    # parent             
        self.config = config                    # Grab the configuration from the config class
        mainFrame = wx.Frame.__init__(self, self.parent, title=title, size=(350,150))        
        
        # setup the menubar
        filemenu= wx.Menu()                     
        setupmenu = wx.Menu()
        helpmenu = wx.Menu()
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File")        # Adding the "filemenu" to the MenuBar   
        menuBar.Append(setupmenu, "Setup")      # Setup menu
        menuBar.Append(helpmenu, "Help")        # Help menu
        self.SetMenuBar(menuBar)                # Adding the MenuBar to the Frame content.
        
        # Add content to the menuBar
        menuPorts = setupmenu.Append(wx.ID_ANY, "Serial Port", "Change settings")
        menuSave = filemenu.Append(wx.ID_SAVE, "Save", "Save the current data")     
        filemenu.AppendSeparator()
        menuExit = filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")     
        menuAbout = helpmenu.Append(wx.ID_ABOUT, "&About"," Information about this program")  
        
        # Build the main panel
        self.mainPanel = wx.Panel(self, -1, style=wx.SUNKEN_BORDER)
        
        #   Build sizers and statusbar
        self.topSizer = wx.BoxSizer(wx.HORIZONTAL)              # Top sizer holds label and box 
        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)           # Sizer to hold the buttonSizer
        self.rootSizer = wx.BoxSizer(wx.VERTICAL)               # Main sizer that holds everything
        self.statusBar = self.CreateStatusBar()                 # statusbar in the bottom of the window    
        
        font = wx.Font(32, wx.TELETYPE, wx.NORMAL, wx.NORMAL)   # Custom font for the meter
        
        self.voltageLabel = wx.StaticText(self.mainPanel, -1, "vDC:")   # Label for the foltage reading
        self.voltageBox = wx.TextCtrl(self.mainPanel)                   # Box to hold the readings
        
        # Set the fonts
        self.voltageLabel.SetFont(font)             
        self.voltageBox.SetFont(font)
        
        #   Buttons
        self.stopButton = wx.Button(self.mainPanel, -1, 'Stop')
        self.startButton = wx.Button(self.mainPanel, -1, 'Start')  
        
        #  Sizers.  Everything is on rootSizer   
        self.topSizer.Add(self.voltageLabel, 1, wx.EXPAND)
        self.topSizer.Add(self.voltageBox, 1, wx.EXPAND)
        self.buttonSizer.Add(self.startButton, 1, wx.EXPAND)
        self.buttonSizer.Add(self.stopButton, 1, wx.EXPAND)        
        self.rootSizer.Add(self.topSizer, 1, wx.EXPAND)
        self.rootSizer.Add(self.buttonSizer, 1, wx.EXPAND) 
          
        #  Bind Events
        self.Bind(wx.EVT_CLOSE, self.onExit)        
        self.Bind(wx.EVT_MENU, self.onAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.onExit, menuExit)
        self.Bind(wx.EVT_MENU, self.setupPort, menuPorts)        
        self.Bind(wx.EVT_MENU, self.onSave, menuSave)        
        self.Bind(wx.EVT_BUTTON, self.onStart, self.startButton)
        self.Bind(wx.EVT_BUTTON, self.onStop, self.stopButton)
        self.Bind(EVT_NEW_DATA, self.onNewData)             # custom event for new data    
        self.Bind(EVT_ERROR, self.findError)                # Custom event for errors             

        #  set the sizers
        self.SetSizer(self.rootSizer)
        self.SetAutoLayout(1)
        #self.rootSizer.Fit(self)     
        
        #  set preset value
        self.voltageBox.SetValue('0.00') 
        
        self.Layout()
        self.Show(True)     
    
        try :
            port.ser = serial.Serial(port.name, port.baud, timeout=port.timeout)    # Test the port
            time.sleep(1)               # Give the controller a second to come up
            port.ser.flushInput()       # Dump anything in the buffer
            
        except :
            self.showComError("Unable to open serial port!")        # Throw up a window
           
        
        self.statusBar.SetStatusText('Port: ' + port.name+ '\tStopped!')
        
    def findError(self, e) :
        '''
        Error handler for outside events
        
        Keyword Arguments:
        e:  Event
        '''
        err = e.attr1
        if err == "COM Error" : self.showComError(e.attr2)
        else :  self.showGeneralError(e.attr2)
        
    def onExit(self, e) :
        '''
        Exit event handler
        
        Keyword Arguments:
        e:  Event
        '''
        global keepReading
        try :
            port.ser.close()    # Needs to be in a try in case it wasn't opened
            
        except :
            pass
        
        keepReading = False     # Kill parallel threads
        self.Destroy()          # wipe out window and dump to the OS
      
    def onNewData(self, e) :
        '''
        New data event handler
        
        Keyword Arguments:
        e:  Event
        '''
        global dataList         # Data buffer
        global keepReading
        if keepReading :
            self.voltageBox.SetValue(dataList[len(dataList)-1].strip()) # Set the voltage box to the last element
                                            # in the buffer with trailing characters stripped off
                        
            bufferPercent = round((((len(dataList) * 1.0) / self.config.maxLength) * 100), 2)   # Calculate percentage
                                                        # from the length of the buffer
                                                        # rounded to 2 places
            self.statusBar.SetStatusText('Port: ' + port.name + '\tRunning... ' \
                              '\tBuffer: ' + str(bufferPercent) + '%')  

      
    def setupPort(self, e) :   
        '''
        Serial port setup event handler
        
        Keyword Arguments:
        e:  Event
        '''
        dia = configSerial.configSerial(self, -1, port)     # Use the serial port config module to configure
        dia.ShowModal()
        
      
    def onSave(self, e) :
        '''
        Save menu event handler
        
        Keyword Arguments
        e:  Event
        '''
        global dataList         # Buffer for the data
        dlg = wx.FileDialog(self, "Select file", '.', "", "*.*", \
                    wx.SAVE | wx.OVERWRITE_PROMPT)
                    
        if dlg.ShowModal() == wx.ID_OK:   
            self.filename = dlg.GetFilename()       # set the filename to the selected file
            self.dirname = dlg.GetDirectory()       # get the directory of the file
            of = open(os.path.join(self.dirname, self.filename),'w')    # open the file in write mode  
            for i in dataList :                     # Loop through the data and write it to the file   
                of.write(i)          
            of.close()
        dlg.Destroy()
        
    def onAbout(self, e) :
        '''
        About menu event handler
        
        Keyword Arguments
        e:  Event
        '''
        dlg = wx.MessageDialog(self, "A DMM that reads data over a serial port\n" \
                                       "by Jesse Merritt\n"\
                                       "www.github.com/jes1510", 'About', wx.OK | wx.ICON_INFORMATION)  
        dlg.ShowModal()
      
    
    def onStart(self, e) :
        '''
        Start Button event handler
        
        Keyword Argument:s
        e:  Event
        '''
        global keepReading
        global dataList
        global running
        dataList = []                       # Clear the data buffer on a fresh start
        keepReading = True                  # Set the flag for parallel threads       
       
        if not running :
            r = readData(self, self.config)      # spawn the data thread
            print self.config.vMax
            r.start()                       # Start the thread running
            running = True
        
    def onStop(self, e) :
        '''
        Stop Button event handler
        
        Keyword Arguments:
        e:  Event
        ''' 
        global keepReading
        global running        

        keepReading = False                 # Kill parallel thread
        running = False
        
        self.statusBar.SetStatusText('Port: ' + port.name + '\tStopped!')   # update the status bar   
      
    
    def showComError(self, msg) :           
        '''
        Show a COM Error
        
        Keyword Arguments:
        msg:  The message dialog to be shown
        '''
        dlg = wx.MessageDialog(self, msg , 'COM Error!',  wx.OK | wx.ICON_ERROR)  
        dlg.ShowModal() 

    def showGeneralError(self, msg) :
        '''
        Show a general Error
        
        Keyword Arguments:
        msg:  The message dialog to be shown
        '''
        dlg = wx.MessageDialog(self, msg, 'Error!', wx.OK | wx.ICON_ERROR)      
        dlg.ShowModal()


class readData(Thread) :
    '''
    Class to handle serial port operations in a thread
    
    Keyword Arguments:
    parent:  Parent class of calling window
    confg:  Configuration class
    '''
    def __init__(self, parent, config):
        Thread.__init__(self)       #  Initialize as a thread
        self.setDaemon(True)        #  If you don't do this then the thread can get abandoned
        self.parent = parent        
        self.newDataEvent = NewDataEvent()   #  Simple name for new data event       
        self.config = config        #  name the configuration
        
    def run(self) :    
        '''
        Called to start thread
        '''
        window = self.parent           
        global dataList             # data buffer
        global keepReading          # processing flag       
        mS = 1.0 / float(self.config.minFramerate)  #  Calculate milliseconds from frame rate 
        lastPost = time.time()      # grab the time
        s = port.ser                # rename the serial port to save key strokes ;)
        
        try :            
            s.flushInput()          # Dump anything left in the port            
            while keepReading:      # MAIN LOOP!  Keep running while the flag is set                
                i = port.ser.readline()      # read a line of data from the port
          
                if i :                # If there is data...
                    try :             # Just ignore stray characters, not graceful but it's simple                        
                        constant = self.config.vMax  / (pow(2, self.config.ADCBits) - 1)  
                        volts = int(i.strip()) * constant     # Calculate volts from the constant                        
                    except :
                        continue
                    
                    dataList.append(str(round(volts, 2))+'\n')   # Put the voltage in the data buffer                 
                    
                    if len(dataList) > self.config.maxLength :          # reaper to maintain max length of the buffer
                        dataList.pop(0)
                    
                    if (time.time() - lastPost) > mS :                  # If the timer expires then flag the window to update the box
                        wx.PostEvent(self.parent, self.newDataEvent)    # post an event to the window
                        lastPost = time.time()                          # reset the timer
                
                else :
                    wx.PostEvent(self.parent, errorEvent(attr1="COM Error", attr2="Serial port timeout!"))  # Nothing was read
                
        except Exception, detail:       
            wx.PostEvent(self.parent, errorEvent(attr1="General Error", attr2="Error with serial thread!")) # no specific error
             

        
        
class configuration() :
    '''
    Configuration class encapsulates configuration data and 
    manages config file
    '''  
    def __init__(self) :  
        self.configFilename = 'wxDmm.config'
        self.configFile = wx.Config(self.configFilename)    # Open config file.  Default location is home 
        self.maxLength = 65535                              # Max number of readings in buffer   
        self.vMax = 5.0                                     # Maximum voltage on the A/D
        self.ADCBits = 10                                   # resolution of A/D in bits
        self.minFramerate = 30                              # Minimum framerate to maintain on meter        
      
        if self.configFile.Exists('maxLength'):       # If the config file exists then load configuration
            self.maxLength = self.configFile.ReadInt('maxLength')

            self.minFramerate = self.configFile.ReadFloat('minFramerate')
            self.vMax = self.configFile.ReadFloat('vMax')
            self.ADCBits = self.configFile.ReadInt('ADCBits')
      
        else:
            self.saveOptions()                # create a default file if one doesn't exist
        
      
    
    def saveOptions(self) :
        '''
        Writes the configuration to the config file
        '''
        self.configFile.WriteInt('maxLength', self.maxLength)
        self.configFile.WriteFloat('vMax', self.vMax)
        self.configFile.WriteInt('ADCBits', self.ADCBits)
        self.configFile.WriteFloat('minFramerate', self.minFramerate)    
          

if __name__ == '__main__':    
    config = configuration()
    port = configSerial.Port(config.configFilename)

    app = wx.App(False)                 # wx instance
    frame = MainWindow(None, config)        # main window frame

    app.MainLoop()
