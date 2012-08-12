wxDmm
===========
Written by Jesse Merritt
www.github.com/jes1510
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
    along with this program.  If not, see <http://www.gnu.org/licenses/

wxDmm is a simple digital meter that will read a value from an analog to digital converter over a serial
port and convert it to a voltage.  Each data point needs to be terminated with a 'newline' character (\n). 
The data is appended into a buffer that can be saved to a file for further evaluation.  The buffer will 
maintain a fixed length once it is filled to preserve memory.  The amount of free space in the buffer
is shown in the status bar.

wxDmm is written in Python and uses wxPython for the GUI.  The original concept was proposed by Joe Pardue 
of http://smileymicros.com/ and I developed it to demonstrate threading and using wxPython for GUI 
development for a talk I was going to give at the Knoxville Robotics Club (www.knoxarearobotics.com).  It
requires the configSerial module here:
https://github.com/jes1510/wx-configSerial/blob/master/configSerial.py

pySerial is also required:
http://pyserial.sourceforge.net/	

An arduino or other similar microcontroller with a serial connection can be used for the data collection.
The example given for the analogRead() function on the Arduino site works well with wxDmm.  Increase the 
baud rate to 115200 to improve responsiveness and sample rate.
http://arduino.cc/en/Reference/analogRead

This system is far from accurate and it is very likely to damage something if used incorrectly.  I am
not responsible if something goes wrong.

Project home page:
https://github.com/jes1510/wxDmm


