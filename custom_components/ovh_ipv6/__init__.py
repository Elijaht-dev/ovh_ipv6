"""Integrate with OVH ipv6 DNS service."""
from __future__ import annotations

import ovh
import logging
import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval

from .const import (
    DOMAIN,
    CONF_OVH_AK,
    CONF_OVH_AS,
    CONF_OVH_CK,
    CONF_DNSZONE,
    CONF_DNSID,
    DEFAULT_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the OVH IPv6 component."""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up OVH IPv6 from a config entry."""
    application_key = entry.data[CONF_OVH_AK]
    application_secret = entry.data[CONF_OVH_AS]
    consumer_key = entry.data[CONF_OVH_CK]
    dnszone = entry.data[CONF_DNSZONE]
    dns_id = entry.data[CONF_DNSID]

    def create_ovh_client():
        """Create OVH client in executor."""
        return ovh.Client(
            endpoint='ovh-eu',
            application_key=application_key,
            application_secret=application_secret,
            consumer_key=consumer_key
        )

    try:
        ovh_client = await hass.async_add_executor_job(create_ovh_client)
    except Exception as err:
        _LOGGER.error("Error creating OVH client: %s", str(err))
        return False

    async def get_current_ipv6():
        """Get current IPv6 address from ipify.org."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('https://api6.ipify.org') as response:
                    return await response.text()
        except Exception as e:
            _LOGGER.error("Error getting IPv6 address: %s", str(e))
            return None

    async def update_dns_record(now=None) -> bool:
        """Update the OVH DNS record."""
        try:
            current_ipv6 = await get_current_ipv6()
            if not current_ipv6:
                return False

            try:
                def get_record():
                    return ovh_client.get(f"/domain/zone/{dnszone}/dynHost/record/{dns_id}")

                def update_record(target):
                    ovh_client.put(
                        f"/domain/zone/{dnszone}/dynHost/record/{dns_id}",
                        ttl=0,
                        ip=target
                    )

                dns_record = await hass.async_add_executor_job(get_record)
                current_target = dns_record.get('ip')
                
                if current_target == current_ipv6:
                    _LOGGER.debug("IPv6 address unchanged, skipping update")
                    return True
                    
                await hass.async_add_executor_job(
                    update_record,
                    current_ipv6
                )
                
                _LOGGER.info("Successfully updated DNS record from %s to %s", 
                            current_target, current_ipv6)
                return True

            except ovh.exceptions.APIError as e:
                _LOGGER.error("Failed to get current DNS record: %s", str(e))
                return False

        except Exception as e:
            _LOGGER.error("Unexpected error updating DNS record: %s", str(e))
            return False

    # Store client in hass data
    hass.data[DOMAIN][entry.entry_id] = ovh_client

    # Schedule periodic updates
    entry.async_on_unload(
        async_track_time_interval(hass, update_dns_record, DEFAULT_INTERVAL)
    )

    # Do first update
    await update_dns_record()
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if entry.entry_id in hass.data[DOMAIN]:
        hass.data[DOMAIN].pop(entry.entry_id)
    return True