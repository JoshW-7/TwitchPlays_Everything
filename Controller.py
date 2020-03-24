import time
import Vjoy

from Vjoy import joyState, SetButton, SetPOV, UpdateJoyState
from threading import Thread
from copy import copy
from TwitchBot import sendmessage
#from Display import Display

import pyautogui

INPUTS = {
    "left":         0, "c":             0,
    "right":        1, "z":             1,
    "up":           2, "tleft":         2,
    "down":         3, "tright":        3,
    "a":            4,
    "b":            5,
    "l":            6, "one":           6,
    "r":            7, "two":           7,
    "select":       8, "minus":         8,
    "start":        9, "plus":          9,
    "cleft":        10, "pleft":        10,
    "cright":       11, "pright":       11,
    "cup":          12, "pup":          12,
    "cdown":        13, "pdown":        13,
    "dleft":        14,
    "dright":       15,
    "dup":          16,
    "ddown":        17,
    "SAVESTATE1":   18, "tforward":     18,
    "SAVESTATE2":   19, "tback":        19,
    "SAVESTATE3":   20, "lclick":       20,
    "SAVESTATE4":   21, "cclick":       21,
    "SAVESTATE5":   22,
    "SAVESTATE6":   23,
    "LOADSTATE1":   24,
    "LOADSTATE2":   25,
    "LOADSTATE3":   26,
    "LOADSTATE4":   27,
    "LOADSTATE5":   28, "zl":           28,
    "LOADSTATE6":   29, "zr":           29,
    "x":            30, "shake":        30,
    "y":            31, "point":        31
}

def reset():
    pyautogui.press("f1")

"""
def savestate(num, user):
    global Controllers

    if user["level"] < 3 and num <= 3 and num > 0:
        return "Access denied"
    elif num > 0 and num <= 6:
        Controllers[1].execute_input({"name": "SAVESTATE" + str(num), "duration": 200})
        f = open("last_save.txt", "w")
        f.write(str(num))
        f.close()

        return "/me Saving state " + str(num)
    else: return "Invalid number."

def loadstate(num, user):
    global Controllers

    if num > 0 and num <= 6:
        Controllers[1].execute_input({"name": "LOADSTATE" + str(num), "duration": 200})
        f = open("last_load.txt", "w")
        f.write(str(num))
        f.close()

        return "/me Loading state " + str(num)
    else: return "Invalid number."
"""

