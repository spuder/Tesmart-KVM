"""Constants for the Tesmart integration."""

DOMAIN = "tesmart"
CONF_READ_STATE = "read_state"
BAUDRATE = 9600
INPUT_COMMAND = bytes((0xAA, 0xBB, 0x03, 0x01))
COMMAND_END = 0xEE
INPUTS = {
    "PC 1": 0x01,
    "PC 2": 0x02,
    "PC 3": 0x03,
    "PC 4": 0x04,
}
