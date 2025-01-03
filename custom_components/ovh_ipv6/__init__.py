"""Integration with OVH DynHost service."""
from __future__ import annotations

import logging
import aiohttp
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval

from .const import (
    DOMAIN,
    CONF_HOSTNAME,
    DEFAULT_INTERVAL,
    DYNHOST_UPDATE_URL,
)

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

    async def get_current_ipv6():
        """Get current IPv6 address from ipify.org."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('https://api6.ipify.org') as response:
                    return await response.text()
        except Exception as e:
            _LOGGER.error("Error getting IPv6 address: %s", str(e))
            return None

    async def update_dynhost(now=None) -> bool:
        """Update the DynHost record."""
        try:
            current_ipv6 = await get_current_ipv6()
            if not current_ipv6:
                return False

            async with aiohttp.ClientSession() as session:
                auth = aiohttp.BasicAuth(username, password)
                params = {
                    "system": "dyndns",
                    "hostname": hostname,
                    "myip": current_ipv6
                }
                
                async with session.get(
                    DYNHOST_UPDATE_URL,
                    params=params,
                    auth=auth
                ) as response:
                    if response.status == 200:
                        response_text = await response.text()
                        _LOGGER.info("DynHost update successful: %s", response_text)
                        return True
                    else:
                        _LOGGER.error(
                            "Failed to update DynHost. Status: %s, Response: %s",
                            response.status,
                            await response.text()
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