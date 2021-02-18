#!/usr/bin/env python3

from time import sleep
import time
import datetime
import sys
import io
import os
from ftplib import FTP
import logging
from fractions import Fraction

from PIL import Image, ImageStat
import picamera

import config as conf

SEC_PER_MIN = 60

# full black: return 0
# full white: return 255
# https://stackoverflow.com/questions/3490727/what-are-some-methods-to-analyze-image-brightness-using-python
def brightness(img_obj):
    if isinstance(img_obj, str):
        img = Image.open(img_obj).convert('L')
    else:
        img = img_obj.convert('L')
    stat = ImageStat.Stat(img)
    return stat.rms[0]

def today_at(h_in, m_in=0, sec=0, micros=0):
    now = datetime.datetime.now()
    return now.replace(hour=h_in, minute=m_in, second=sec, microsecond=micros)

def ftp_upload(config, img):
    server = config.get('upload', 'FtpAddress', fallback='')
    if server:
        user = config.get('upload', 'User')
        logging.debug("upload to " + server + " as " + user)
        try:
            with FTP(host=server, user=user, passwd=config.get('upload', 'Pwd')) as ftp:
                file_obj = open(img, 'rb')
                ftp.storbinary('STOR %s' % os.path.basename(img), file_obj, 1024)
                file_obj.close()
                logging.info("... %s uploaded", img)
        except OSError:
            logging.exception("%s | ftp_upload caught an error", time.strftime("%Y.%m.%d %H:%M"))

def log_camera_settings(camera, bright=None):
    logging.info('CSV, CAM, '
                 + time.strftime("%Y.%m.%d %H:%M")
                 + ', exp_mode= ' + camera.exposure_mode
                 + ', framerate= ' + str(camera.framerate)
                 + ', iso= ' + str(camera.iso)
                 + ', shutter_speed= ' + str(camera.shutter_speed)
                 + ', digital_gain= ' + str(float(camera.digital_gain))
                 + ', analog_gain= ' + str(float(camera.analog_gain))
                 + ', exposure_speed= ' + str(camera.exposure_speed)
                 + ', brightness= ' + str(bright))

# Wait until analog gain and digital gain stabilizes around some values
def stabilize_camera_gain(camera):
    prev_an_gain = camera.analog_gain
    prev_dig_gain = camera.digital_gain
    sleep(3)
    while camera.analog_gain != prev_an_gain or camera.digital_gain != prev_dig_gain:
        prev_an_gain = camera.analog_gain
        prev_dig_gain = camera.digital_gain
        print(float(prev_an_gain), float(prev_dig_gain), camera.exposure_speed)
        sleep(3)

def manual_expo_mode(state):
    return state["expo_mode"] == "manual"

# Switch between auto exposure and manual exposure based on brightness
# Adjust shutter speed in manual mode with a smooth transition.
def adjust_camera_exp_mode(camera, bright, expo_state, config):
    MAX_SS = 6 # longest shutter speed in sec
    increase_ss = 300 * 1000 # increase shutter speed in manual mode (uSec)

    skip_current_loop = False

    logging.debug("cropped brightness=%d, shutterspeed=%d", bright, camera.shutter_speed)

    # Handle dark scene
    if bright < 20:
        if not manual_expo_mode(expo_state):
            expo_state["expo_mode"] = "manual"
            stabilize_camera_gain(camera)
            camera.exposure_mode = 'off'
            camera.framerate = Fraction(1, MAX_SS)
            camera.shutter_speed = camera.exposure_speed
            logging.debug("set manual_expo_mode, shutterspeed=%d", camera.shutter_speed)
            skip_current_loop = True
        elif camera.shutter_speed < int((MAX_SS) * 1000 * 1000):
            camera.shutter_speed += increase_ss
            logging.debug("increased shutterspeed=%d", camera.shutter_speed)
            sleep(6) # give some time for adaptation
            skip_current_loop = True
        else:
            logging.warning(r"Too dark scene. ¯\_(ツ)_/¯")
            sleep(5 * SEC_PER_MIN)

    # Handle bright scene in manual mode
    if manual_expo_mode(expo_state) and bright > 30:
        if expo_state["twilight_start"] <= today_at(0):
            expo_state["twilight_start"] = datetime.datetime.now()
            # try to reach 0.45 sec shutter speed in 15 minutes
            night_sleep_timer = config.getint('camera', 'SecondsBetweenShotsAtNight',
                                              fallback=120)
            iterations = 15 * SEC_PER_MIN / night_sleep_timer
            delta_ss = camera.exposure_speed - (450 * 1000)
            expo_state["decrease_ss"] = int(delta_ss / iterations)
            logging.debug("twilight start at %s, decrease_ss=%d",
                          str(expo_state["twilight_start"]), expo_state["decrease_ss"])

        cam_ss_now = camera.shutter_speed
        camera.shutter_speed -= expo_state["decrease_ss"]
        if camera.shutter_speed > cam_ss_now:
            logging.warning("FURA fura dolog. Elotte %d utana %d", cam_ss_now, camera.shutter_speed) #FIXME
            camera.shutter_speed = camera.exposure_speed - expo_state["decrease_ss"]


        if bright > 100 or camera.shutter_speed < 500 * 1000:
            camera.shutter_speed = 0
            camera.exposure_mode = 'night'
            expo_state["expo_mode"] = "auto"

        logging.debug("reduced shutterspeed=%d (by %d)",
                      camera.shutter_speed, expo_state["decrease_ss"])
    return skip_current_loop

