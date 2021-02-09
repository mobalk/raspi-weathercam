#!/usr/bin/env python3

import picamera
from time import sleep
from PIL import Image, ImageStat, ImageFont, ImageDraw
import time
import datetime
import sys
import io
import os
from os import path
import fileinput
from ftplib import FTP
import logging
import config as conf
from fractions import Fraction

SEC_PER_MIN = 60
LOGFILE = "weathercam.log"

logging.basicConfig(filename=LOGFILE, level=logging.DEBUG)
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

def todayAt (hr, min=0, sec=0, micros=0):
   now = datetime.datetime.now()
   return now.replace(hour=hr, minute=min, second=sec, microsecond=micros)

def smartSleep(brightness, sleepTimer):
    global darkCounter
    global wakeupTime # mid of civil twilight

    LONGEST_SLEEP = 15 * SEC_PER_MIN

    logging.debug("smartSleep >> br=" + str(brightness) + ", timer=" + str(sleepTimer)
                  + ", darkCounter=" + str(darkCounter))
    nightTsh = config.getint('upload', 'NightTreshold', fallback=4)
    timeNow = datetime.datetime.now()

    logging.debug('    nightTrsh: %d, uploadTrsh: %d, timeNow: %s, wakeupTime: %s',
                  nightTsh, brTsh, timeNow, wakeupTime)
    if (timeNow < todayAt(6) or timeNow > todayAt(12)) and brightness < nightTsh:
        darkCounter += 1
        if darkCounter % 3 == 0 and sleepTimer <= LONGEST_SLEEP:
            sleepTimer = min(LONGEST_SLEEP, sleepTimer * 3)
            logging.info("Set capture timer to " + str(sleepTimer / SEC_PER_MIN) + " min")
    else:
        if brightness > brTsh:
            if darkCounter > 0:
                wakeupTime = timeNow - datetime.timedelta(seconds=LONGEST_SLEEP)
                darkCounter = 0
                logging.info('    New wakeupTime: %s', wakeupTime)

        origTimer = config.getint('camera', 'SecondsBetweenShots', fallback=60)
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
    try:
        with FTP(host=server, user=user,
                 passwd=config.get('upload','Pwd')) as ftp:
            fp = open(img, 'rb')
            ftp.storbinary('STOR %s' % os.path.basename(img), fp, 1024)
            fp.close()
            logging.info("... " + img + " uploaded")
    except Exception as ex:
        logging.exception(time.strftime("%Y.%m.%d %H:%M") + ' | ftpUpload caught an error')

def logCameraSettings(camera, brigth = None):
    logging.info('CSV, CAM, '
                 + time.strftime("%Y.%m.%d %H:%M")
                 + ', exp_mode= ' + camera.exposure_mode
                 + ', framerate= ' + str(camera.framerate)
                 + ', iso= ' + str(camera.iso)
                 + ', shutter_speed= ' + str(camera.shutter_speed)
                 + ', digital_gain= ' + str(float(camera.digital_gain))
                 + ', analog_gain= ' + str(float(camera.analog_gain))
                 + ', exposure_speed= ' + str(camera.exposure_speed)
                 + ', brightness= ' + str(brigth))

config = conf.init()
wakeupTime = todayAt(6)

with picamera.PiCamera() as camera:
    while True: # extern loop that allows reconfiguring camera setup
        try:
            # Configure camera
            logging.info("Re-read config")
            conf.read(config)
            if config.getboolean('camera', 'CropImage'):
                res = config.get('camera', 'FullResolution', fallback='')
            else:
                res = config.get('camera', 'Resolution', fallback='')
            logging.info("resolution: " + res)
            if res : camera.resolution = res

            # Read all other configuration
            qual = config.getint('jpg', 'Quality', fallback=90)
            brTsh = config.getint('upload', 'BrightnessTreshold', fallback=10)
            server = config.get('upload', 'FtpAddress', fallback='')
            user = config.get('upload', 'User', fallback='')
            pwd = config.get('upload', 'Pwd', fallback='')
            defaultSleepTimer = config.getint('camera', 'SecondsBetweenShots', fallback=60)
            previewTimer = config.getint('camera', 'ShowPreviewBeforeCapture', fallback=3)
            imgPath = config.get('app', 'ImageStorePath', fallback='/tmp/')
            darkCounter = 0
            manualExpoMode = False
            sleepTimer = defaultSleepTimer

            MAX_SS = 6 # longest shutter speed
            camera.framerate = Fraction(1, MAX_SS)
            camera.exposure_mode = 'night'

            while True: # Intern loop for continous captures
                stream = io.BytesIO()

                #camera.start_preview()
                sleep(previewTimer)
                camera.capture(stream, format='jpeg', quality=qual)
                #camera.stop_preview()

                filename = imgPath + "IMG-" + time.strftime("%Y%m%d-%H%M%S") + ".jpg"

                stream.seek(0)
                img = Image.open(stream)

                logCameraSettings(camera, int(brightness(img)))

                # crop (if configured)
                if config.getboolean('camera', 'CropImage'):
                    left = config.getint('camera', 'BoxPositionX')
                    top = config.getint('camera', 'BoxPositionY')
                    right = left + config.getint('camera', 'BoxSizeX')
                    bottom = top + config.getint('camera', 'BoxSizeY')

                    logging.debug((left, top, right, bottom))
                    im1 = img.crop((left, top, right, bottom))

                    resizeX = config.getint('camera', 'ResizeX') 
                    resizeY = resizeX \
                              *  config.getint('camera', 'BoxSizeY') \
                              / config.getint('camera', 'BoxSizeX')

                    im1 = im1.resize((int(resizeX), int(resizeY)), resample = Image.LANCZOS)
                    img = im1

                # save
                img.save(filename, quality = qual, optimize = True)

                # get brightness info of cropped img
                bright = int(brightness(img))

                logging.debug("cropped brightness=%d, shutterspeed=%d", bright, camera.shutter_speed)
                if bright < 20 and camera.shutter_speed < int((MAX_SS + 0.1) * 1000 * 1000):
                    if not manualExpoMode:
                        manualExpoMode = True
                        sleep(previewTimer)     # sleep to fix gain values
                        camera.exposure_mode = 'off'
                        camera.shutter_speed = camera.exposure_speed
                        camera.iso = 400

                    camera.shutter_speed += 500 * 1000 # add 0.5 sec
                    logging.debug("increased shutterspeed=%d", camera.shutter_speed)
                    continue
                if manualExpoMode and bright > 30:
                    camera.shutter_speed -= 500 * 1000

                    if camera.shutter_speed < 500 * 1000: # turn off manual expo as second step
                        camera.shutter_speed = 0
                        camera.exposure_mode = 'night'
                        manualExpoMode = False
                        camera.iso = 0
                    elif camera.shutter_speed < 1000 * 1000: # half the iso as first step
                        camera.iso = 200

                    logging.debug("reduced shutterspeed=%d", camera.shutter_speed)

                filesize = round(os.stat(filename).st_size / 1024 * 10) / 10
                logging.info(filename + ", size=" + str(filesize)
                             + ", brightness=" + str(bright))

                # upload always
                if server:
                    ftpUpload(filename)
                    #pass

                sleepTimer = smartSleep(bright, sleepTimer)
                if manualExpoMode:
                    sleepTimer = max(sleepTimer, 5 * SEC_PER_MIN)
                sleep(sleepTimer)
        except KeyboardInterrupt:
            print("\n\nEnter 'c' for [c]ontinue ar anything else to exit.")
            userinput = input("Whats next?\n")
            if userinput == 'c':
                continue
            else:
                break

        finally:
            logging.warning("Finally block")


