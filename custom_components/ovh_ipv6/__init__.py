"""Integrate with OVH ipv6 DNS service."""
import json
import ovh
import asyncio
from datetime import timedelta
import logging

import aiohttp
import voluptuous as vol

from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.typing import ConfigType

_LOGGER = logging.getLogger(__name__)  # Remove the parentheses

# Define all custom constants
DOMAIN = "ovh_ipv6"
CONF_OVH_AK = "ovh_ak"
CONF_OVH_AS = "ovh_as"
CONF_OVH_CK = "ovh_ck"
CONF_DNSZONE = "dnszone"
CONF_DNSID = "dnsid"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_INTERVAL = timedelta(minutes=15)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_OVH_AK): cv.string,
                vol.Required(CONF_OVH_AS): cv.string, 
                vol.Required(CONF_OVH_CK): cv.string,
                vol.Required(CONF_DNSZONE): cv.string,
                vol.Required(CONF_DNSID): cv.string,
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_INTERVAL): vol.All(
                    cv.time_period, cv.positive_timedelta
                ),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Initialize the OVH component."""
    conf = config[DOMAIN]
    application_key = conf.get(CONF_OVH_AK).strip()
    application_secret = conf.get(CONF_OVH_AS).strip()
    consumer_key = conf.get(CONF_OVH_CK).strip()
    dnszone = conf.get(CONF_DNSZONE).strip()
    dns_id = conf.get(CONF_DNSID).strip()
    interval = conf.get(CONF_SCAN_INTERVAL)

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

    async def update_dns_record(now=None):
        """Update the OVH DNS record."""
        try:
            # Get current IPv6
            current_ipv6 = await get_current_ipv6()
            if not current_ipv6:
                return False

            # Get current DNS record
            try:
                dns_record = ovh_client.get(f"/domain/zone/{dnszone}/record/{dns_id}")
                current_target = dns_record.get('target')
                
                # Skip update if IPv6 hasn't changed
                if current_target == current_ipv6:
                    _LOGGER.debug("IPv6 address unchanged, skipping update")
                    return True
                    
            except ovh.exceptions.APIError as e:
                _LOGGER.error("Failed to get current DNS record: %s", str(e))
                return False

            # Update DNS record if IPv6 has changed
            result = ovh_client.put(f"/domain/zone/{dnszone}/record/{dns_id}",
                ttl=0,
                target=current_ipv6
            )
            
            # Refresh the DNS zone
            ovh_client.post(f"/domain/zone/{dnszone}/refresh")
            
            _LOGGER.info("Successfully updated DNS record from %s to %s", 
                        current_target, current_ipv6)
            return True

        except ovh.exceptions.APIError as e:
            _LOGGER.error("OVH API error: %s", str(e))
            return False

        except Exception as e:
            _LOGGER.error("Unexpected error updating DNS record: %s", str(e))
            return False

    # Schedule periodic updates
    async_track_time_interval(hass, update_dns_record, interval)

    # Do first update and ensure we return a boolean
    try:
        result = await update_dns_record()
        return bool(result)
    except Exception as err:
        _LOGGER.error("Error during initial DNS update: %s", str(err))
        return False