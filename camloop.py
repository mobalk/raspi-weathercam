#!/usr/bin/env python3

import picamera
from time import sleep
from PIL import Image, ImageStat, ImageFont, ImageDraw
import time
import sys
import io
import os
from os import path
import fileinput
from ftplib import FTP
import logging
import config as conf

SEC_PER_MIN = 60
LOGFILE = "weathercam.log"

logging.basicConfig(filename=LOGFILE, level=logging.INFO)
print("Logging to " + LOGFILE)

logging.debug("Python version: \n" + sys.version)


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

def writetoimage(img, text):
    font = ImageFont.truetype("/usr/share/fonts/dejavu/DejaVuSans.ttf", 16)
    draw = ImageDraw.Draw(img)
    draw.text((0,0), text, (255,255,0), font=font)


def smartSleep(brightness, sleepTimer):
    global darkCounter
    logging.debug("smartSleep >> br=" + str(brightness) + ", timer=" + str(sleepTimer)
                  + ", darkCounter=" + str(darkCounter))
    nightTsh = config.getint('upload', 'NightTreshold', fallback=4)
    if brightness < nightTsh:
        darkCounter += 1
        if darkCounter % 3 == 0:
            sleepTimer = min(15 * SEC_PER_MIN, sleepTimer * 3)
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


def ftpUpload(img):
    server = config.get('upload','FtpAddress')
    user= config.get('upload','User')
    logging.debug("upload to " + server + " as " + user)
    with FTP(host=server, user=user,
             passwd=config.get('upload','Pwd')) as ftp:
        fp = open(img, 'rb')
        ftp.storbinary('STOR %s' % os.path.basename(img), fp, 1024)
        fp.close()
        logging.info("... " + img + " uploaded")

config = conf.init()

with picamera.PiCamera() as camera:
    while True: # extern loop that allows reconfiguring camera setup
        try:
            # Configure camera
            logging.info("Re-read config")
            conf.read(config)
            res = config.get('camera', 'Resolution', fallback='')
            logging.info("resolution: " + res)
            if res : camera.resolution = res

            # Read all other configuration
            qual = config.getint('jpg', 'Quality', fallback=90)
            brTsh = config.getint('upload', 'BrightnessTreshold', fallback=10)
            server = config.get('upload', 'FtpAddress', fallback='')
            user = config.get('upload', 'User', fallback='')
            pwd = config.get('upload', 'Pwd', fallback='')
            sleepTimer = config.getint('camera', 'SecondsBetweenShots', fallback=60)
            previewTimer = config.getint('camera', 'ShowPreviewBeforeCapture', fallback=3)
            imgPath = config.get('app', 'ImageStorePath', fallback='/tmp/')
            darkCounter = 0

            while True: # Intern loop for continous captures
                stream = io.BytesIO()

                camera.start_preview()
                sleep(previewTimer)
                camera.capture(stream, format='jpeg', quality=qual)
                camera.stop_preview()

                filename = imgPath + "IMG-" + time.strftime("%Y%m%d-%H%M%S") + ".jpg"

                # get brightness info
                stream.seek(0)
                img = Image.open(stream)
                bright = int(brightness(img))

                # save
                img.save(filename, quality = qual, optimize = True)

                filesize = round(os.stat(filename).st_size / 1024 * 10) / 10
                logging.info(filename + ", size=" + str(filesize)
                             + ", brightness=" + str(bright))

                # upload always
                if True or bright > brTsh:
                    if server:
                        ftpUpload(filename)
                else:
                    logging.debug("Skip to upload, brightness " + str(bright)
                                  + " under treshold " + str(brTsh))

                sleepTimer = smartSleep(bright, sleepTimer)
                sleep(sleepTimer)
        except KeyboardInterrupt:
            print("\n\nEnter 'c' for [c]ontinue ar anything else to exit.")
            userinput = input("Whats next?")
            if userinput == 'c':
                continue
            else:
                break

        finally:
            camera.stop_preview()
            logging.warning("Finally block")


