#!/usr/bin/env python3
import sys
from PIL import Image, ImageStat

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
    return (stat.rms[0] / 255.0)

if __name__ == "__main__":
    print(brightness(sys.argv[1]))
