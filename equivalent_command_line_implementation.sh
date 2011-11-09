#!/bin/bash
gst-launch-0.10 -vvv rtspsrc location='rtsp://192.168.1.61:554/axis-media/media.amp?videocodec=jpeg&audio=0' ! rtpjpegdepay ! ffdec_mjpeg ! xvimagesink
