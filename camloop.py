#!/usr/bin/env python3

import picamera
from time import sleep
from PIL import Image, ImageStat, ImageFont, ImageDraw
import time
import sys
import io
import configparser
import os.path
from os import path
import logging
logging.basicConfig(level=logging.DEBUG)

logging.debug("Python version: \n" + sys.version)

SEC_PER_MIN = 60

# full black: return 0
# full white: return 255
# https://stackoverflow.com/questions/3490727/what-are-some-methods-to-analyze-image-brightness-using-python
def brightness( img_obj ):
    if isinstance(img_obj, str):
        im = Image.open(img_obj).convert('L')
    else:
        im = img_obj.convert('L')
    stat = ImageStat.Stat(im)
    return stat.rms[0]

# Read config file
def configinit():
    global config
    config = configparser.ConfigParser()
    readconfig()

    userauthconfig = config.get('app', 'PathToUserAuthConfig', fallback='')
    logging.debug("PathToUserAuthConfig: " + userauthconfig)
    if userauthconfig and path.exists(userauthconfig):
        config.read(userauthconfig)
        logging.debug(userauthconfig + " read successfully")

def readconfig():
    config.read('config.ini')

def writetoimage(img, text):
    font = ImageFont.truetype("/usr/share/fonts/dejavu/DejaVuSans.ttf", 16)
    draw = ImageDraw.Draw(img)
    draw.text((0,0), text, (255,255,0), font=font)


def smartSleep(brightness, sleepTimer):
    global darkCounter
    logging.debug("smartSleep >> br=" + str(brightness) + ", timer=" + str(sleepTimer)
                  + ", darkCounter=" + str(darkCounter))
    brTsh = config.getint('upload', 'BrightnessTreshold', fallback=10)
    if brightness < brTsh / 3:
        darkCounter += 1
        if darkCounter % 5 == 0:
            sleepTimer = min(15 * SEC_PER_MIN, sleepTimer * 2)
            logging.info("Set capture timer to " + str(sleepTimer / SEC_PER_MIN) + " min")
    else:
        origTimer = config.getint('camera', 'SecondsBetweenShots', fallback=10)
        darkCounter = 0
        if sleepTimer != origTimer:
            sleepTimer = origTimer
            logging.info("Set capture timer back to " + str(sleepTimer) + " sec")

    logging.debug("smartSleep <<  return timer=" + str(sleepTimer)
                  + ", darkCounter=" + str(darkCounter))
    return sleepTimer


configinit()

with picamera.PiCamera() as camera:
    try:
        # Configure camera
        res = config.get('camera', 'Resolution', fallback='')
        print("resolution: " + res)
        if res : camera.resolution = res

        # Read all other configuration
        qual = config.getint('jpg', 'Quality', fallback=90)
        brTsh = config.getint('upload', 'BrightnessTreshold', fallback=10)
        server = config.get('upload', 'FtpAddress', fallback='')
        user = config.get('upload', 'User', fallback='')
        pwd = config.get('upload', 'Pwd', fallback='')
        sleepTimer = config.getint('camera', 'SecondsBetweenShots', fallback=10)

        darkCounter = 0

        while True:
            stream = io.BytesIO()

            camera.start_preview()
            sleep(3)
            camera.capture(stream, format='jpeg', quality=qual)
            camera.stop_preview()

            filename = "/tmp/IMG-" + time.strftime("%Y%m%d-%H%M%S") + ".jpg"

            # get brightness info
            stream.seek(0)
            img = Image.open(stream)
            bright = int(brightness(img))
            logging.info(filename + ", brightness=" + str(bright))

            # save
            img.save(filename, quality = qual, optimize = True)

            # upload
            if bright > brTsh:
                if server:
                    print("upload to " + server + " as " + user)
            else:
                logging.debug("Skip to upload, brightness " + str(bright)
                              + " under treshold " + str(brTsh))

            sleepTimer = smartSleep(bright, sleepTimer)
            sleep(sleepTimer)
    #except:
    #    logging.warning("Execption occured")
    finally:
        camera.stop_preview()
        logging.warning("Finally block")


# --- BACKUP ---:W

#camera.start_preview()
#sleep(500)
#camera.stop_preview()

#print(brightness('/home/pi/tast1.jpg'))

#         with picamera.PiCamera() as camera:
#             camera.start_preview()
#             try:
#                 for i, filename in enumerate(
#                         camera.capture_continuous('image{counter:02d}.jpg')):
#                     print(filename)
#                     time.sleep(1)
#                     if i == 59:
#                         break
#             finally:
#                 camera.stop_preview()

