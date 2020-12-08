#!/usr/bin/env python

from picamera import PiCamera
from time import sleep
from PIL import Image, ImageStat, ImageFont, ImageDraw
import time

# full black: return 0
# 1 white dot (800x600): 0.362
# 1/14 white: return 16.15
# full white: return 255
# treshold: 7-10
# https://stackoverflow.com/questions/3490727/what-are-some-methods-to-analyze-image-brightness-using-python
def brightness( im_file ):
    im = Image.open(im_file).convert('L')
    stat = ImageStat.Stat(im)
    return stat.rms[0]

def brightnessImg( img_obj ):
    im = img_obj.convert('L')
    stat = ImageStat.Stat(im)
#     im.save("/tmp/pic111L.jpg")
    return stat.rms[0]

camera = PiCamera()
camera.start_preview()
sleep(3)
filename = "/tmp/IMG-" + time.strftime("%Y%m%d-%H%M%S") + ".jpg"
print(filename)
camera.capture(filename)
camera.stop_preview()

font = ImageFont.truetype("/usr/share/fonts/dejavu/DejaVuSans.ttf", 16)
# img = Image.new("RGBA", (200,200), (120,20,20))
img = Image.open(filename)
draw = ImageDraw.Draw(img)
draw.text((0,0), "Brightness: " + str(brightnessImg(img)), (255,255,0), font=font)
# img.show()
img.save(filename[:-4] + "e.jpg")

#camera.start_preview()
#sleep(50)
#camera.stop_preview()

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