def setResolution(camera, config):
    if config.getboolean('camera', 'CropImage'):
        res = config.get('camera', 'FullResolution', fallback='')
    else:
        res = config.get('camera', 'Resolution', fallback='')
    logging.info("resolution: " + res)
    if res:
        camera.resolution = res

def cropImage(img, config):
    left = config.getint('camera', 'BoxPositionX')
    top = config.getint('camera', 'BoxPositionY')
    right = left + config.getint('camera', 'BoxSizeX')
    bottom = top + config.getint('camera', 'BoxSizeY')

    logging.debug((left, top, right, bottom))
    im1 = img.crop((left, top, right, bottom))

    resize_x = config.getint('camera', 'ResizeX')
    resize_y = resize_x \
               *  config.getint('camera', 'BoxSizeY') \
               / config.getint('camera', 'BoxSizeX')

    im1 = im1.resize((int(resize_x), int(resize_y)), resample=Image.LANCZOS)
    return im1

def sleep_a_bit(expo_state, config):
    if manual_expo_mode(expo_state):
        sleep(config.getint('camera', 'SecondsBetweenShotsAtNight', fallback=120))
    else:
        sleep(config.getint('camera', 'SecondsBetweenShots', fallback=60))

def main():
    expo_state = {
        "expo_mode": "auto", # "manual"
        "twilight_start": today_at(0),
        "decrease_ss": 300 * 1000 # decrease shutter speed in manual mode (uSec)
    }
    LOGFILE = "weathercam.log"
    logging.basicConfig(filename=LOGFILE, level=logging.DEBUG)
    print("Logging to " + LOGFILE)
    logging.debug("Python version: \n%s", sys.version)

    config = conf.init()

    with picamera.PiCamera() as camera:
        while True: # extern loop that allows reconfiguring camera setup
            try:
                # Configure camera
                logging.info("Re-read config")
                conf.read(config)

                setResolution(camera, config)
                # Read all other configuration
                qual = config.getint('jpg', 'Quality', fallback=90)
                preview_timer = config.getint('camera', 'ShowPreviewBeforeCapture',
                                              fallback=3)
                img_path = config.get('app', 'ImageStorePath', fallback='/tmp/')

                camera.exposure_mode = 'night'
                sleep(6) # quickly adapt analog/digital gain, only then slow down framerate
                camera.framerate = Fraction(2, 1) #'night' mode can handle max 0.5 sec shutter speed

                while True: # Intern loop for continous captures
                    stream = io.BytesIO()

                    #camera.start_preview()
                    sleep(preview_timer)
                    camera.capture(stream, format='jpeg', quality=qual)
                    #camera.stop_preview()

                    filename = img_path + "IMG-" + time.strftime("%Y%m%d-%H%M%S") + ".jpg"

                    stream.seek(0)
                    img = Image.open(stream)

                    log_camera_settings(camera, int(brightness(img)))

                    # crop - if configured
                    if config.getboolean('camera', 'CropImage'):
                        img = cropImage(img, config)

                    # save
                    img.save(filename, quality=qual, optimize=True)

                    # get brightness info of cropped img
                    bright = int(brightness(img))

                    skip_this_loop = adjust_camera_exp_mode(camera, bright, expo_state, config)
                    if skip_this_loop:
                        continue

                    filesize = round(os.stat(filename).st_size / 1024 * 10) / 10
                    logging.info("%s, size=%d, brightness=%d", filename, filesize, bright)

                    ftp_upload(config, filename)

                    sleep_a_bit(expo_state, config)
            except KeyboardInterrupt:
                print("\n\nEnter 'c' for [c]ontinue ar anything else to exit.")
                userinput = input("Whats next?\n")
                if userinput == 'c':
                    continue
                else:
                    break

            finally:
                logging.warning("Finally block", exc_info=True)

if __name__ == "__main__":
    main()
