# replaces all ,, with ,; and all ,] with ] in order to try and fix most of the errors in the files

import re
import os

DIR = "ADBX_RAW/"
BASE = "2017-08-29-%sZ.json" # HHMM


for HH in range(24):
    print("HH: {:02d}".format(HH))
    for MM in range(60):
        print("  MM: {:02d}".format(MM))
        if HH < 10:
                timestamp = "0" + str(HH)
        else:
            timestamp = str(HH)
        if MM < 10:
            timestamp += "0" + str(MM)
        else:
            timestamp += str(MM)
        fpath = DIR + (BASE % timestamp)
        with open(fpath, "r", encoding="utf-8") as fin:
            with open(DIR + "temp", "w", encoding="utf-8") as fout:
                for line in fin:
                    line = line.replace(",,", ",")
                    line = line.replace(",]", "]")
                    line = line.replace("[,", "[")
                    fout.write(line)
        os.remove(fpath)
        os.rename(DIR + "temp", fpath)