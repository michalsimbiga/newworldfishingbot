import asyncio
import logging
import signal
import sys
import time

import dlib
import numpy as np
import pyautogui
import win32api
import win32con
from PIL import ImageGrab
#
from win32gui import GetForegroundWindow, GetWindowRect

log = logging.getLogger(__name__)


def _cleanup_loop(loop):
    try:
        _cancel_tasks(loop)
        if sys.version_info >= (3, 6):
            loop.run_until_complete(loop.shutdown_asyncgens())
    finally:
        log.info('Closing the event loop.')
        loop.close()


def _cancel_tasks(loop):
    try:
        task_retriever = asyncio.Task.all_tasks
    except AttributeError:
        # future proofing for 3.9 I guess
        task_retriever = asyncio.all_tasks

    tasks = {t for t in task_retriever(loop=loop) if not t.done()}

    if not tasks:
        return

    log.info('Cleaning up after %d tasks.', len(tasks))
    for task in tasks:
        task.cancel()

    loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
    log.info('All tasks finished cancelling.')

    for task in tasks:
        if task.cancelled():
            continue
        if task.exception() is not None:
            loop.call_exception_handler({
                'message': 'Unhandled exception during Client.run shutdown.',
                'exception': task.exception(),
                'task': task
            })


NEW_WORLD = "New World"
rect = GetWindowRect(GetForegroundWindow())
img = ImageGrab.grab()
shouldRepairCount = 0
polePosition = (0, 0)
mouseResetPosition = (0, 0)

START = "START"
CATCHING = "CATCHING"
PULLING = "PULLING"
REPAIRING = "REPAIRING"
MAIN_PROGRESS = START

detector = dlib.simple_object_detector("pull_detector.svm")
reel_detector = dlib.simple_object_detector("reel_detector.svm")
pole_detector = dlib.simple_object_detector("pole_detector.svm")


