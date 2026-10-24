"""Config flow for Tesmart KVMs."""

from typing import Any, override

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_DEVICE
from homeassistant.core import callback
from homeassistant.helpers.selector import BooleanSelector, SerialPortSelector

from .const import CONF_READ_STATE, DOMAIN


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

    @staticmethod
    @callback
    @override
    def async_get_options_flow(config_entry):
        """Create the options flow for an existing Tesmart device."""
        return TesmartOptionsFlow(config_entry)


class TesmartOptionsFlow(OptionsFlow):
    """Configure optional serial feedback reading."""

    def __init__(self, config_entry):
        """Initialize the options flow."""
        self.config_entry = config_entry

    @override
    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Set whether incoming serial feedback should update the selector."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_READ_STATE,
                        default=self.config_entry.options.get(CONF_READ_STATE, False),
                    ): BooleanSelector()
                }
            ),
        )
