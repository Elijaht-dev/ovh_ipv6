"""Config flow for OVH IPv6 DynHost integration."""
from __future__ import annotations

import logging
from typing import Any
import voluptuous as vol
import aiohttp
from ipaddress import IPv6Address

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from homeassistant.components import network

from .const import DOMAIN, CONF_HOSTNAME, DYNHOST_UPDATE_URL

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
            try:
                # Get IPv6 address from Home Assistant's network API
                network_info = await network.async_get_adapters(self.hass)
                ipv6_address = None
                
                for adapter in network_info:
                    if adapter["enabled"] and adapter["ipv6"]:
                        for ip_info in adapter["ipv6"]:
                            try:
                                addr = IPv6Address(ip_info["address"])
                                if not addr.is_link_local:
                                    ipv6_address = str(addr)
                                    break
                            except ValueError:
                                continue
                    if ipv6_address:
                        break

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
                base_url = DYNHOST_UPDATE_URL
                url = f"https://{user_input[CONF_USERNAME]}:{user_input[CONF_PASSWORD]}@{base_url}"
                
                async with aiohttp.ClientSession() as session:
                    params = {
                        "system": "dyndns",
                        "hostname": user_input[CONF_HOSTNAME],
                        "myip": ipv6_address
                    }
                    async with session.get(url, params=params) as response:
                        if response.status == 401:
                            errors["base"] = "invalid_auth"
                            _LOGGER.error("Authentication failed for %s", user_input[CONF_HOSTNAME])
                        elif response.status != 200:
                            response_text = await response.text()
                            errors["base"] = "cannot_connect"
                            _LOGGER.error(
                                "Connection failed for %s with status %s: %s",
                                user_input[CONF_HOSTNAME],
                                response.status,
                                response_text
                            )
                        else:
                            await self.async_set_unique_id(user_input[CONF_HOSTNAME])
                            return self.async_create_entry(
                                title=f"OVH DynHost ({user_input[CONF_HOSTNAME]})",
                                data=user_input,
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
