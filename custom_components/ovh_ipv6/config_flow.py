"""Config flow for OVH IPv6 DynHost integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    CONF_HOSTNAME,
    DYNHOST_UPDATE_URL,
    DYNDNS_SUCCESS_RESPONSES,
)
from .ip_address import async_get_current_ipv6

_LOGGER = logging.getLogger(__name__)


class OvhIpv6ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for OVH IPv6 DynHost."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_HOSTNAME])
            self._abort_if_unique_id_configured()

            try:
                ipv6_address = await async_get_current_ipv6(self.hass, _LOGGER)

                if not ipv6_address:
                    errors["base"] = "no_ipv6"
                    return self.async_show_form(
                        step_id="user",
                        data_schema=vol.Schema({
                            vol.Required(CONF_USERNAME): str,
                            vol.Required(CONF_PASSWORD): str,
                            vol.Required(CONF_HOSTNAME): str,
                        }),
                        errors=errors,
                    )

                # Test the credentials
                url = f"https://{DYNHOST_UPDATE_URL}"
                auth = aiohttp.BasicAuth(
                    user_input[CONF_USERNAME],
                    user_input[CONF_PASSWORD],
                )

                session = async_get_clientsession(self.hass)
                params = {
                    "system": "dyndns",
                    "hostname": user_input[CONF_HOSTNAME],
                    "myip": ipv6_address,
                }
                async with session.get(url, auth=auth, params=params) as response:
                    response_text = (await response.text()).strip()
                    response_status = response.status

                if response_status == 401 or response_text.startswith("badauth"):
                    errors["base"] = "invalid_auth"
                    _LOGGER.error(
                        "Authentication failed for %s",
                        user_input[CONF_HOSTNAME],
                    )
                elif response_status != 200:
                    errors["base"] = "cannot_connect"
                    _LOGGER.error(
                        "Connection failed for %s with status %s: %s",
                        user_input[CONF_HOSTNAME],
                        response_status,
                        response_text,
                    )
                elif response_text.startswith(DYNDNS_SUCCESS_RESPONSES):
                    return self.async_create_entry(
                        title=f"OVH DynHost ({user_input[CONF_HOSTNAME]})",
                        data=user_input,
                    )
                else:
                    errors["base"] = "cannot_connect"
                    _LOGGER.error(
                        "DynHost rejected %s update to %s: %s",
                        user_input[CONF_HOSTNAME],
                        ipv6_address,
                        response_text,
                    )

            except aiohttp.ClientError:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                    vol.Required(CONF_HOSTNAME): str,
                }
            ),
            errors=errors,
        )
