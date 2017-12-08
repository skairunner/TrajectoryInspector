from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import selenium
import getpass
import time
import json
import subprocess
import os
import wget


BASEADDR = "http://uk.whattheflight.com/airlines/logos/letter/"
OUTADDR = "client/logos/"

#driver = webdriver.Firefox()
# phantomjs_path = "C:\coding\JeevesCoursePlanner\scraper\phantomjs.exe"
#driver = webdriver.PhantomJS(executable_path=phantomjs_path, service_log_path=os.path.devnull)
#driver.set_window_size(1400, 1000)
driver = webdriver.Chrome()
timeout = 30

imageurls = []
for char in "abcdefghijklmnopqrstuvwxyz":
    charurls = []
    driver.get(BASEADDR + char)

    thumbs = driver.find_elements_by_css_selector(".thumbnail")
    for thumb in thumbs:
        url = thumb.find_element_by_css_selector("img").get_attribute("src")
        charurls.append(url)
        imageurls.append(url)
    with open("client/logos/urls/%s.json" % (char), "w") as f:
        json.dump(charurls, f)

for i, url in enumerate(imageurls):
    print("\n{} / {}".format(i + 1, len(imageurls)))
    r = wget.download(url, out=OUTADDR + url.split("/")[-1])

print("Done.")
driver.close()