#!/usr/bin/env python3
""" Open a photo periodically and upload to idokep.hu weather service """
from time import sleep
import time
import datetime
import sys
import io
import os
from ftplib import FTP, error_temp
import logging
from fractions import Fraction

from PIL import Image, ImageStat

import config

SEC_PER_MIN = 60

# Set the directory to monitor
directory_to_monitor = "/home/capri/Pictures/raw"

# Function to get the latest image file from the directory
def get_latest_image(directory):
    # Get a list of all files in the directory
    files = [f for f in os.listdir(directory) if f.lower().endswith(('png', 'jpg', 'jpeg', 'gif', 'bmp'))]
    
    if not files:
        return None
    
    # Get the full path and modification time for each file
    file_paths = [os.path.join(directory, f) for f in files]
    latest_file = max(file_paths, key=os.path.getmtime)
    
    return latest_file

# Function to open the latest image
def open_image(image_path):
    try:
        img = Image.open(image_path)
        print(f"Opened image: {image_path}")
        main(img)
    except Exception as e:
        print(f"Error opening image {image_path}: {e}")

# Function to delete the image file after processing
def delete_image(image_path):
    try:
        os.remove(image_path)  # Delete the image file
        print(f"Deleted image: {image_path}")
    except Exception as e:
        print(f"Error deleting image {image_path}: {e}")

# Main loop that runs indefinitely
def monitor_directory():
    last_seen_image = None
    logfile = "weathercam.log"
    logging.basicConfig(filename=logfile, level=logging.INFO)
    print("Logging to " + logfile)
    logging.debug("Python version: \n%s", sys.version)

    while True:
        try:
            # Configure camera
            logging.info("Re-read config")
            config.reread()

            # Read all other configuration
            img_path = config.get('app', 'ImageStorePath', fallback='/tmp/')
            os.makedirs(img_path, exist_ok=True)
      
            while True:
                latest_image = get_latest_image(directory_to_monitor)
            
                # Check if a new image has appeared
                if latest_image != last_seen_image:
                    if latest_image:
                        open_image(latest_image)
                        delete_image(latest_image)
                        last_seen_image = latest_image
                
                # Wait for a short interval before checking again (e.g., 5 seconds)
                time.sleep(5)
        except KeyboardInterrupt:
            print("\n\nEnter 'c' for [c]ontinue ar anything else to exit.")
            userinput = input("Whats next?\n")
            if userinput == 'c':
                continue
            #else:
            break

        finally:
            logging.warning("Finally block", exc_info=True)

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
    server = config.get('upload', 'FtpAddress', fallback='')
    if server:
        user = config.get('upload', 'User')
        logging.debug("upload to " + server + " as " + user)
        try:
            max_timeout = config.getint('camera', 'SecondsBetweenShots', fallback=60)
            with FTP(host=server, user=user, passwd=config.get('upload', 'Pwd'),
                    timeout=max_timeout) as ftp:
                file_obj = open(img, 'rb')
                ftp.storbinary('STOR %s' % os.path.basename(img), file_obj, 1024)
                file_obj.close()
                logging.info("... %s uploaded %s", img, get_extra_line_wrap())
        except (OSError, error_temp):
            logging.exception("%s | ftp_upload caught an error", time.strftime("%Y.%m.%d %H:%M"))
        except:
            logging.exception("%s | unexpected error", time.strftime("%Y.%m.%d %H:%M"))

def crop_image(img):
    """ Crop image as configured. """
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

def main(img):
    img_path = config.get('app', 'ImageStorePath', fallback='/tmp/')
    filename = img_path + "IMG-" + time.strftime("%Y%m%d-%H%M%S") + ".jpg"

    # crop - if configured
    if config.getboolean('camera', 'CropImage'):
        img = crop_image(img)

    # save
    qual = config.getint('jpg', 'Quality', fallback=90)
    img.save(filename, quality=qual, optimize=True)

    # get brightness info of cropped img
    bright = int(brightness(img))

    filesize = round(os.stat(filename).st_size / 1024 * 10) / 10
    logging.info("%s, size=%d, brightness=%d", filename, filesize, bright)

    ftp_upload(filename)

if __name__ == "__main__":
    monitor_directory()