class Controller:

    def __init__(self, id=0):

        self.id = id
        self.buttons ={
        "left":         False, "tleft":         False,
        "right":        False, "tright":        False,
        "up":           False,
        "down":         False,
        "a":            False,
        "b":            False,
        "l":            False, "one":           False,
        "r":            False, "two":           False,
        "select":       False, "minus":         False, "z": False,
        "start":        False, "plus":          False,
        "cleft":        False, "pleft":         False,
        "cright":       False, "pright":        False,
        "cup":          False, "pup":           False,
        "cdown":        False, "pdown":         False,
        "dleft":        False, "c":             False,
        "dright":       False, "z":             False,
        "dup":          False,
        "ddown":        False,
        "SAVESTATE1":   False, "tforward":      False,
        "SAVESTATE2":   False, "tback":         False,
        "SAVESTATE3":   False,
        "SAVESTATE4":   False,
        "SAVESTATE5":   False,
        "SAVESTATE6":   False,
        "LOADSTATE1":   False,
        "LOADSTATE2":   False,
        "LOADSTATE3":   False,
        "LOADSTATE4":   False,
        "LOADSTATE5":   False,
        "LOADSTATE6":   False,
        "x":            False, "shake":         False,
        "y":            False, "point":          False,
        "#":            False,
        ".":            False
        }

        self.paused = False
        self.thread_count = 0

    def execute_input_array(self, input_array, user):

        self.thread_count += 1

        # The list of buttons this particular instance cares about
        instance_buttons = []

        # For each string of simultaneous buttons
        for simultaneous_buttons in input_array:

            # Determine the delay time
            max_delay = 0
            for button in simultaneous_buttons:
                if button["duration"] > max_delay:
                    max_delay = button["duration"]

            # Press each button in a separate thread, as they are simultaneous
            for button in simultaneous_buttons:
                b = Thread(target=self.execute_input, args=[button])
                b.start()
                instance_buttons.append(button["name"])

            # Wait the maximum time
            delay_time = int(max_delay)/1000
            if delay_time > 0:
                time.sleep(delay_time)

        # Release any buttons this instance started holding
        for button in instance_buttons:
            if self.buttons[button]:
                if button == "l" or button == "left" or button == "right" or button == "up" or button == "down" or button == "pleft" or button == "pright" or button == "pup" or button == "pdown":
                    self.release_analog({"name": button})
                elif button != "." and button != "#":
                    self.release_digital({"name": button})

        self.thread_count -= 1

    def hold_digital_duration(self, button):
        global Vjoy
        global joyState

        score = 0
        if self.buttons["a"] or button["name"] == "a": score += 1
        if self.buttons["b"] or button["name"] == "b": score += 1
        if self.buttons["select"] or button["name"] == "select": score += 1
        if self.buttons["start"] or button["name"] == "start": score += 1
        if score >= 4:
            self.release_digital({"name": "a"})
            self.release_digital({"name": "b"})
            self.release_digital({"name": "select"})
            sendmessage("No resetting ;P")
        else:
            if button["name"].startswith("LOADSTATE") or button["name"].startswith("SAVESTATE"):
                SetButton(joyState[1], INPUTS[button["name"]], Vjoy.BUTTON_DOWN)
            elif button["name"] != "point":
                SetButton(joyState[self.id], INPUTS[button["name"]], Vjoy.BUTTON_DOWN)
            else:
                SetButton(joyState[self.id], INPUTS[button["name"]], Vjoy.BUTTON_UP)
            self.buttons[button["name"]] = True

            if button["name"].startswith("LOADSTATE") or button["name"].startswith("SAVESTATE"):
                UpdateJoyState(1, joyState[1])
                time.sleep(0.2)
            else:
                UpdateJoyState(self.id, joyState[self.id])
                time.sleep(button["duration"]/1000)

            if button["name"].startswith("LOADSTATE") or button["name"].startswith("SAVESTATE"):
                SetButton(joyState[1], INPUTS[button["name"]], Vjoy.BUTTON_UP)
            elif button["name"] != "point":
                SetButton(joyState[self.id], INPUTS[button["name"]], Vjoy.BUTTON_UP)
            else:
                SetButton(joyState[self.id], INPUTS[button["name"]], Vjoy.BUTTON_DOWN)

            if button["name"].startswith("LOADSTATE") or button["name"].startswith("SAVESTATE"):
                UpdateJoyState(1, joyState[1])
            else:
                UpdateJoyState(self.id, joyState[self.id])
            self.buttons[button["name"]] = False


    def hold_digital_indefinite(self, button):
        global Vjoy
        global joyState

        score = 0
        if self.buttons["a"] or button["name"] == "a": score += 1
        if self.buttons["b"] or button["name"] == "b": score += 1
        if self.buttons["select"] or button["name"] == "select": score += 1
        if self.buttons["start"] or button["name"] == "start": score += 1
        if score >= 4:
            self.release_digital({"name": "a"})
            self.release_digital({"name": "b"})
            self.release_digital({"name": "select"})
            sendmessage("No resetting ;P")
        else:
            if button["name"] != "point":
                SetButton(joyState[self.id], INPUTS[button["name"]], Vjoy.BUTTON_DOWN)
            else:
                SetButton(joyState[self.id], INPUTS[button["name"]], Vjoy.BUTTON_UP)
            UpdateJoyState(self.id, joyState[self.id])

            self.buttons[button["name"]] = True

    def release_digital(self, button):
        global Vjoy
        global joyState

        if button["name"] != "point":
            SetButton(joyState[self.id], INPUTS[button["name"]], Vjoy.BUTTON_UP)
        else:
            SetButton(joyState[self.id], INPUTS[button["name"]], Vjoy.BUTTON_DOWN)
        UpdateJoyState(self.id, joyState[self.id])
        self.buttons[button["name"]] = False

    def hold_analog_duration(self, button):
        global Vjoy
        global joyState

        if button["name"] == "l": joyState[self.id].XRotation = int(Vjoy.AXIS_MIN * button["percent"]/100)
        if button["name"] == "left": joyState[self.id].XAxis = int(Vjoy.AXIS_MIN * button["percent"]/100)
        if button["name"] == "right": joyState[self.id].XAxis = int(Vjoy.AXIS_MAX * button["percent"]/100)
        if button["name"] == "up": joyState[self.id].YAxis = int(Vjoy.AXIS_MAX * button["percent"]/100)
        if button["name"] == "down": joyState[self.id].YAxis = int(Vjoy.AXIS_MIN * button["percent"]/100)

        if button["name"] == "pleft": joyState[self.id].XRotation = int(Vjoy.AXIS_MIN * button["percent"]/100)
        if button["name"] == "pright": joyState[self.id].XRotation = int(Vjoy.AXIS_MAX * button["percent"]/100)
        if button["name"] == "pup": joyState[self.id].YRotation = int(Vjoy.AXIS_MIN * button["percent"]/100)
        if button["name"] == "pdown": joyState[self.id].YRotation = int(Vjoy.AXIS_MAX * button["percent"]/100)

        UpdateJoyState(self.id, joyState[self.id])
        self.buttons[button["name"]] = True

        time.sleep(button["duration"]/1000)

        if button["name"] == "l": joyState[self.id].XRotation = Vjoy.AXIS_NIL
        if button["name"] == "left": joyState[self.id].XAxis = Vjoy.AXIS_NIL
        if button["name"] == "right": joyState[self.id].XAxis = Vjoy.AXIS_NIL
        if button["name"] == "up": joyState[self.id].YAxis = Vjoy.AXIS_NIL
        if button["name"] == "down": joyState[self.id].YAxis = Vjoy.AXIS_NIL

        if button["name"] == "pleft": joyState[self.id].XRotation = Vjoy.AXIS_NIL
        if button["name"] == "pright": joyState[self.id].XRotation = Vjoy.AXIS_NIL
        if button["name"] == "pup": joyState[self.id].YRotation = Vjoy.AXIS_NIL
        if button["name"] == "pdown": joyState[self.id].YRotation = Vjoy.AXIS_NIL

        UpdateJoyState(self.id, joyState[self.id])
        self.buttons[button["name"]] = False

    def hold_analog_indefinite(self, button):
        global Vjoy
        global joyState

        if button["name"] == "l": joyState[self.id].XRotation = int(Vjoy.AXIS_MIN * button["percent"]/100)
        if button["name"] == "left": joyState[self.id].XAxis = int(Vjoy.AXIS_MIN * button["percent"]/100)
        if button["name"] == "right": joyState[self.id].XAxis = int(Vjoy.AXIS_MAX * button["percent"]/100)
        if button["name"] == "up": joyState[self.id].YAxis = int(Vjoy.AXIS_MAX * button["percent"]/100)
        if button["name"] == "down": joyState[self.id].YAxis = int(Vjoy.AXIS_MIN * button["percent"]/100)

        if button["name"] == "pleft": joyState[self.id].XRotation = int(Vjoy.AXIS_MIN * button["percent"]/100)
        if button["name"] == "pright": joyState[self.id].XRotation = int(Vjoy.AXIS_MAX * button["percent"]/100)
        if button["name"] == "pup": joyState[self.id].YRotation = int(Vjoy.AXIS_MIN * button["percent"]/100)
        if button["name"] == "pdown": joyState[self.id].YRotation = int(Vjoy.AXIS_MAX * button["percent"]/100)

        UpdateJoyState(self.id, joyState[self.id])
        self.buttons[button["name"]] = True

    def release_analog(self, button):
        global Vjoy
        global joyState

        if button["name"] == "l":
            joyState[self.id].XRotation = Vjoy.AXIS_NIL
            self.release_digital({"name": "l"})

        if button["name"] == "left": joyState[self.id].XAxis = Vjoy.AXIS_NIL
        if button["name"] == "right": joyState[self.id].XAxis = Vjoy.AXIS_NIL
        if button["name"] == "up": joyState[self.id].YAxis = Vjoy.AXIS_NIL
        if button["name"] == "down": joyState[self.id].YAxis = Vjoy.AXIS_NIL

        if button["name"] == "pleft": joyState[self.id].XRotation = Vjoy.AXIS_NIL
        if button["name"] == "pright": joyState[self.id].XRotation = Vjoy.AXIS_NIL
        if button["name"] == "pup": joyState[self.id].YRotation = Vjoy.AXIS_NIL
        if button["name"] == "pdown": joyState[self.id].YRotation = Vjoy.AXIS_NIL

        UpdateJoyState(self.id, joyState[self.id])
        self.buttons[button["name"]] = False

    def execute_input(self, button):

        if button["name"].startswith("LOADSTATE") or button["name"].startswith("SAVESTATE"):
            self.hold_digital_duration(button)
            return

        if (button["name"] == "l" and button["percent"] != 100) or (button["name"] in ["left", "right", "up", "down"]):
            if button["hold"]:
                self.hold_analog_indefinite(button)
            elif button["release"]:
                self.release_analog(button)
            else:
                self.hold_analog_duration(button)
        elif button["name"] != "." and button["name"] != "#":
            if button["hold"]:
                self.hold_digital_indefinite(button)
            elif button["release"]:
                self.release_digital(button)
            else:
                self.hold_digital_duration(button)
        else:
            if button["name"] == ".":
                self.buttons[button["name"]] = True
                time.sleep(0.2)
                self.buttons[button["name"]] = False
            elif button["name"] == "#":
                self.buttons[button["name"]] = True
                time.sleep(button["duration"]/1000)
                self.buttons[button["name"]] = False
            else:
                self.hold_digital_duration(button)

Controllers = [Controller(0), Controller(1)]
