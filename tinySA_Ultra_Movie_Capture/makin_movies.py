#!/usr/bin/env python3

#  Captures images from the tinySA4 (Ultra) and uses those images to create movies
#  Run with -h for usage
#
#    Requires:  pip3 install moviepy, pyserial, numpy, pillow
#
#    Example to create images every second and movies every minute:
#       mkdir images movies
#       ./makin_movies.py images/img movies/movie --max-hold --frame-period=1 --frame-count=60
#       # Images will be stored as images/img_* and movies will be stored as movies/movie_*
#
#
# If using with older tinySA (non tinySA4), you might need to change (LCD_WIDTH,LCD_HEIGHT) to (320,240)

import serial
import numpy as np
import struct
from serial.tools import list_ports
from moviepy.editor import ImageSequenceClip
from datetime import datetime, timedelta
import time

VID = 0x0483 #1155
PID = 0x5740 #22336
LCD_WIDTH = 480
LCD_HEIGHT = 320

# Get nanovna device automatically
def getport() -> str:
    device_list = list_ports.comports()
    for device in device_list:
        if device.vid == VID and device.pid == PID:
            print ("getport() found VID=0x%04x PID=0x%04x" % (VID, PID))
            print (device)
            return device.device
    raise OSError("device not found")

class NanoVNA:
    def __init__(self, dev = None):
        self.dev = dev or getport()
        self.serial = None
        self._frequencies = None
        self.points = 101

    def open(self):
        if self.serial is None:
            print("Opening serial connection...")
            self.serial = serial.Serial(self.dev)
            print("Serial connection:", self.serial)

    def close(self):
        if self.serial:
            self.serial.close()
        self.serial = None

    def send_command(self, cmd):
        self.open()
        self.serial.write(cmd.encode())
        self.serial.readline() # discard empty line

    def resume(self):
        self.send_command("resume\r")

    def calc(self, calc_cmd):
        self.send_command(f"calc {calc_cmd}\r")

    def restart_maxhold(self):
        print("Resetting max hold...")
        self.calc("off")
        self.calc("maxh")
        time.sleep(1.0)

    def capture(self):
        from PIL import Image
        self.send_command("capture\r")
        bytesToRead = LCD_WIDTH * LCD_HEIGHT * 2
        b = self.serial.read(bytesToRead)
        x = struct.unpack(">%dH" % (LCD_WIDTH * LCD_HEIGHT), b)
        # convert pixel format from 565(RGB) to 8888(RGBA)
        arr = np.array(x, dtype=np.uint32)
        arr = 0xFF000000 + ((arr & 0xF800) >> 8) + ((arr & 0x07E0) << 5) + ((arr & 0x001F) << 19)
        return (b, Image.frombuffer('RGBA', (LCD_WIDTH, LCD_HEIGHT), arr, 'raw', 'RGBA', 0, 1))

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage="%prog: [options] <image_prefix> <movie_prefix>")
    parser.add_option("-d", "--dev", dest="device",
                      help="device node", metavar="DEV")
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=False,
                      help="verbose output")
    parser.add_option("-p", "--frame-period", type="int", default=1, help="Seconds per frame, min 1")
    parser.add_option("-c", "--frame-count", type="int", default=60, help="Frames per movie, min 1")
    parser.add_option("-x", "--max-hold", action="store_true", default=False, help="Start max hold at start of movie")

    (opt, args) = parser.parse_args()

    nv = NanoVNA(opt.device or getport())

    if len(args) != 2:
        parser.error("incorrect number of arguments")

    image_prefix = args[0]
    movie_prefix = args[1]

    fps = 1./opt.frame_period
    print(f"Frame Period = {opt.frame_period}  (FPS = {fps})  Frames Per Movie = {opt.frame_count}")
    print(f"Image prefix = {image_prefix}  Movie Prefix = {movie_prefix}")
    print(f"Max hold = {'ON' if opt.max_hold else 'OFF'}")


    file_open = False
    image_list = []

    if opt.max_hold:
        nv.restart_maxhold()

    while 1:
        lastFrameTime = datetime.now()
        datetimeString = lastFrameTime.strftime("%F-%H-%M-%S")

        # Make capture
        (raw_data,img) = nv.capture()

        # Write to image file
        image_filename = f"{image_prefix}_{datetimeString}.png"
        img.save(image_filename)
        print(f"Wrote image file {image_filename}  -- Frame {len(image_list)+1}/{opt.frame_count}")

        # Add to clip list
        if len(image_list) == 0:
            movie_filename = f"{movie_prefix}_{datetimeString}.mp4"
        image_list.append(image_filename)

        if len(image_list) >= opt.frame_count:

            # Write clip list to file
            clip = ImageSequenceClip(image_list, fps=fps)
            try:
                clip.write_videofile(movie_filename, audio = False)
                print(f"Wrote video file {movie_filename}")
            except:
                print(f"Error writing to {movie_filename}")
            image_list = []

            if opt.max_hold:
                nv.restart_maxhold()

        sleep_time = (lastFrameTime - datetime.now() + timedelta(seconds=opt.frame_period)).total_seconds()
        if sleep_time > 0:
            time.sleep(sleep_time)
