"""IPv6 address helpers for the OVH IPv6 integration."""
from __future__ import annotations

import logging
import socket
from ipaddress import IPv6Address

from homeassistant.components import network
from homeassistant.core import HomeAssistant

IPV6_ROUTE_TEST_TARGETS = (
    "2001:4860:4860::8888",
    "2606:4700:4700::1111",
    "2620:fe::fe",
)


def _parse_ipv6(address: str) -> IPv6Address | None:
    """Parse an IPv6 address from Home Assistant network data."""
    try:
        return IPv6Address(address.split("%", 1)[0])
    except ValueError:
        return None


def _is_public_ipv6(address: IPv6Address) -> bool:
    """Return true for IPv6 addresses that can be published in DNS."""
    return address.is_global and not address.is_multicast


def _get_route_source_ipv6(logger: logging.Logger) -> IPv6Address | None:
    """Return the IPv6 address the OS selects for outbound internet traffic."""
    for target in IPV6_ROUTE_TEST_TARGETS:
        try:
            with socket.socket(socket.AF_INET6, socket.SOCK_DGRAM) as test_socket:
                test_socket.setblocking(False)
                test_socket.connect((target, 1, 0, 0))
                address = _parse_ipv6(test_socket.getsockname()[0])
        except OSError as err:
            logger.debug("Could not detect IPv6 source address via %s: %s", target, err)
            continue

        if address and _is_public_ipv6(address):
            return address

    return None


async def async_get_current_ipv6(
    hass: HomeAssistant, logger: logging.Logger
) -> str | None:
    """Get the best public IPv6 address to publish for this Home Assistant host."""
    adapters = await network.async_get_adapters(hass)
    candidates: list[tuple[bool, str, IPv6Address]] = []

    for adapter in adapters:
        if not adapter["enabled"]:
            continue

        for ip_info in adapter["ipv6"]:
            address = _parse_ipv6(ip_info["address"])
            if not address or not _is_public_ipv6(address):
                continue

            candidates.append((adapter["default"], adapter["name"], address))

    if not candidates:
        logger.error("No public IPv6 address found on enabled Home Assistant adapters")
        return None

    route_source = _get_route_source_ipv6(logger)
    if route_source:
        for _is_default, adapter_name, address in candidates:
            if address == route_source:
                logger.debug(
                    "Using outbound IPv6 source address %s from adapter %s",
                    address,
                    adapter_name,
                )
                return str(address)

        logger.debug(
            "Outbound IPv6 source address %s was not found on enabled adapters",
            route_source,
        )

    candidates.sort(key=lambda item: (not item[0], item[1], int(item[2])))
    is_default, adapter_name, address = candidates[0]
    logger.debug(
        "Using public IPv6 address %s from %s adapter %s",
        address,
        "default" if is_default else "enabled",
        adapter_name,
    )
    return str(address)
