wxDmm
===========

wxDmm is a simple digital meter that will read a value from an analog to digital converter over a serial
port and convert it to a voltage.  Each data point needs to be terminated with a 'newline' character (\n). 
The data is appended into a buffer that can be saved to a file for further evaluation.  The buffer will 
maintain a fixed length once it is filled to preserve memory.  The amount of free space in the buffer
is shown in the status bar

wxDmm is written in Python and uses wxPython for the GUI.  The original concept was proposed by Joe Pardue 
of http://smileymicros.com/ and I developed it to demonstrate threading and using wxPython for GUI 
development for a talk I was going to give at the Knoxville Robotics Club (www.knoxarearobotics.com).

An arduino or other similar microcontroller with a serial connection can be used for the data collection.  
An example sketch for an Arduino is included in the distribution package for example purposes.  The example
given for the analogRead() function on the Arduino site works well with wxDmm.  Increase the baud rate 
to 115200 to improve responsiveness.

http://arduino.cc/en/Reference/analogRead

This system is far from accurate and it is very likely to damage something if used incorrectly.  I am
not responsible if something goes wrong.

Project home page:
https://github.com/jes1510/wxDmm


