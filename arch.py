#!/usr/bin/env python3

import os
from PIL import Image
import logging
import time

import config

SEC_PER_DAY = 60 * 60 * 24

logging.basicConfig(level=logging.INFO)
dryRun = False
delete = True

factor = 0.4


# Lookup config.ini, in same directory with this script.
config.init(os.path.join(os.path.split(os.path.realpath(__file__))[0], 'config.ini'))

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
archiveUntil = time.time() - 5 * SEC_PER_DAY

print("Archiver tool  - configuration:\n  Dry run: %r\n  Delete immediately: %r" \
      "\n  Crop factor: %f\n  Archive until: %s " 
      % (dryRun, delete, factor, time.strftime("%Y %m %d", time.localtime( archiveUntil))))
print("\nHit Ctrl + C to exit")
for x in range(5, 0, -1):
    print(x, end=' .. ', flush=True)
    time.sleep(1)

n_arch = 0
n_skipped = 0

for filename in sorted(os.listdir(directory)):
    fPath = os.path.join(directory, filename)
    if not os.path.isfile(fPath) or not fPath.endswith(('.jpg', '.jpeg', '.png')):
        continue
    if os.stat(fPath).st_mtime >= archiveUntil:
        logging.debug("Skip " + fPath)
        n_skipped += 1
        continue

    filedate = filename.split("-")[1]
    yyyy = filedate[0:4]
    mm = filedate[4:6]
    newPathParent = os.path.join(directory, 'arch', yyyy, mm)
    os.makedirs(newPathParent, exist_ok=True)
    newPath = os.path.join(newPathParent, filename)
    if delete:
        logging.debug("Delete file=" + fPath
                      + " new=" + newPath)
    else:
        movePath = os.path.join(directory, 'archived', filename)
        logging.debug("file=" + fPath
                      + " new=" + newPath
                      + " move=" + movePath)

    try:
        im1 = Image.open(fPath)
    except OSError:
        print("Cannot open" , fPath)
        if delete:
            print("Delete", fPath)
            if not dryRun:
                os.remove(fPath)
        continue

    newsize = (int(im1.width * factor), int(im1.height * factor))
    try:
        im1 = im1.resize(newsize, resample = Image.LANCZOS)
    except OSError:
        print("Cannot resize" , fPath)
        if delete:
            print("Delete", fPath)
            if not dryRun:
                os.remove(fPath)
        continue

    if os.path.exists(newPath) and ans != "O":
        if ans == "S": continue
        print(newPath + " exists. What to do?")
        print("[o]verwrite, [s]kip, [O]verwrite all, [S]kip all, e[x]it? ")
        while True:
            ans = input()
            if ans in ('o', 'O', 's', 'S', 'x'): break
            if ans == "s": continue
            if ans == "x": break

    if dryRun:
        logging.info('Save ' + newPath)
        if delete:
            logging.info('  Delete ' + fPath)
    else:
        n_arch += 1
        im1.save(newPath, quality=80, optimize = True)
        oldsize = round(os.stat(fPath).st_size / 1024 * 10) / 10
        newsize = round(os.stat(newPath).st_size / 1024 * 10) / 10
        logging.info("%s, old size=%d, new size=%d, ratio=%d%%", newPath, oldsize, newsize,
                     int((newsize / oldsize) * 100))

        if delete:
            os.remove(fPath)
        else:
            os.replace(fPath, movePath)

print("%d files have been archived. (Skipped: %d)" % (n_arch, n_skipped))
