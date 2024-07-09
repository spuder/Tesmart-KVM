# Write your code here :-)
import time
import board
import digitalio
import adafruit_matrixkeypad
import usb_hid
import busio
import adafruit_dotstar as dotstar
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

# Initial delay for stable startup
time.sleep(1)

# Initialization
cols = [digitalio.DigitalInOut(x) for x in (board.D11, board.D12, board.D13)]
rows = [digitalio.DigitalInOut(x) for x in (board.D9, board.D10)]
keys = ((0, 1, 2), (3, 4, 5))

keypad = adafruit_matrixkeypad.Matrix_Keypad(rows, cols, keys)
kbd = Keyboard(usb_hid.devices)

AVAILABLE_KEYS = [
    Keycode.ONE,
    Keycode.TWO,
    Keycode.THREE,
    Keycode.FOUR,
    Keycode.FIVE,
    Keycode.SIX,
    Keycode.SCROLL_LOCK,
]

uart = busio.UART(board.D1, board.D0, baudrate=9600)
dots = dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=0.1)
colors = {
    "red": (100, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "purple": (128, 0, 128),
    "orange": (255, 165, 0),
}
dots[0] = colors["blue"]

primary_display = 0
secondary_display = 1


def send_uart_message(message):
    try:
        uart.write(message)
    except Exception as e:
        print(f"UART Error: {e}")


def update_dotstar_color(display):
    color = colors["blue"]
    if display == 0:
        color = colors["red"]
    elif display == 1:
        color = colors["orange"]
    elif display == 2:
        color = colors["green"]
    elif display == 3:
        color = colors["purple"]
    dots[0] = color


# Main loop
while True:
    keys = keypad.pressed_keys
    if keys:
        key = keys[0]
        if key == 0:
            primary_display = 0
            secondary_display = 0
            update_dotstar_color(primary_display)
            send_uart_message(bytearray([0xAA, 0xBB, 0x03, 0x01, 0x01, 0xEE]))
        elif key == 1:
            primary_display = 1
            secondary_display = 1
            update_dotstar_color(primary_display)
            send_uart_message(bytearray([0xAA, 0xBB, 0x03, 0x01, 0x02, 0xEE]))
        elif key == 2:
            primary_display = 2
            secondary_display = 2
            update_dotstar_color(primary_display)
            send_uart_message(bytearray([0xAA, 0xBB, 0x03, 0x01, 0x03, 0xEE]))
        elif key == 3:
            primary_display = (primary_display + 1) % 4
            send_uart_message(bytearray([0xAA, 0xBB, 0x03, 0x03, 0x01, 0xEE]))
        elif key == 4:
            secondary_display = (secondary_display + 1) % 4
            send_uart_message(bytearray([0xAA, 0xBB, 0x03, 0x04, 0x01, 0xEE]))
        elif key == 5:
            primary_display, secondary_display = secondary_display, primary_display
            update_dotstar_color(primary_display)
            send_uart_message(bytearray([0xAA, 0xBB, 0x03, 0x05, 0x01, 0xEE]))
        time.sleep(0.15)
