import time
import board
import busio
import digitalio
import adafruit_matrixkeypad
import adafruit_dotstar as dotstar

# Initial delay for stable startup
time.sleep(1)

# Hardware initialization
# The SAMD21 CircuitPython build has no built-in keypad module, so scan with adafruit_matrixkeypad
cols = [digitalio.DigitalInOut(x) for x in (board.D11, board.D12, board.D13)]
rows = [digitalio.DigitalInOut(x) for x in (board.D9, board.D10)]
keys = ((0, 1, 2), (3, 4, 5))
keypad = adafruit_matrixkeypad.Matrix_Keypad(rows, cols, keys)
uart = busio.UART(board.D1, board.D0, baudrate=9600, timeout=0)
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

# The KVM reports channel changes as ASCII lines, e.g. "Set ch is 2\r\r\n" (0-based).
# Switching both outputs (front-panel 1-4, IR 1-4, serial switch) sends the line 2-3
# times in quick succession. Output A/B (front panel or IR) sends it once and doesn't say
# which output changed; since those buttons step to the next PC, we infer the output.
CHANNEL_PREFIX = "Set ch is "
PAIR_WINDOW = 0.25  # seconds to wait for the rest of a "Set ch" burst (serial echoes can lag >100 ms)
OWN_COMMAND_WINDOW = 1.0  # seconds a single "Set ch" is attributed to our last command

DEBOUNCE_TIME = 0.15

# State variables
primary_display = 0
secondary_display = 1
rx_buffer = b""
pending_channels = []
pending_since = 0
last_command_key = None
last_command_time = 0

def send_uart_message(command_key):
    """Send UART message with error handling"""
    global last_command_key, last_command_time
    try:
        uart.write(UART_COMMANDS[command_key])
        last_command_key = command_key
        last_command_time = time.monotonic()
    except Exception as e:
        print(f"UART Error: {e}")

def update_led_color():
    """Update DotStar LED color based on primary display"""
    dots[0] = COLORS[primary_display]

def read_uart_lines():
    """Return complete lines received from the KVM"""
    global rx_buffer
    if uart.in_waiting:
        data = uart.read(uart.in_waiting)
        if data:
            rx_buffer += data
    lines = []
    end = rx_buffer.find(b"\n")
    while end >= 0:
        line = rx_buffer[:end]
        rx_buffer = rx_buffer[end + 1:]
        try:
            lines.append(line.decode().strip())
        except UnicodeError:
            pass
        end = rx_buffer.find(b"\n")
    return lines

def handle_kvm_line(line, now):
    """Queue channel reports; log everything else"""
    global pending_since
    print(f"KVM: {line}")
    if line.startswith(CHANNEL_PREFIX):
        try:
            channel = int(line[len(CHANNEL_PREFIX):])
        except ValueError:
            return
        if 0 <= channel < len(COLORS):
            if not pending_channels:
                pending_since = now
            pending_channels.append(channel)

def changed_output(channel, now):
    """Return "A" or "B": which output a single "Set ch" line most likely came from"""
    if now - last_command_time < OWN_COMMAND_WINDOW:
        if last_command_key == 3:
            return "A"
        if last_command_key == 4:
            return "B"
    a_next = (primary_display + 1) % len(COLORS)
    b_next = (secondary_display + 1) % len(COLORS)
    if channel == b_next and channel != a_next:
        return "B"
    # A's next PC, or ambiguous (both outputs on the same PC, or state drifted): guess A
    return "A"

def apply_pending_channels(now):
    """Once the pair window closes, sync display state with what the KVM reported"""
    global primary_display, secondary_display
    if not pending_channels or now - pending_since < PAIR_WINDOW:
        return
    channel = pending_channels[-1]
    if len(pending_channels) >= 2:
        # Both outputs switched to the same PC
        primary_display = channel
        secondary_display = channel
    elif changed_output(channel, now) == "B":
        secondary_display = channel
    else:
        primary_display = channel
    pending_channels.clear()
    update_led_color()
    print(f"STATE: A=PC{primary_display + 1} B=PC{secondary_display + 1}")

# Initialize LED color
update_led_color()

# Main loop
last_pressed_keys = []
last_key_time = 0

while True:
    now = time.monotonic()
    for line in read_uart_lines():
        if line:
            handle_kvm_line(line, now)
    apply_pending_channels(now)

    pressed_keys = keypad.pressed_keys

    # Only act on newly pressed keys (not keys held from previous loop)
    new_keys = [k for k in pressed_keys if k not in last_pressed_keys]
    last_pressed_keys = pressed_keys

    if not new_keys or (now - last_key_time) <= DEBOUNCE_TIME:
        continue

    key = new_keys[0]
    last_key_time = now

    if key <= 2:  # Keys 0, 1, 2: Set both displays to same value
        primary_display = key
        secondary_display = key
    elif key == 3:  # Cycle primary display
        primary_display = (primary_display + 1) % 4
    elif key == 4:  # Cycle secondary display
        secondary_display = (secondary_display + 1) % 4
    elif key == 5:  # Swap displays
        primary_display, secondary_display = secondary_display, primary_display

    update_led_color()
    send_uart_message(key)
