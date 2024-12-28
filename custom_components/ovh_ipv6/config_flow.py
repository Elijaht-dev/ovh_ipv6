"""Config flow for OVH IPv6 DNS integration."""
from __future__ import annotations

import logging
from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv
import ovh

from .const import (
    DOMAIN,
    CONF_OVH_AK,
    CONF_OVH_AS,
    CONF_OVH_CK,
    CONF_DNSZONE,
    CONF_DNSID,
)

_LOGGER = logging.getLogger(__name__)

class OvhIpv6ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for OVH IPv6 DNS."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                def create_client():
                    return ovh.Client(
                        endpoint='ovh-eu',
                        application_key=user_input[CONF_OVH_AK],
                        application_secret=user_input[CONF_OVH_AS],
                        consumer_key=user_input[CONF_OVH_CK],
                    )

                client = await self.hass.async_add_executor_job(create_client)
                
                # Test the connection
                await self.hass.async_add_executor_job(
                    client.get,
                    f"/domain/zone/{user_input[CONF_DNSZONE]}/record/{user_input[CONF_DNSID]}"
                )

                return self.async_create_entry(
                    title=f"OVH DNS ({user_input[CONF_DNSZONE]})",
                    data=user_input,
                )

            except ovh.exceptions.InvalidKey:
                errors["base"] = "invalid_auth"
            except ovh.exceptions.ResourceNotFoundError:
                errors["base"] = "invalid_dns"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_OVH_AK): str,
                    vol.Required(CONF_OVH_AS): str,
                    vol.Required(CONF_OVH_CK): str,
                    vol.Required(CONF_DNSZONE): str,
                    vol.Required(CONF_DNSID): str,
                }
            ),
            errors=errors,
        )
