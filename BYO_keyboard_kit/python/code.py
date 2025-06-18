import time
import board
import digitalio
import adafruit_matrixkeypad
import busio
import adafruit_dotstar as dotstar

# Initial delay for stable startup
time.sleep(1)

# Hardware initialization
cols = [digitalio.DigitalInOut(x) for x in (board.D11, board.D12, board.D13)]
rows = [digitalio.DigitalInOut(x) for x in (board.D9, board.D10)]
keys = ((0, 1, 2), (3, 4, 5))

keypad = adafruit_matrixkeypad.Matrix_Keypad(rows, cols, keys)
uart = busio.UART(board.D1, board.D0, baudrate=9600)
dots = dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=0.1)

# Color definitions - optimized values
COLORS = [
    (100, 0, 0),    # red - display 0
    (255, 165, 0),  # orange - display 1  
    (0, 255, 0),    # green - display 2
    (128, 0, 128),  # purple - display 3
]

# UART command templates
UART_COMMANDS = {
    0: bytearray([0xAA, 0xBB, 0x03, 0x01, 0x01, 0xEE]),  # Set display 0
    1: bytearray([0xAA, 0xBB, 0x03, 0x01, 0x02, 0xEE]),  # Set display 1
    2: bytearray([0xAA, 0xBB, 0x03, 0x01, 0x03, 0xEE]),  # Set display 2
    3: bytearray([0xAA, 0xBB, 0x03, 0x03, 0x01, 0xEE]),  # Cycle primary
    4: bytearray([0xAA, 0xBB, 0x03, 0x04, 0x01, 0xEE]),  # Cycle secondary
    5: bytearray([0xAA, 0xBB, 0x03, 0x05, 0x01, 0xEE]),  # Swap displays
}

# State variables
primary_display = 0
secondary_display = 1

# Initialize LED color
dots[0] = COLORS[primary_display]

def send_uart_message(command_key):
    """Send UART message with error handling"""
    try:
        uart.write(UART_COMMANDS[command_key])
    except Exception as e:
        print(f"UART Error: {e}")

def update_led_color():
    """Update DotStar LED color based on primary display"""
    dots[0] = COLORS[primary_display]

# Main loop
last_key_time = 0
DEBOUNCE_TIME = 0.15

while True:
    pressed_keys = keypad.pressed_keys
    
    if pressed_keys and (time.monotonic() - last_key_time) > DEBOUNCE_TIME:
        key = pressed_keys[0]
        last_key_time = time.monotonic()
        
        if key <= 2:  # Keys 0, 1, 2: Set both displays to same value
            primary_display = key
            secondary_display = key
            update_led_color()
            send_uart_message(key)
            
        elif key == 3:  # Cycle primary display
            primary_display = (primary_display + 1) % 4
            send_uart_message(3)
            
        elif key == 4:  # Cycle secondary display
            secondary_display = (secondary_display + 1) % 4
            send_uart_message(4)
            
        elif key == 5:  # Swap displays
            primary_display, secondary_display = secondary_display, primary_display
            update_led_color()
            send_uart_message(5)