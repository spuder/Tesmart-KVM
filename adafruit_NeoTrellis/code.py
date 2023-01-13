import time
import board
import busio
from adafruit_neotrellis.neotrellis import NeoTrellis

# To view available pins, enter REPL and type `dir(board)`
# https://i0.wp.com/peppe8o.com/wp-content/uploads/2021/05/raspberry-pi-pico-pinout.jpg?w=792&ssl=1
# SDA = GP2 = pin4
# SCL = GP3 = pin5
i2c_bus = busio.I2C(board.GP3, board.GP2)

trellis = NeoTrellis(i2c_bus)
trellis.brightness = 0.05

OFF = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)

left_buttons=[0, 4, 8, 12]
right_buttons=[3,7,11,15]

# def blink(event):
#     # turn the LED on when a rising edge is detected
#     if event.edge == NeoTrellis.EDGE_RISING:
#         trellis.pixels[event.number] = CYAN
#     # turn the LED off when a falling edge is detected
#     elif event.edge == NeoTrellis.EDGE_FALLING:
#         trellis.pixels[event.number] = OFF

# write file to raspberry pi pico internal flash memory
# https://learn.adafruit.com/micropython-hardware-pico/pico-filesystem

def tesmart()

def selection(event):
    if event.edge == NeoTrellis.EDGE_RISING:
        if event.number in left_buttons:
            for i in left_buttons:
                if i != event.number:
                    trellis.pixels[i] = BLUE
                else:
                    trellis.pixels[event.number] = GREEN
        if event.number in right_buttons:
            for i in right_buttons:
                if i != event.number:
                    trellis.pixels[i] = BLUE
                else:
                    trellis.pixels[event.number] = GREEN


for i in range(16):
    # activate rising edge events on all keys
    trellis.activate_key(i, NeoTrellis.EDGE_RISING)
    # activate falling edge events on all keys
    trellis.activate_key(i, NeoTrellis.EDGE_FALLING)
    # set all keys to trigger the blink callback
    trellis.callbacks[i] = selection

    # cycle the LEDs on startup
    trellis.pixels[i] = PURPLE
    time.sleep(0.025)

while True:
    trellis.sync()
    time.sleep(0.02)
