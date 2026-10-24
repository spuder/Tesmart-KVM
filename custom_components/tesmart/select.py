"""Input selection for Tesmart KVMs."""

import asyncio
from asyncio import StreamReader, StreamWriter
from contextlib import suppress
import logging
from typing import override

from serialx import Parity, SerialException, StopBits, open_serial_connection

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICE
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    BAUDRATE,
    COMMAND_END,
    CONF_READ_STATE,
    DOMAIN,
    INPUTS,
    INPUT_COMMAND,
)

INPUTS_BY_NUMBER = {number: name for name, number in INPUTS.items()}


async def _open_serial(device: str) -> tuple[StreamReader, StreamWriter]:
    """Open a serial connection with the KVM's settings."""
    return await open_serial_connection(
        url=device,
        baudrate=BAUDRATE,
        bytesize=8,
        parity=Parity.NONE,
        stopbits=StopBits.ONE,
    )


async def _send_input(device: str, input_number: int) -> None:
    """Send a source-selection command to the KVM."""
    _, writer = await _open_serial(device)
    try:
        writer.write(INPUT_COMMAND + bytes((input_number, COMMAND_END)))
        await writer.drain()
    finally:
        writer.close()
        await writer.wait_closed()


def _parse_status_line(line: bytes) -> str | None:
    """Translate a documented KVM channel notification into an input name."""
    try:
        message = line.decode("ascii").strip()
    except UnicodeDecodeError:
        return None

    prefix = "Set ch is "
    if not message.startswith(prefix):
        return None

    channel = message[len(prefix) :]
    if channel not in {"0", "1", "2", "3"}:
        return None
    return INPUTS_BY_NUMBER[int(channel)]


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
        self._read_state = entry.options.get(CONF_READ_STATE, False)
        self._writer = None
        self._writer_ready = asyncio.Event()
        self._reader_task: asyncio.Task | None = None
        self._attr_unique_id = entry.entry_id
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Tesmart KVM",
            "manufacturer": "Tesmart",
        }

    @override
    async def async_added_to_hass(self) -> None:
        """Start listening for KVM status messages when enabled."""
        if self._read_state:
            self._reader_task = self.hass.async_create_background_task(
                self._async_read_status(), "Tesmart serial status reader"
            )

    @override
    async def async_will_remove_from_hass(self) -> None:
        """Stop the status reader when the entity is removed."""
        if self._reader_task is not None:
            self._reader_task.cancel()
            with suppress(asyncio.CancelledError):
                await self._reader_task

    async def _async_read_status(self) -> None:
        """Maintain a serial connection and apply incoming channel messages."""
        while True:
            writer = None
            try:
                reader, writer = await _open_serial(self._device)
                self._writer = writer
                self._writer_ready.set()
                self._attr_available = True
                self.async_write_ha_state()

                while line := await reader.readline():
                    option = _parse_status_line(line)
                    if option is not None:
                        self._attr_current_option = option
                        self.async_write_ha_state()

                raise ConnectionError("Tesmart serial stream closed")
            except (ConnectionError, OSError, SerialException, TimeoutError):
                self._writer = None
                self._writer_ready.clear()
                self._attr_available = False
                self.async_write_ha_state()
            finally:
                if writer is not None:
                    writer.close()
                    with suppress(OSError, SerialException):
                        await writer.wait_closed()
            await asyncio.sleep(5)

    async def async_select_option(self, option: str) -> None:
        """Switch the KVM to the selected input."""
        if self._read_state:
            try:
                await asyncio.wait_for(self._writer_ready.wait(), timeout=10)
            except TimeoutError as err:
                raise HomeAssistantError("Tesmart serial proxy is unavailable") from err

            if self._writer is None:
                raise HomeAssistantError("Tesmart serial proxy is unavailable")

            self._writer.write(INPUT_COMMAND + bytes((INPUTS[option], COMMAND_END)))
            await self._writer.drain()
        else:
            await _send_input(self._device, INPUTS[option])
        self._attr_current_option = option
        self.async_write_ha_state()
