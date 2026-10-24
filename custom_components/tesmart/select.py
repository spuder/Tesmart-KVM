"""Input selection for Tesmart KVMs."""

import serial

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import BAUDRATE, COMMAND_END, DOMAIN, INPUTS, INPUT_COMMAND


def _send_input(port: str, input_number: int) -> None:
    """Send a source-selection command to the KVM."""
    with serial.Serial(port=port, baudrate=BAUDRATE, timeout=1) as connection:
        connection.write(INPUT_COMMAND + bytes((input_number, COMMAND_END)))


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Tesmart input selector."""
    async_add_entities([TesmartInputSelect(hass, entry)])


class TesmartInputSelect(SelectEntity):
    """Select the active input on the Tesmart KVM."""

    _attr_has_entity_name = True
    _attr_name = "Input"
    _attr_options = list(INPUTS)

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the selector."""
        self._hass = hass
        self._port = entry.data[CONF_PORT]
        self._attr_unique_id = entry.entry_id
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Tesmart KVM",
            "manufacturer": "Tesmart",
        }

    async def async_select_option(self, option: str) -> None:
        """Switch the KVM to the selected input."""
        await self._hass.async_add_executor_job(
            _send_input, self._port, INPUTS[option]
        )
        self._attr_current_option = option
        self.async_write_ha_state()
