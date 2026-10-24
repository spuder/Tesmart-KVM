"""Input selection for Tesmart KVMs."""

from serialx import Parity, StopBits, open_serial_connection

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import BAUDRATE, COMMAND_END, DOMAIN, INPUTS, INPUT_COMMAND


async def _send_input(device: str, input_number: int) -> None:
    """Send a source-selection command to the KVM."""
    _, writer = await open_serial_connection(
        url=device,
        baudrate=BAUDRATE,
        bytesize=8,
        parity=Parity.NONE,
        stopbits=StopBits.ONE,
    )
    try:
        writer.write(INPUT_COMMAND + bytes((input_number, COMMAND_END)))
        await writer.drain()
    finally:
        writer.close()
        await writer.wait_closed()


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Tesmart input selector."""
    async_add_entities([TesmartInputSelect(entry)])


class TesmartInputSelect(SelectEntity):
    """Select the active input on the Tesmart KVM."""

    _attr_has_entity_name = True
    _attr_name = "Input"
    _attr_options = list(INPUTS)

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the selector."""
        self._device = entry.data[CONF_DEVICE]
        self._attr_unique_id = entry.entry_id
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Tesmart KVM",
            "manufacturer": "Tesmart",
        }

    async def async_select_option(self, option: str) -> None:
        """Switch the KVM to the selected input."""
        await _send_input(self._device, INPUTS[option])
        self._attr_current_option = option
        self.async_write_ha_state()
