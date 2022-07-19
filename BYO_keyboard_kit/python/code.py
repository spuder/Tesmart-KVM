# For a full list of keycodes:
# https://circuitpython.readthedocs.io/projects/hid/en/latest/_modules/adafruit_hid/keycode.html

import time
import board
import digitalio
import adafruit_matrixkeypad
import usb_hid
import busio
from board import *

from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS

time.sleep(1)

cols = [digitalio.DigitalInOut(x) for x in (board.D11, board.D12, board.D13)]
rows = [digitalio.DigitalInOut(x) for x in (board.D9, board.D10)]
keys = (
    (0, 1, 2),
    (3, 4, 5),
)


keypad = adafruit_matrixkeypad.Matrix_Keypad(rows, cols, keys)

kbd = Keyboard(usb_hid.devices)

AVAILABLE_KEYS = [
    Keycode.ONE,
    Keycode.TWO,
    Keycode.THREE,
    Keycode.FOUR,
    Keycode.FIVE,
    Keycode.SIX,
    Keycode.SCROLL_LOCK
]

uart = busio.UART(board.D1, board.D0, baudrate=9600)
#uart = busio.UART(board.TX, board.RX, budrate=9600)

# https://docs.circuitpython.org/projects/hid/en/latest/api.html#adafruit-hid-keycode-keycode
while True:
    keys = keypad.pressed_keys
    if keys:
        print(keys)
        if 0 in keys:
            # Switch to PC 1
            text = bytearray([0xAA, 0xBB, 0x03, 0x01, 0x01, 0xEE])
            uart.write(text)
        if 1 in keys:
            # Switch to PC 2
            text = bytearray([0xAA, 0xBB, 0x03, 0x01, 0x02, 0xEE])
            uart.write(text)
        if 2 in keys:
            # Switch to PC 3
            text = bytearray([0xAA, 0xBB, 0x03, 0x01, 0x03, 0xEE])
            uart.write(text)
        if 3 in keys:
            # Output A control next input
            text = bytearray([0xAA, 0xBB, 0x03, 0x03, 0x01, 0xEE])
            uart.write(text)
        if 4 in keys:
            # Output B control next input
            text = bytearray([0xAA, 0xBB, 0x03, 0x04, 0x01, 0xEE])
            uart.write(text)
        if 5 in keys:
            # Change active selected computer in display mode 2
            text = bytearray([0xAA, 0xBB, 0x03, 0x05, 0x01, 0xEE])
            uart.write(text)
            
    time.sleep(0.2)
