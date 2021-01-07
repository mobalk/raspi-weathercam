import configparser
import os
from PIL import Image, ImageChops, ImageEnhance
import logging

LOGFILE = "arch.log"

logging.basicConfig(level=logging.DEBUG)
#logging.basicConfig(filename=LOGFILE, level=logging.DEBUG)
print("Logging to " + LOGFILE)


config = configparser.ConfigParser()
config.read('config.ini')

#newsize = (1014, 760) # 50 % of 2028 x 1560
#newsize = (811, 608) # 40% of 2028 x 1560
factor = 0.4


directory = config.get('app', 'ImageStorePath', fallback='/tmp/')
try:
    os.mkdir(directory + '/' + 'arch')
except FileExistsError:
    pass

try:
    os.mkdir(directory + '/' + 'archived')
except FileExistsError:
    pass

im1 = None
im2 = None
ans = None

for filename in sorted(os.listdir(directory)):
    logging.debug(directory + " / " + filename)
    #userinput = input("go?")
    im1 = Image.open(directory + "/" + filename)
    newsize = (int(im1.width * factor), int(im1.height * factor))
    im1 = im1.resize(newsize, resample=Image.LANCZOS)
    newPath = directory + "/arch/" + filename
    if os.path.exists(newPath) and ans != "O":
        if ans == "S": continue
        print(newPath + " exists. What to do?\n [o]verwrite, [s]kip, [O]verwrite all, [S]kip all, e[x]it? ")
        while True:
            ans = input()
            if ans in ('o', 'O', 's', 'S', 'x'): break
        if ins == "s": continue
        if ans == "x": break

    im1.save(directory + "/arch/" + filename, quality=95, optimize = True)
    os.replace(directory + "/" + filename, directory + "/archived/" + filename)

