#!/usr/bin/env python3
""" Take a photo periodically and upload to idokep.hu weather service """
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

def brightness(img_obj):
    """ Return image brightness level.

    Algorithm based on
    https://stackoverflow.com/questions/3490727/what-are-some-methods-to-analyze-image-brightness-using-python
    Full black returns 0, full white returns 255
    """
    if isinstance(img_obj, str):
        img = Image.open(img_obj).convert('L')
    else:
        img = img_obj.convert('L')
    stat = ImageStat.Stat(img)
    return stat.rms[0]

def today_at(h_in, m_in=0, sec=0, micros=0):
    """ Return datetime where date part is today and time part comes from input. """
    now = datetime.datetime.now()
    return now.replace(hour=h_in, minute=m_in, second=sec, microsecond=micros)

def get_extra_line_wrap():
    """ Return a line break if in debugging mode, empty string otherwise. """
    lwrap = ""
    if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
        lwrap = "\n"
    return lwrap

def ftp_upload(img):
    """ Upload the image to the configured ftp address. """
    global config
    server = config.get('upload', 'FtpAddress', fallback='')
    if server:
        user = config.get('upload', 'User')
        logging.debug("upload to " + server + " as " + user)
        try:
            with FTP(host=server, user=user, passwd=config.get('upload', 'Pwd')) as ftp:
                file_obj = open(img, 'rb')
                ftp.storbinary('STOR %s' % os.path.basename(img), file_obj, 1024)
                file_obj.close()
                logging.info("... %s uploaded %s", img, get_extra_line_wrap())
        except OSError:
            logging.exception("%s | ftp_upload caught an error", time.strftime("%Y.%m.%d %H:%M"))

def log_camera_settings(camera, bright=None):
    """ Log camera settings in a comma separated style. """
    # pylint: disable=logging-not-lazy
    logging.info('CSV, CAM, %s, exp_mode= %s, framerate= %d, iso= %d, shutter_speed= %d,'
                 + 'digital_gain= %0.4f, analog_gain= %0.4f, exposure_speed= %d, brightness= %d',
                 time.strftime("%Y.%m.%d %H:%M"), camera.exposure_mode, camera.framerate,
                 camera.iso, camera.shutter_speed, float(camera.digital_gain),
                 float(camera.analog_gain), camera.exposure_speed, bright)

def x_within_y_percent_of_z(x_to_compare, y_percent, z_base):
    """ Return true if the input values are within a given y percent range. """
    z_lower = (100 - y_percent) * z_base / 100.0
    z_upper = (100 + y_percent) * z_base / 100.0
    return bool(z_lower <= x_to_compare <= z_upper)

def stabilize_camera_gain(camera):
    """ Wait until analog gain and digital gain stabilizes around some values. """
    prev_an_gain = camera.analog_gain
    prev_dig_gain = camera.digital_gain
    sleep(3)
    while not (x_within_y_percent_of_z(camera.analog_gain, 3, prev_an_gain)
               and x_within_y_percent_of_z(camera.digital_gain, 3, prev_dig_gain)):
        prev_an_gain = camera.analog_gain
        prev_dig_gain = camera.digital_gain
        print(float(prev_an_gain), float(prev_dig_gain), camera.exposure_speed)
        sleep(3)

def manual_expo_mode(state):
    """ Bool to express if mode is manual. """
    return state["expo_mode"] == "manual"

