import time
import threading
import socket
import numpy as np
import cv2
from kivy.clock import Clock
from fractions import Fraction
from os import path, listdir
from detect import detect_markers_integrated
from find_objects import img_check
from four_points_edited import four_point_transform, contour_transform
from color_balance_marker import colorBalance

try:
    from picamera import PiCamera
    from picamera.array import PiRGBArray
except:
    pass

class Cameraman():
    def __init__(self):
        #super(Cameraman, self).__init__(**kwargs)
        
        self.busy = True

        self.camera = PiCamera(resolution=(3280, 2464), framerate=10)
        self.camera.iso = 100
        time.sleep(2)
        self.camera.exposure_mode = 'off'
        self.camera.awb_mode = 'off'

        self.rawCapture = PiRGBArray(self.camera)

        self.set_params()
        #self.camera.iso = 100
        self.camera.shutter_speed = 13000
        self.camera.brightness = 50
        self.camera.awb_gains = (1.92, 0.93)
        self.camera.contrast = 0

        self.busy=False
        self.ba_state = "waiting image"
        print('Camera ready')

        self.values=[[0,0,0],[0,0,0]]

    def set_params(self, shutter=None, bright=None, awb_g=None, contrast=None):
        status="OK"
        try:
            if shutter!=None:
                status="sh_error"
                assert type(shutter)==int
                assert 5000<=shutter<=100000
                self.camera.shutter_speed = shutter
                status="OK"
            if bright!=None:
                status="bg_error"
                assert type(bright)==int
                assert 0<=bright<=100
                self.camera.brightness = bright
                status="OK"
            if awb_g!=None:
                status="wg_error"
                assert type(awb_g)==tuple and len(awb_g)==2
                assert type(awb_g[0])==float and type(awb_g[1])==float
                assert 0<=awb_g[0]<=8 and 0<=awb_g[0]<=8
                self.camera.awb_gains = awb_g
                status="OK"
            if contrast!=None:
                status="ct_error"
                assert type(contrast) == int
                assert 0<=contrast<=100
                self.camera.contrast = contrast
                status="OK"
                return [self.camera.shutter_speed,self.camera.brightness,self.camera.awb_gains,self.camera.contrast]
        except:
            return status
        #self.camera.iso = 100
        #self.camera.shutter_speed = 13000
        #self.camera.brightness = 50
        #self.camera.awb_gains = (1.92, 0.93)
        #self.camera.contrast = 0

    def get_busy_state(self):
        return self.busy

    def get_ba_state(self):
        return self.ba_state

    def capture_preview(self, check_img=False):
        self.check_img=check_img
        self.busy=True
        if self.check_img:
            self.ba_state="checking"
        else:
            self.ba_state="BA deactivated"
        t1 = threading.Thread(target=self.capture_execute,)
        t1.start()

    def capture_execute(self):
        self.camera.capture(self.rawCapture, format="rgb", use_video_port=False)
        buf = self.rawCapture.array
        self.img = cv2.cvtColor(buf, cv2.COLOR_RGB2BGR)
        self.rawCapture.truncate(0)
        cv2.imwrite('/home/pi/temp.png', self.img)
        cv2.imwrite('/home/pi/temp_preview.png', cv2.resize(self.img.copy(), None, None, fx=(400 / self.img.shape[1]), fy=(400 / self.img.shape[1]), interpolation=cv2.INTER_LINEAR))
        self.busy=False
        if self.check_img:
            try:
                contours, bg_cnt = img_check(self.img)
                ba_state="no_square"
                self.img, persp_mtx = four_point_transform(self.img, bg_cnt[:, 0, :])
                contours = contour_transform(contours, persp_mtx)
                ba_state="no_marker"
                markers, contours = detect_markers_integrated(self.img, contours)
                assert len(markers) > 0
                ba_state="no_obj"
                assert len(contours) > 0
                self.ba_state="OK"
                return
            except:
                self.ba_state=ba_state
                return
        else:
            return

    def capture_calibration(self, check_img=True):
        self.check_img=check_img
        self.busy=True
        if self.check_img:
            self.ba_state="checking"
        else:
            self.ba_state="BA deactivated"
        t1 = threading.Thread(target=self.calibration_data,)
        t1.start()

    def calibration_data(self):
        
        self.camera.capture(self.rawCapture, format="rgb", use_video_port=False)
        buf = self.rawCapture.array
        self.img = cv2.cvtColor(buf, cv2.COLOR_RGB2BGR)
        self.rawCapture.truncate(0)
        #cv2.imwrite('/home/pi/temp.png', self.img)
        cv2.imwrite('/home/pi/temp_preview.png', cv2.resize(self.img.copy(), None, None, fx=(400 / self.img.shape[1]), fy=(400 / self.img.shape[1]), interpolation=cv2.INTER_LINEAR))
        self.busy=False
        if self.check_img:
            try:
                contours, bg_cnt = img_check(self.img)
                ba_state="no_square"
                self.img, persp_mtx = four_point_transform(self.img, bg_cnt[:, 0, :])
                contours = contour_transform(contours, persp_mtx)
                ba_state="no_marker"
                markers, contours = detect_markers_integrated(self.img, contours)
                assert len(markers) > 0
                self.values = colorBalance(self.img, markers[0].coordinates())
                self.ba_state="values ready"
                return
            except:
                self.ba_state=ba_state
                return
        else:
            return

    def calibration_values(self):
        return self.values

    def clear_camera(self):
        self.camera.close()
        return

if __name__ == '__main__':
    Cameraman()
