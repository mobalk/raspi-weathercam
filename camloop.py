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

# Wait until analog gain and digital gain stabilizes around some values
def stabilizeCameraGain(camera):
    prevAnGain = camera.analog_gain
    prevDigGain = camera.digital_gain
    sleep(3)
    while camera.analog_gain != prevAnGain or camera.digital_gain != prevDigGain:
        prevAnGain = camera.analog_gain
        prevDigGain = camera.digital_gain
        print(float(prevAnGain), float(prevDigGain), camera.exposure_speed)
        sleep(3)

# Switch between auto exposure and manual exposure based on brightness
# Adjust shutter speed in manual mode with a smooth transition.
def adjustCameraExposureMode(camera, brigth):
    global manualExpoMode
    global twilightStart
    global decreaseSS
    skipCurrentLoop = False

    logging.debug("cropped brightness=%d, shutterspeed=%d", bright, camera.shutter_speed)

    # Handle dark scene
    if bright < 20:
        if not manualExpoMode:
            manualExpoMode = True
            stabilizeCameraGain(camera)
            camera.exposure_mode = 'off'
            camera.framerate = Fraction(1, MAX_SS)
            camera.shutter_speed = camera.exposure_speed
            logging.debug("set manualExpoMode, shutterspeed=%d", camera.shutter_speed)
            skipCurrentLoop = True
        elif camera.shutter_speed < int((MAX_SS) * 1000 * 1000):
            camera.shutter_speed += increaseSS
            logging.debug("increased shutterspeed=%d", camera.shutter_speed)
            sleep(6) # give some time for adaptation
            skipCurrentLoop = True
        else:
            logging.warning('Too dark scene. ¯\_(ツ)_/¯')
            sleep(15 * SEC_PER_MIN)

    # Handle bright scene in manual mode
    if manualExpoMode and bright > 30:
        if twilightStart <= todayAt(0):
            twilightStart = datetime.datetime.now()
            # try to reach 0.45 sec shutter speed in 30 minutes
            iterations = 30 * SEC_PER_MIN / nightSleepTimer
            dSS = camera.exposure_speed - (450 * 1000)
            decreaseSS = int(dSS / iterations)
            logging.debug('twilight start at ' + twilightStart + ', decreaseSS=' + decreaseSS)

        camera.shutter_speed -= decreaseSS

        if bright > 100 or camera.shutter_speed < 500 * 1000:
            camera.shutter_speed = 0
            camera.exposure_mode = 'night'
            manualExpoMode = False

        logging.debug("reduced shutterspeed=%d", camera.shutter_speed)
    return skipCurrentLoop

config = conf.init()

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
            sleepTimer = config.getint('camera', 'SecondsBetweenShots', fallback=60)
            nightSleepTimer = config.getint('camera', 'SecondsBetweenShotsAtNight', fallback=120)
            previewTimer = config.getint('camera', 'ShowPreviewBeforeCapture', fallback=3)
            imgPath = config.get('app', 'ImageStorePath', fallback='/tmp/')
            darkCounter = 0
            manualExpoMode = False
            twilightStart = todayAt(0)

            MAX_SS = 6 # longest shutter speed in sec
            increaseSS = 300 * 1000 # increase shutter speed in manual mode (uSec)
            decreaseSS = 300 * 1000 # decrease shutter speed in manual mode (uSec)

            camera.exposure_mode = 'night'
            sleep(6) # quickly adapt analog/digital gain, only then slow down framerate
            camera.framerate = Fraction(2, 1) # 'night' mode can handle max 0.5 sec shutter speed

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

                skipThisLoop = adjustCameraExposureMode(camera, bright)
                if skipThisLoop:
                    continue

                filesize = round(os.stat(filename).st_size / 1024 * 10) / 10
                logging.info(filename + ", size=" + str(filesize)
                             + ", brightness=" + str(bright))

                # upload always
                if server:
                    ftpUpload(filename)
                    #pass

                if manualExpoMode:
                    sleep(nightSleepTimer)
                else:
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


