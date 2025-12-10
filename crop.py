#!/usr/bin/env python3
from time import strftime
import time
import sys
import os

from PIL import Image

import config


# Function to open the latest image
def open_image(image_path):
    try:
        img = Image.open(image_path)
        print(f"Opened image: {image_path}")
        main(img)
    except Exception as e:
        print(f"Error opening image {image_path}: {e}")

def crop_image(img):
    """ Crop image as configured. """
    left = config.getint('camera', 'BoxPositionX')
    top = config.getint('camera', 'BoxPositionY')
    right = left + config.getint('camera', 'BoxSizeX')
    bottom = top + config.getint('camera', 'BoxSizeY')

    im1 = img.crop((left, top, right, bottom))

    resize_x = config.getint('camera', 'ResizeX')
    resize_y = resize_x \
               *  config.getint('camera', 'BoxSizeY') \
               / config.getint('camera', 'BoxSizeX')

    im1 = im1.resize((int(resize_x), int(resize_y)), resample=Image.LANCZOS)
    return im1

def main(img):
    print("MAIN")
    img_path = './'
    filename = img_path + "IMG-" + time.strftime("%Y%m%d-%H%M%S") + ".jpg"

    # crop - if configured
    if config.getboolean('camera', 'CropImage'):
        img = crop_image(img)

    # save
    qual = config.getint('jpg', 'Quality', fallback=90)
    img.save(filename, quality=qual, optimize=True)

    filesize = round(os.stat(filename).st_size / 1024 * 10) / 10
    print(f"created: {filename} size:{filesize}")

if __name__ == "__main__":
    open_image(sys.argv[1])
