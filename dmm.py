'''
Written by Jesse Merritt
August 5 , 2012

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

Reads simple ADC readings over a serial port

Here is an awesome wx tutorial I cam acoss while writing this:
http://wiki.wxpython.org/AnotherTutorial

The program depends on the following modules:
serial:			Controls data over the virtual serial port
wx:  			Manages the GUI
wx.lib.newevent:  	Event manager
configSerial: 		Configures serial port and manages config file

'''

import sys
sys.path.append("~/code/python/configSerial")
import serial
import wx
from threading import Thread
import time
import configSerial
import os
import wx.lib.newevent
import threading

keepAlive = True
keepReading = True
data = 0
dataList = []
maxLength = 1024

NewDataEvent, EVT_NEW_DATA = wx.lib.newevent.NewEvent()

class MainWindow(wx.Frame, Thread):
    def __init__(self, parent, title="Simple DMM") :
        self.parent = parent
        self.read = ''
        mainFrame = wx.Frame.__init__(self, self.parent, title=title, size=(2048,600))
        
        filemenu= wx.Menu()
        setupmenu = wx.Menu()
        helpmenu = wx.Menu()

        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File")                    # Adding the "filemenu" to the MenuBar   
        menuBar.Append(setupmenu, "Setup")
        menuBar.Append(helpmenu, "Help")
        self.SetMenuBar(menuBar)                            # Adding the MenuBar to the Frame content.
        
        menuPorts = setupmenu.Append(wx.ID_ANY, "Serial Port", "Change settings");      
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
        
        font = wx.Font(32, wx.TELETYPE, wx.NORMAL, wx.NORMAL)
        
        self.voltageLabel = wx.StaticText(self.mainPanel, -1, "ADC Value:") 
        self.voltageBox = wx.TextCtrl(self.mainPanel)    
        
        self.voltageLabel.SetFont(font)
        self.voltageBox.SetFont(font)
        
        #   Buttons
        self.stopButton = wx.Button(self.mainPanel, -1, 'Stop')
        self.startButton = wx.Button(self.mainPanel, -1, 'Start')
                
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
        self.Bind(wx.EVT_MENU, self.onAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.onExit, menuExit)
        self.Bind(wx.EVT_MENU, self.onOpen, menuOpen)
        self.Bind(wx.EVT_MENU, self.setupPort, menuPorts)        
        self.Bind(wx.EVT_MENU, self.onSave, menuSave)
        
        self.Bind(wx.EVT_BUTTON, self.onStart, self.startButton)
        self.Bind(wx.EVT_BUTTON, self.onStop, self.stopButton)
        self.Bind(EVT_NEW_DATA, self.onNewData)
        
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
            time.sleep(2)			# Give the controller
            port.ser.flushInput()		# Dump anything in the buffer
            
        except :
            self.showComError() 		# Throw up a window
           
        self.statusBar.SetStatusText('Port: ' + port.name )

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
      
    def onNewData(self, e) :
      self.voltageBox.SetValue(dataList[len(dataList)-1].strip())

    def setupPort(self, e) :        
	dia = configSerial.configSerial(self, -1, port)
	dia.ShowModal()   
      
    def onSave(self, e) :
	global dataList
	dlg = wx.FileDialog(self, "Choose a file", '.', "", "*.*", \
                wx.SAVE | wx.OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:	  
	    self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            of = open(os.path.join(self.dirname, self.filename),'w')
            for i in dataList :	      
	      of.write(i)
            of.close()
        dlg.Destroy()
	  
    
    def onStart(self, e) :
        global keepReading
        keepReading = True
        r = readData(self)
        if threading.activeCount() < 2 :
	  r.start()
        
    def onStop(self, e) :
        global keepReading
        keepReading = False        

    def showComError(self) :     #	Can't open COM port
        dlg = wx.MessageDialog(self, "Could not open COM port!\nCheck the config file", 'Error!', wx.OK | wx.ICON_ERROR)  
        dlg.ShowModal()
        self.setupPort(None)
    
    def onAbout(self, e) :     #	Can't open COM port
        dlg = wx.MessageDialog(self, "A simple DMM that reads data over a serial port\n", 'About', wx.OK | wx.ICON_INFORMATION)  
        dlg.ShowModal()        

    def showBufferFull(self) :
        dlg = wx.MessageDialog(self, "Could not open COM port!", 'Error!', wx.OK | wx.ICON_ERROR)
        dlg.showModal()


class readData(Thread) :
    def __init__(self, parent):
        Thread.__init__(self)
        self.setDaemon(True)    #  If you don't do this then the thread can get abandoned
        self.parent = parent
        
    def run(self) :        
        window = self.parent
        evt = NewDataEvent()
        global keepAlive
        global dataList
        global maxLength
        while keepAlive and keepReading:   
	    
            i = port.ser.readline()  
            dataList.append(i)
            if len(dataList) > maxLength :
	      dataList.pop(0)
	      
	      wx.PostEvent(self.parent, evt)
	      
            
            #time.sleep(0.1)

if __name__ == '__main__':
    port = configSerial.Port('dmm.config')

    app = wx.App(False)         # wx instance
    frame = MainWindow(None)    # main window frame

    app.MainLoop()
