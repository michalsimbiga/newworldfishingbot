# -*- coding: utf-8 -*-
#
import os
import sys
import time
import webbrowser

import dlib
import numpy as np
import pyautogui
from PIL import ImageGrab
from infi.systray import SysTrayIcon
#
from win10toast import ToastNotifier
from win32gui import GetWindowText, GetForegroundWindow, GetWindowRect

NEW_WORLD = "New World"
windowText = GetWindowText(GetForegroundWindow())
rect = GetWindowRect(GetForegroundWindow())
img = ImageGrab.grab()


def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def app_pause(systray):
    global is_stop
    is_stop = False if is_stop is True else True
    # print ("Is Pause: " + str(is_stop))
    if is_stop is True:
        systray.update(
            hover_text=app + " - On Pause")
    else:
        systray.update(
            hover_text=app)


def app_destroy(systray):
    # print("Exit app")
    sys.exit()


def app_about(systray):
    # print("github.com/YECHEZ/wow-fish-bot")
    webbrowser.open('https://github.com/YECHEZ/wow-fish-bot')


if __name__ == "__main__":
    print("AppStart")
    is_stop = True
    flag_exit = False

    is_block = False
    new_cast_time = 0
    recast_time = 20
    wait_mes = 0

    app = NEW_WORLD
    link = NEW_WORLD
    app_ico = resource_path('wow-fish-bot.ico')
    menu_options = (("Start/Stop", None, app_pause),
                    (link, None, app_about),)
    systray = SysTrayIcon(app_ico, app, menu_options, on_quit=app_destroy)
    systray.start()
    toaster = ToastNotifier()
    toaster.show_toast(app, link, icon_path=app_ico, duration=5)
    detector = dlib.simple_object_detector("pull_detector.svm")
    progress_detector = dlib.simple_object_detector("progress_detector.svm")

    in_progress = False
    rect = GetWindowRect(GetForegroundWindow())

    REELING_LOOP = True
    PROGRESS = "Progress"
    CATCHING = "CATCHING"
    PULLING = "PULLING"
    MAIN_PROGRESS = PROGRESS


    def start_fishing():
        global rect
        global in_progress
        global MAIN_PROGRESS
        time.sleep(7)
        print("Not in Progress ")
        rect = GetWindowRect(GetForegroundWindow())
        print("Cast Fishing")
        pyautogui.mouseDown(button='left')
        pyautogui.mouseUp(button='left')
        in_progress = True
        MAIN_PROGRESS = CATCHING


    def track():
        global rect
        global in_progress
        global MAIN_PROGRESS
        print("In progress")

        track_time = time.time()
        recast_time = 40

        isTracking = True

        while isTracking:
            print("Tracking " + time.time().__str__())

            img = ImageGrab.grab((0, rect[3] / 2, rect[2], rect[3])).convert("L")
            img_np = np.array(img)
            dets = detector(img_np, 1)

            if len(dets) > 0:
                print("Number of faces detected: {}".format(len(dets)))

                pyautogui.mouseDown(button='left')
                pyautogui.mouseUp(button='left')

                print("Got something !" + time.time().__str__())
                MAIN_PROGRESS = PULLING
                time.sleep(2)
                break

            if time.time() - track_time > recast_time:
                print("Recasting")
                MAIN_PROGRESS = PROGRESS
                break


    def reeling():
        global MAIN_PROGRESS
        global REELING_LOOP

        REELING_LOOP = True

        checkCount = 0

        while REELING_LOOP:
            print("Reeling " + time.time().__str__())
            pyautogui.mouseDown(button='left')
            time.sleep(0.8)
            pyautogui.mouseUp(button='left')
            time.sleep(0.6)
            if checkCount == 20:
                if not reelingInProgress():
                    print("Breaking Reeling")
                    break
                else:
                    print("Still Reeling")
                checkCount = 0
            else:
                checkCount += 1


    def reelingInProgress():
        global REELING_LOOP
        global MAIN_PROGRESS

        print("checkStillReeling " + time.time().__str__())
        img = ImageGrab.grab((0, rect[3] / 2, rect[2], rect[3])).convert("L")
        img.save("images/" + time.time().__str__() + ".jpg")
        img_np = np.array(img)
        dets = detector(img_np, 1)

        if len(dets) > 0:
            print("Number of faces detected: {}".format(len(dets)))
            return True
        else:
            REELING_LOOP = False
            MAIN_PROGRESS = PROGRESS
            return False


    while flag_exit is False:
        print("MainLoop" + time.time().__str__())

        if MAIN_PROGRESS == PROGRESS:
            start_fishing()
        elif MAIN_PROGRESS == CATCHING:
            track()
        elif MAIN_PROGRESS == PULLING:
            reeling()
        else:
            windowText = GetWindowText(GetForegroundWindow())
            time.sleep(4)
