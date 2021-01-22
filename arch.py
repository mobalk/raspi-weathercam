import configparser
import os
from PIL import Image, ImageChops, ImageEnhance
import logging
import time

SEC_PER_DAY = 60 * 60 * 24

logging.basicConfig(level=logging.DEBUG)
dryRun = False

config = configparser.ConfigParser()
config.read('config.ini')

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
archiveUntil = time.time() - 7 * SEC_PER_DAY

for filename in sorted(os.listdir(directory)):
    fPath = os.path.join(directory, filename)
    newPath = os.path.join(directory, 'arch', filename)
    movePath = os.path.join(directory, 'archived', filename)
    logging.debug("file=" + fPath
                  + " new=" + newPath
                  + " move=" + movePath)

    if os.path.isfile(fPath) and os.stat(fPath).st_mtime < archiveUntil:
        im1 = Image.open(fPath)
        newsize = (int(im1.width * factor), int(im1.height * factor))
        im1 = im1.resize(newsize, resample = Image.LANCZOS)
        if os.path.exists(newPath) and ans != "O":
            if ans == "S": continue
            print(newPath + " exists. What to do?")
            print("[o]verwrite, [s]kip, [O]verwrite all, [S]kip all, e[x]it? ")
            while True:
                ans = input()
                if ans in ('o', 'O', 's', 'S', 'x'): break
                if ins == "s": continue
                if ans == "x": break

        if dryRun:
            logging.info('Save ' + newPath)
        else:
            im1.save(newPath, quality=80, optimize = True)
            os.replace(fPath, movePath)
