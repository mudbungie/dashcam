#!/usr/bin/env python3

# Daemon that watches the camera, and records things.

import picamera
import time

def get_config():
    # Open a JSON file

# Return a configured camera.
def init_cam():
    cam = picamera.PiCamera()
    cam.resolution = (1280, 720)
    return cam

def start_recording():
    cam = init_cam()
    
