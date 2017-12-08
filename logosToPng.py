from PIL import Image
import os

SRC = "client/logos/original/"
OUT = "client/logos/"

for filename in os.listdir(SRC):
    im = Image.open(SRC + filename)
    filename = filename.lower().split(".")
    filename[-1] = ".png"
    filename = "".join(filename)
    im.save(OUT + filename)