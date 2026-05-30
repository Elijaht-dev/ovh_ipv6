"""Integration with OVH DynHost service."""
from __future__ import annotations

import logging

import aiohttp

from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    CONF_HOSTNAME,
    DEFAULT_INTERVAL,
    DYNHOST_UPDATE_URL,
    DYNDNS_SUCCESS_RESPONSES,
)
from .ip_address import async_get_current_ipv6

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the OVH IPv6 component."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up OVH IPv6 from a config entry."""
    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]
    hostname = entry.data[CONF_HOSTNAME]

    async def update_dynhost(now=None) -> bool:
        """Update the DynHost record."""
        try:
            current_ipv6 = await async_get_current_ipv6(hass, _LOGGER)
            if not current_ipv6:
                return False

            session = async_get_clientsession(hass)
            url = f"https://{DYNHOST_UPDATE_URL}"
            auth = aiohttp.BasicAuth(username, password)
            params = {
                "system": "dyndns",
                "hostname": hostname,
                "myip": current_ipv6,
            }

            async with session.get(url, auth=auth, params=params) as response:
                response_text = (await response.text()).strip()
                response_status = response.status

            if response_status == 200 and response_text.startswith(
                DYNDNS_SUCCESS_RESPONSES
            ):
                _LOGGER.info(
                    "DynHost update for %s set IPv6 to %s: %s",
                    hostname,
                    current_ipv6,
                    response_text,
                )
                return True

            _LOGGER.error(
                "Failed to update DynHost for %s to %s. Status: %s, Response: %s",
                hostname,
                current_ipv6,
                response_status,
                response_text,
            )
            return False

        except Exception as e:
            _LOGGER.error("Unexpected error updating DynHost: %s", str(e))
            return False

    # Schedule periodic updates
    entry.async_on_unload(
        async_track_time_interval(hass, update_dynhost, DEFAULT_INTERVAL)
    )

    # Do first update
    await update_dynhost()
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if entry.entry_id in hass.data[DOMAIN]:
        hass.data[DOMAIN].pop(entry.entry_id)
    return True