class NewWorldFishingBot:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self._closed = False
        self._ready = asyncio.Event()
        self.setup()

    def screenToNpArray(self, screenshot=False, fullscreen=False):
        tempRect = (400, rect[1], rect[2] - 400, rect[3] / 2)
        if fullscreen:
            tempRect = (0, rect[1], rect[2], rect[3])

        img = ImageGrab.grab(tempRect).convert("L")
        if screenshot: img.save("images/" + time.time().__str__() + ".jpg")
        return np.array(img)

    def single_click(self):
        pyautogui.mouseDown(button='left')
        pyautogui.mouseUp(button='left')

    def move_mouse_right(self):
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 500, 0, 0, 0)

    def setup(self):
        """
            Prepares events and commands for our bot
        """

    def run(self):
        """
            Runs the instance of the bot
        """
        loop = self.loop

        try:
            loop.add_signal_handler(signal.SIGINT, lambda: loop.stop())
            loop.add_signal_handler(signal.SIGTERM, lambda: loop.stop())
        except NotImplementedError:
            pass

        async def runner():
            try:
                await self.start()
            finally:
                if not self.is_closed():
                    await self.close()

        def stop_loop_on_completion(f):
            loop.stop()

        future = asyncio.ensure_future(runner(), loop=loop)
        future.add_done_callback(stop_loop_on_completion)
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            log.info('Received signal to terminate bot and event loop.')
        finally:
            future.remove_done_callback(stop_loop_on_completion)
            log.info('Cleaning up tasks.')
            _cleanup_loop(loop)

        if not future.cancelled():
            try:
                return future.result()
            except KeyboardInterrupt:
                # I am unsure why this gets raised here but suppress it anyway
                return None

    def is_closed(self):
        """:class:`bool`: Indicates if the websocket connection is closed."""
        return self._closed

    async def start(self):
        log.info("Bot Started")
        await self.botLoop()

    async def close(self):
        log.info("Bot Closed")

    async def cast_rod(self):
        global rect
        global MAIN_PROGRESS
        time.sleep(7)
        print("Cast Fishing")

        rect = GetWindowRect(GetForegroundWindow())
        self.single_click()
        MAIN_PROGRESS = CATCHING

    async def wait_for_bait(self):
        global rect
        global MAIN_PROGRESS
        print("Waiting for bait")

        track_time = time.time()
        recast_time = 20
        isTracking = True

        while isTracking:
            img_np = self.screenToNpArray()
            dets = detector(img_np, 1)

            if len(dets) > 0:
                self.single_click()

                print("Got something !" + time.time().__str__())

                MAIN_PROGRESS = PULLING
                time.sleep(1)
                break

            if time.time() - track_time > recast_time:
                print("Recasting")
                self.move_mouse_right()
                MAIN_PROGRESS = START
                break

    async def reeling(self):
        global MAIN_PROGRESS
        global REELING_LOOP

        REELING_LOOP = True

        while REELING_LOOP:
            print("Reeling " + time.time().__str__())
            pyautogui.mouseDown(button='left')
            time.sleep(1)
            pyautogui.mouseUp(button='left')
            time.sleep(0.8)

            if self.reelingInProgress():
                print("Still Reeling")
            else:
                print("Break Reeling")
                break

    def reelingInProgress(self):
        global REELING_LOOP
        global MAIN_PROGRESS

        print("checkStillReeling " + time.time().__str__())
        img_np = self.screenToNpArray()
        dets = reel_detector(img_np, 1)

        if len(dets) > 0:
            print("Reeling detected")
            return True
        else:
            print("Stop Reeling")
            REELING_LOOP = False
            MAIN_PROGRESS = START
            return False

    async def repearing(self):
        global MAIN_PROGRESS
        global polePosition
        global mouseResetPosition

        print("Repairing process started")

        pyautogui.keyDown('tab')
        pyautogui.keyUp('tab')

        time.sleep(4)

        repairingLoop = True

        print("Looking for pole")

        while repairingLoop:
            if polePosition == (0, 0):
                print("Detecting rod")
                img_np = self.screenToNpArray(fullscreen=True)
                dets = pole_detector(img_np, 1)

                if len(dets) > 0:

                    print("Potential Poles found")

                    self.screenToNpArray(screenshot=True, fullscreen=True)

                    for i, d in enumerate(dets):
                        print("Pole detected detected moving to pole square")

                        b_x = int((d.left() + d.right()) / 2)
                        b_y = int((d.top() + d.bottom()) / 2)

                        mouseResetPosition = (d.left() + d.right(), (d.top() + d.bottom()))

                        polePosition = (b_x, b_y)

                        await self.repair()

                        repairingLoop = False

                else:

                    print("No Pole Found ")

                    pyautogui.keyDown('tab')
                    pyautogui.keyUp('tab')

                    self.move_mouse_right()

                    repairingLoop = False

            else:
                print("Rod cords present")
                await self.repair()

                repairingLoop = False

    async def repair(self):
        global MAIN_PROGRESS
        (poleX, poleY) = polePosition
        (resetX, resetY) = mouseResetPosition

        pyautogui.moveTo(poleX, poleY, 0.3)
        pyautogui.keyDown('r')
        pyautogui.mouseDown(button='right')
        pyautogui.mouseUp(button='right')
        pyautogui.keyUp('r')
        pyautogui.moveTo(resetX, resetY, 0.3)

        time.sleep(1)

        pyautogui.keyDown('e')
        pyautogui.keyUp('e')

        time.sleep(2)

        pyautogui.keyDown('tab')
        pyautogui.keyUp('tab')

        time.sleep(2)

        pyautogui.keyDown('f3')
        pyautogui.keyUp('f3')

        MAIN_PROGRESS = START

    async def botLoop(self):
        global MAIN_PROGRESS
        global shouldRepairCount

        while not self.is_closed():
            print("Bot Loop Running")

            if shouldRepairCount == 10:
                MAIN_PROGRESS = REPAIRING
                shouldRepairCount = 0

            if MAIN_PROGRESS == START:
                await self.cast_rod()
            elif MAIN_PROGRESS == CATCHING:
                await self.wait_for_bait()
            elif MAIN_PROGRESS == PULLING:
                shouldRepairCount += 1
                await self.reeling()
            elif MAIN_PROGRESS == REPAIRING:
                time.sleep(7)
                await self.repearing()
            else:
                time.sleep(4)