def adjust_camera_exp_mode(camera, bright, expo_state):
    """ Switch between auto exposure and manual exposure based on brightness.
    Try to adjust shutter speed in manual mode with a smooth transition.
    """
    global config
    max_ss = 6 # longest shutter speed in sec
    increase_ss = 300 * 1000 # increase shutter speed in manual mode (uSec)

    skip_current_loop = False

    logging.debug("cropped brightness=%d, shutterspeed=%d", bright, camera.shutter_speed)

    # Handle dark scene
    if bright < 20:
        if not manual_expo_mode(expo_state):
            expo_state["expo_mode"] = "manual"
            stabilize_camera_gain(camera)
            camera.exposure_mode = 'off'
            camera.framerate = Fraction(1, max_ss)
            camera.shutter_speed = camera.exposure_speed
            logging.debug("set manual_expo_mode, shutterspeed=%d", camera.shutter_speed)
            skip_current_loop = True
        elif camera.shutter_speed < int((max_ss) * 1000 * 1000):
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
            logging.warning("VERY strange. Shutter before %d, after %d",
                            cam_ss_now, camera.shutter_speed)
            sleep(3) # stop a bit and think hard
            # try to reduce it with double
            camera.shutter_speed = cam_ss_now - (2 * expo_state["decrease_ss"])
            if camera.shutter_speed > cam_ss_now:
                logging.warning("VERY VERY strange. Shutter before %d, after %d",
                                cam_ss_now, camera.shutter_speed)
                sleep(3) # stop a bit and think hard

                target_ss = cam_ss_now - expo_state["decrease_ss"]
                # first reset then assign slowly increase until needed
                needtobe = 0
                delta = 100000
                camera.shutter_speed = needtobe
                while camera.shutter_speed < target_ss:
                    needtobe += delta
                    camera.shutter_speed = needtobe
                    logging.debug("needtobe: %d, ss: %d", needtobe, camera.shutter_speed)

                camera.shutter_speed = needtobe - delta
                if camera.shutter_speed > cam_ss_now:
                    logging.warning("VERY VERY VERY strange. Shutter before %d, after %d",
                                    cam_ss_now, camera.shutter_speed)
                    # fake a morning to switch back to auto exposure
                    bright = 101

        if bright > 100 or camera.shutter_speed < 500 * 1000:
            camera.shutter_speed = 0
            camera.exposure_mode = 'night'
            expo_state["expo_mode"] = "auto"
        elif bright > 60:
            # reduce more, before it gets too bright
            camera.shutter_speed -= expo_state["decrease_ss"]

        logging.debug("reduced shutterspeed=%d (by %d)",
                      camera.shutter_speed, (cam_ss_now - camera.shutter_speed))
    return skip_current_loop

def set_resolution(camera):
    """ Set camera resolution according configured values. """
    global config
    if config.getboolean('camera', 'CropImage'):
        res = config.get('camera', 'FullResolution', fallback='')
    else:
        res = config.get('camera', 'Resolution', fallback='')
    logging.info("resolution: %s", res)
    if res:
        camera.resolution = res

def crop_image(img):
    """ Crop image as configured. """
    global config
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

def sleep_a_bit(expo_state):
    """ Sleep after each cycle."""
    global config
    if manual_expo_mode(expo_state):
        sleep(config.getint('camera', 'SecondsBetweenShotsAtNight', fallback=120))
    else:
        sleep(config.getint('camera', 'SecondsBetweenShots', fallback=60))

def main():
    """ Start PiCamera and take pictures until program is terminated. """
    global config

    expo_state = {
        "expo_mode": "auto", # "manual"
        "twilight_start": today_at(0),
        "decrease_ss": 300 * 1000 # decrease shutter speed in manual mode (uSec)
    }

    logfile = "weathercam.log"
    logging.basicConfig(filename=logfile, level=logging.DEBUG)
    print("Logging to " + logfile)
    logging.debug("Python version: \n%s", sys.version)

    with picamera.PiCamera() as camera:
        while True: # extern loop that allows reconfiguring camera setup
            try:
                # Configure camera
                logging.info("Re-read config")
                conf.read(config)

                set_resolution(camera)
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
                        img = crop_image(img)

                    # save
                    img.save(filename, quality=qual, optimize=True)

                    # get brightness info of cropped img
                    bright = int(brightness(img))

                    skip_this_loop = adjust_camera_exp_mode(camera, bright, expo_state)
                    if skip_this_loop:
                        continue

                    filesize = round(os.stat(filename).st_size / 1024 * 10) / 10
                    logging.info("%s, size=%d, brightness=%d", filename, filesize, bright)

                    ftp_upload(filename)

                    sleep_a_bit(expo_state)
            except KeyboardInterrupt:
                print("\n\nEnter 'c' for [c]ontinue ar anything else to exit.")
                userinput = input("Whats next?\n")
                if userinput == 'c':
                    continue
                #else:
                break

            finally:
                logging.warning("Finally block", exc_info=True)

config = conf.init()

if __name__ == "__main__":
    main()
