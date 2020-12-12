#!/usr/bin/env python3

from picamera import PiCamera
from time import sleep
from PIL import Image, ImageStat, ImageFont, ImageDraw
import time
import sys
import io
import configparser

print("Python version")
print (sys.version)

# full black: return 0
# full white: return 255
# https://stackoverflow.com/questions/3490727/what-are-some-methods-to-analyze-image-brightness-using-python
def brightness( img_obj ):
    print(type(img_obj))
    #print("brightImg " + type(img_obj))
    if isinstance(img_obj, str):
        im = Image.open(img_obj).convert('L')
        print("converted ")
    else:
        im = img_obj.convert('L')
    stat = ImageStat.Stat(im)
    return stat.rms[0]

config = configparser.ConfigParser()
config.read('config.ini')
res = config.get('camera', 'Resolution', fallback='')
print("resolution: " + res)

camera = PiCamera()
#camera = PiCamera(resolution = res)
if res : camera.resolution = res

stream = io.BytesIO()

camera.start_preview()
sleep(3)

filename = "/tmp/IMG-" + time.strftime("%Y%m%d-%H%M%S") + ".jpg"
print(filename)

camera.capture(stream, format='jpeg')

camera.stop_preview()

# add brightness info
stream.seek(0)
img = Image.open(stream)
font = ImageFont.truetype("/usr/share/fonts/dejavu/DejaVuSans.ttf", 16)
draw = ImageDraw.Draw(img)
bright = brightness(img)

draw.text((0,0), "Brightness: " + str(bright), (255,255,0), font=font)

# save
qual = config.getint('jpg', 'Quality', fallback=90)
img.save(filename[:-4] + "e.jpg", quality = qual)

# upload
brTsh = config.getint('upload', 'BrightnessTreshold', fallback=10)
if bright > brTsh:
    server = config.get('upload', 'FtpAddress', fallback='')
    if server:
        print("upload to " + server)


# --- BACKUP ---
#camera.start_preview()
#sleep(500)
#camera.stop_preview()

print(brightness('/home/pi/tast1.jpg'))

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

