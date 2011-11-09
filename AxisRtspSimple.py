#!/usr/bin/python

'''This module contains the lower-level classes that allow an RTSP pipeline to
be built and manipulated.  Only Axis P1347 cameras have been tested with motion
jpeg encoding.'''

__author__ = 'Paul Milliken'
__licence__ = 'GPLv3'
__version__ = 0.1
__maintainer__ = 'Paul Milliken'
__email__ = 'paul.milliken@gmail.com'
__status__ = 'Prototype'

import pygst
pygst.require('0.10')
import gst
import gtk
import datetime

class RtspBaseClass:
    '''RtspBaseClass is a base class that provides the building blocks for other
    classes that create rtsp pipelines.  Commonly used gstreamer pipeline 
    elements and callback methods are defined within.'''
    
    def createEmptyPipeline(self):
        self.pipeline = gst.Pipeline('mypipeline')

    def createRtspsrcElement(self):
        '''The name of each rtsp source element is a string representing its
        ipaddress'''
        self.source = gst.element_factory_make('rtspsrc', 'source')
        self.source.set_property('latency', 0)
        self.formRtspUri()
        self.source.set_property('location', self.rtspUri)

    def formRtspUri(self):
        '''The rtsp stream can be accessed via this string on Axis cameras:'''
        self.rtspUri = \
            'rtsp://%s:554/axis-media/media.amp?videocodec=jpeg&audio=0' %\
            (self.ipAddress)

    def createDepayElement(self):
        '''creates jpeg depayer element'''
        self.depay = gst.element_factory_make('rtpjpegdepay','mydepay')
        
    def createDecodeElement(self):
        '''creates mjpeg decoder element'''
        self.decode = gst.element_factory_make('ffdec_mjpeg','mydecode')

    def createXvimagesinkElement(self):
        '''Use an xvimagesink rather than ximagesink to utilise video chip
        for scaling etc.'''
        self.xvimagesink = gst.element_factory_make('xvimagesink', \
            'xvimagesink')
        self.xvimagesink.set_xwindow_id(self.xid)
    
    def createPipelineCallbacks(self):
        '''Note that source is an rtspsrc element which has a dynamically 
        created source pad.  This means it can only be linked after the pad has
        been created.  Therefore, the linking is done with the callback function
        onPadAddedToRtspsrc(...):'''
        self.source.connect('pad-added', self.onPadAddedToRtspsrc)
        self.source.connect('pad-removed', self.onPadRemovedFromRtspsrc)

    def onPadAddedToRtspsrc(self, rtspsrc, pad):
        '''This callback is required because rtspsrc elements have
        dynamically created pads.  So linking can only occur after a pad
        has been created.  Furthermore, only the rtspsrc for the currently
        selected camera is linked to the depayer.'''
        print('pad added to rtspsrc element.')
        self.xvimagesink.set_xwindow_id(self.xid)
        depaySinkPad = self.depay.get_pad('sink')
        pad.link(depaySinkPad)

    def onPadRemovedFromRtspsrc(self, rtspsrc, pad):
        '''Unlinks the rtspsrc element from the depayer'''
        print('pad removed from rtspsrc element.')
        depaySinkPad = self.depay.get_pad('sink')
        pad.unlink(depaySinkPad)

    def pauseOrUnpauseVideo(self):
        '''Toggles between the paused and playing states'''
        if (self.pipeline.get_state()[1]==gst.STATE_PAUSED):
            self.setPipelineStateToPlaying()
        else:
            self.setPipelineStateToPaused()
    
    def setPipelineStateToPlaying(self):
        self.pipeline.set_state(gst.STATE_PLAYING)

    def setPipelineStateToPaused(self):
        self.pipeline.set_state(gst.STATE_PAUSED)

    def setPipelineStateToNull(self):
        self.pipeline.set_state(gst.STATE_NULL)

class RtspPipelineSimple(RtspBaseClass):
    '''This class creates a simple rtsp pipeline as an example'''
    
    def __init__(self, ipAddress, xid):
        self.ipAddress = ipAddress
        # xid is the xwindow I.D. where the video stream will be displayed:
        self.xid = xid
        self.createGstreamerPipeline()
        
    def createGstreamerPipeline(self):
        '''This pipeline implements something similar to the following bash
        equivalent in Python: gst-launch-0.10 -vvv rtspsrc 
        location='rtsp://192.168.1.61:554/axis-media/
        media.amp?videocodec=jpeg&audio=0' ! rtpjpegdepay ! ffdec_mjpeg ! 
        ! xvimagesink'''
        self.createEmptyPipeline()
        self.createPipelineElements()
        self.addElementsToPipeline()
        self.linkPipelineElements()
        self.createPipelineCallbacks()

    def createPipelineElements(self):
        self.createRtspsrcElement()
        self.createDepayElement()
        self.createDecodeElement()
        self.createXvimagesinkElement()

    def addElementsToPipeline(self):
        '''Add elements to the pipeline'''
        self.pipeline.add(self.source)
        self.pipeline.add(self.depay)
        self.pipeline.add(self.decode)
        self.pipeline.add(self.xvimagesink)

    def linkPipelineElements(self):
        '''Link all elements in pipeline except source which has a dynamic
        source pad'''
        self.depay.link(self.decode)
        self.decode.link(self.xvimagesink)

