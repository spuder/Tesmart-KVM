"""Config flow for Tesmart KVMs."""

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PORT

from .const import DOMAIN


class TesmartConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Tesmart KVMs."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Configure the serial port used by the KVM."""
        if user_input is not None:
            return self.async_create_entry(title="Tesmart KVM", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_PORT): str}),
        )
