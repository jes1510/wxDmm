'''
Written by Jesse Merritt
October 1, 2011

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

Reads simple ADC readings from an Arduino over a serial port

Here is an awesome wx tutorial I cam acoss while writing this:
http://wiki.wxpython.org/AnotherTutorial

The GUI requires WX.

The program depends on the following modules:
serial:	Controls data over the virtual serial port
wx:  	Manages the GUI
wx.lib.newevent:  Event manager

Change Log:

'''
import serial
import wx
import sys
from threading import Thread
import time

keepAlive = True
keepReading = True

class MainWindow(wx.Frame):
    def __init__(self, parent, title="Simple DMM") :
        self.parent = parent
        #global ser
        #global configFile
        self.read = ''
        mainFrame = wx.Frame.__init__(self,self.parent, title=title, size=(2048,600))   
        
        filemenu= wx.Menu()
        setupmenu = wx.Menu()
        helpmenu = wx.Menu()

        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File")                    # Adding the "filemenu" to the MenuBar   
        menuBar.Append(setupmenu, "Setup")
        menuBar.Append(helpmenu, "Help")
        self.SetMenuBar(menuBar)                            # Adding the MenuBar to the Frame content.
        
        menuPorts = setupmenu.Append(wx.ID_ANY, "Settings", "Change settings");
        #menuReset = setupmenu.Append(wx.ID_ANY, "Reset Controller", "Hard Reset the controller");      
        menuOpen = filemenu.Append(wx.ID_OPEN, "&Open"," Open a file to edit")        
        menuSave = filemenu.Append(wx.ID_SAVE, "Save", "Save the current data")     
        filemenu.AppendSeparator()
        menuExit = filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")     
        menuAbout = helpmenu.Append(wx.ID_ABOUT, "&About"," Information about this program")  
        
        self.mainPanel = wx.Panel(self, -1, style=wx.SUNKEN_BORDER)   
        
        #   Build sizers and statusbar
        self.topSizer = wx.BoxSizer(wx.HORIZONTAL) 
        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)        
        self.rootSizer = wx.BoxSizer(wx.VERTICAL)                        
        self.statusBar = self.CreateStatusBar()                              # statusbar in the bottom of the window    
        
        self.voltageLabel = wx.StaticText(self.mainPanel, 1, "Voltage:")        
        self.voltageBox = wx.TextCtrl(self.mainPanel)    
        
        #   Buttons
        self.stopButton = wx.Button(self.mainPanel, -1, 'Stop',size=(50,50))
        self.startButton = wx.Button(self.mainPanel, -1, 'Start',size=(50,50))
                
        #self.codeViewer = wx.TextCtrl(self.jogPanel, -1, '', style=wx.TE_MULTILINE|wx.VSCROLL)
        
        #  Sizers.  Everything is on rootSizer   
        self.topSizer.Add(self.voltageLabel, 1, wx.EXPAND)
        self.topSizer.Add(self.voltageBox, 1, wx.EXPAND)
        self.buttonSizer.Add(self.startButton, 1, wx.EXPAND)
        self.buttonSizer.Add(self.stopButton, 1, wx.EXPAND)
        
        self.rootSizer.Add(self.topSizer, 1, wx.EXPAND)
        self.rootSizer.Add(self.buttonSizer, 1, wx.EXPAND) 
          
        #___________Bind Events_______________________________
        self.Bind(wx.EVT_CLOSE, self.onExit)        
    #       self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.onExit, menuExit)
        self.Bind(wx.EVT_MENU, self.onOpen, menuOpen)
        self.Bind(wx.EVT_MENU, self.setupPort, menuPorts)
        #self.Bind(wx.EVT_MENU, self.resetController, menuReset)
        self.Bind(wx.EVT_MENU, self.onSave, menuSave)
        
        self.Bind(wx.EVT_BUTTON, self.onStart, self.startButton)
        self.Bind(wx.EVT_BUTTON, self.onStop, self.stopButton)
        
        #self.Bind(wx.EVT_CHAR_HOOK, self.OnKeyDown)            

        # set the sizers
        self.SetSizer(self.rootSizer)
        self.SetAutoLayout(1)
        self.rootSizer.Fit(self)     
        
        #	Set preset values
        self.voltageBox.SetValue('0.000')        
        
        self.Layout()
        self.Show(True)		
	
        try :
            port.ser = serial.Serial(port.name, port.baud, timeout=port.timeout)
            time.sleep(2)			# Give Grbl time to come up and respond
            port.ser.flushInput()		# Dump all the initial Grbl stuff
            
        except :
            self.showComError() #vents to buttons
            #pass

    def onExit(self, e) :
        global keepAlive
        try :
            port.ser.close()  	# Needs to be in a try in case it wasn't opened
        except :
            pass
        keepAlive = False
        self.Destroy()              # wipe out window and dump to the OS

    def onOpen(self, e):
        pass

    def setupPort(self, e):
        pass
    def onSave(self, e) :
        pass
    
    def onStart(self, e) :
        global keepReading
        keepReading = True
        r = readData(self)
        r.start()
        
    def onStop(self, e) :
        global keepReading
        keepReading = False
        print "stopped"

    def showComError(self) :     #	Can't open COM port
        dlg = wx.MessageDialog(self, "Could not open COM port!\nCheck the config file", 'Error!', wx.OK | wx.ICON_ERROR)  
        dlg.ShowModal()
        #self.setupPort(None)

    def showBufferFull(self) :
        dlg = wx.MessageDialog(self, "Could not open COM port!", 'Error!', wx.OK | wx.ICON_ERROR)
        dlg.showModal()


class readData(Thread) :
    def __init__(self, parent):
        Thread.__init__(self)
        self.setDaemon(True)    #  If you don't do this then the thread can get abandoned
        self.parent = parent
        
    def run(self) :
        i = 1.000
        window = self.parent
        global keepAlive
        while keepAlive and keepReading:
            print "Running!"
            i = i + .001            
            window.voltageBox.SetValue(str(i))
            time.sleep(0.5)
                         
        


class Port() :		# Dummy class to encapsulate the port and config attributes;  Cleaner than global  
    def __init__(self) : 
        self.name = '/dev/ttyACM0'		# Serial port name
        self.baud = 0			        # Baud rate
        self.dataBits = 8			# data bits 
        self.parity = 'n'			# Whether or not to use parity
        self.stopBits = 1			# Number of stop bits
        self.timeout = 1			# Serial port timeout in seconds
        self.rtscts = 0			        # Hardware flow control.  0=off, 1=on
        self.allowKeyboard = True    	        # Allow keyboard shortcuts
        self.configFile = wx.Config('dmmconfig')	# Configfile name.  Default location is home
        self.ser =  serial.Serial()     	# Serial port instance
        self.keyRepeat = 200			# mS delay to use when sending keycord commands.
        self.port  = serial.Serial()
	
        if self.configFile.Exists('port'):	
            self.name = self.configFile.Read('port')
            self.baud = self.configFile.ReadInt('baud') 
            self.timeout = self.configFile.ReadInt('timeout')
            self.allowKeyboard = self.configFile.Read('allowKeyboard')
            self.keyRepeat = self.configFile.ReadInt('keyRepeat')
            self.bufferSize = self.configFile.ReadInt('sizeofbuffer')
	  #self.keyboardDistance = port.configFile.Read('keyboardDistance'

        else :
            print "Error:  Config file not found"
            #sys.exit(1)

port = Port()

app = wx.App(False)         # wx instance
frame = MainWindow(None)    # main window frame

app.MainLoop()
