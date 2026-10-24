"""Config flow for Tesmart KVMs."""

from typing import Any, override

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_DEVICE
from homeassistant.helpers.selector import SerialPortSelector

from .const import DOMAIN


class TesmartConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Tesmart KVMs."""

    VERSION = 1

    @override
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Configure the serial port used by the KVM."""
        if user_input is not None:
            self._async_abort_entries_match({CONF_DEVICE: user_input[CONF_DEVICE]})
            return self.async_create_entry(title="Tesmart KVM", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_DEVICE): SerialPortSelector()}),
        )
