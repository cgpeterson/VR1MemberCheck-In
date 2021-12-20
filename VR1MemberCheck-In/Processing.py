import os
import cv2

import imutils
from imutils.video import FPS
import pyzbar.pyzbar as pyzbar

from selenium import webdriver
import urllib.request as url
from bs4 import BeautifulSoup


class ComputerVision:
    def __init__(self):
        self.email = None
        self.password = None

    def detect(self, _image):
        decodedObjects = pyzbar.decode(_image)

        # add boop

        data = None
        
        for obj in decodedObjects:
            if obj is not None:
                data = obj.data
                break

        return data

    def CleanUp(self, frame):
        # values here are based on my current camera capture
        frame = imutils.resize(frame, width=400)
        grayImage = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        (thresh, bnw_image) = cv2.threshold(grayImage, 127, 255, cv2.THRESH_BINARY) 
        inversed_image = cv2.bitwise_not(bnw_image)

        return frame, inversed_image

    def login(self):
        loginDetails = r'Data/loginInfo.yml'
        if os.path.exists(loginDetails):
            conf = yaml.load(open(loginDetails))
            self.email = conf['user']['email']
            self.password = conf['user']['password']

    def memberCheck(self, weblink):
        isMember = False

        # Enter login info
        if self.email is not None and self.password is not None:
            driver = webdriver.Chrome()
            driver.find_element_by_id("email").send_keys(self.email)
            # <input class="form-control input-lg" type="text" placeholder="Your email" name="email">
            driver.find_element_by_id("password").send_keys(self.password)
            # <input class="form-control input-lg" type="password" placeholder="Password" name="password">
            driver.find_element_by_id("Log In").click()
            # <input type="submit" class="btn btn-success btn-lg" value="Log In" style="width: 100%;" data-disable="no">

            # Find member name
            # Find member number
            # Find if paid up
        isPaid = True

        return 'Cody Peterson', '1410589', '25', '16', isPaid

        

def callback(value):
    pass
