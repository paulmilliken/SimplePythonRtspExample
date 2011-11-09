#!/usr/bin/python

'''This program is a simple example of how to display an RTSP video stream from
an Axis camera.

The Axis P1347 camera appears to be capable of streaming H.264 encoded video up
to resolutions of 2560x1920.  However, a resolution of 1600x1200 is the highest
that I got to work with mjpeg encoding, used in this example.  The advantage of
mjpeg encoding is lower latency.'''

__author__ = 'Paul Milliken'
__licence__ = 'GPLv3'
__version__ = 0.1
__maintainer__ = 'Paul Milliken'
__email__ = 'paul.milliken@gmail.com'
__status__ = 'Prototype'

import AxisRtspSimple
import pygtk
import gtk
import time
import gobject
gobject.threads_init()

class OperatorInterface:
    '''An instatiation of the OperatorInterface class creates a GTK window to
    display an RTSP video stream from the IP address given by the argument.
    Currently, only Axis P1347 cameras have been tested.'''

    def __init__(self, ipAddress):
        '''Sets up the GTK interface and the RTSP pipelines using GStreamer'''
        self.ipAddress = ipAddress
        self.setUpGTKWindow()
        self.setUpGTKCallbacks()
        self.instantiateRtspPipeline()

    def setUpGTKWindow(self):
        '''There is only one fullscreen window with no buttons'''
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.vbox = gtk.VBox()
        self.drawingArea = gtk.DrawingArea()
        self.vbox.pack_start(self.drawingArea)
        self.window.add(self.vbox)
        self.window.show_all()
    
    def setUpGTKCallbacks(self):
        self.window.connect('destroy', self.quitApplication)
        self.window.connect('key-press-event', self.onKeypress)
    
    def quitApplication(self, widget):
        gtk.main_quit()

    def onKeypress(self, widget, event):
        if event.keyval==gtk.keysyms.q:
            self.quitApplication(widget)
        if event.keyval==gtk.keysyms.p:
            self.rtspPipeline.pauseOrUnpauseVideo()
  
    def instantiateRtspPipeline(self):
        self.rtspPipeline = \
            AxisRtspSimple.RtspPipelineSimple(\
            self.ipAddress, self.drawingArea.window.xid)

def test():
    '''Test for only one camera recording to file.  The camera has ipaddress
    192.168.1.61'''
    operatorInterface = OperatorInterface('192.168.1.61')
    operatorInterface.rtspPipeline.setPipelineStateToPlaying()
    gtk.main()
    return(operatorInterface)

if __name__=='__main__':
    testInterface = test()

